from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from ..config import Config, Model, Deck, Note
from ..backends.base import Backend


@dataclass
class PlanStep:
    kind: str
    description: str
    payload: dict


@dataclass
class Plan:
    steps: List[PlanStep] = field(default_factory=list)

    def add(self, kind: str, description: str, payload: dict) -> None:
        self.steps.append(PlanStep(kind, description, payload))

    def to_dict(self) -> dict:
        return {"steps": [s.__dict__ for s in self.steps]}

    def pretty(self) -> str:
        if not self.steps:
            return "No changes."
        lines = ["Planned changes:"]
        for s in self.steps:
            lines.append(f"- [{s.kind}] {s.description}")
        return "\n".join(lines)


class Planner:
    def __init__(self, backend: Backend):
        self.backend = backend

    def build_plan(self, cfg: Config) -> Plan:
        plan = Plan()

        # Decks
        existing_decks = set(self.backend.list_decks())
        desired_decks = {d.name for d in cfg.decks}
        for d in sorted(desired_decks - existing_decks):
            plan.add("deck.create", f"Create deck '{d}'", {"name": d})
        if cfg.prune.decks:
            for d in sorted(existing_decks - desired_decks):
                if d == "Default":
                    continue
                plan.add("deck.delete", f"Delete unmanaged deck '{d}'", {"name": d, "cardsToo": False})

        # Models
        existing_models = set(self.backend.list_models())
        desired_models = {m.name for m in cfg.models}
        for m in cfg.models:
            if m.name not in existing_models:
                plan.add(
                    "model.create",
                    f"Create model '{m.name}' with {len(m.fields)} fields and {len(m.templates)} templates",
                    {
                        "name": m.name,
                        "fields": m.fields,
                        "templates": [t.model_dump() for t in m.templates],
                        "css": m.css,
                    },
                )
            else:
                # Check fields (simple: ensure all exist; field removal not automated)
                current_fields = self.backend.model_field_names(m.name)
                if current_fields != m.fields:
                    plan.add(
                        "model.note",
                        f"Model '{m.name}' field order differs (current={current_fields} desired={m.fields}); manual intervention may be required",
                        {"name": m.name},
                    )
                plan.add(
                    "model.updateTemplates",
                    f"Update templates for model '{m.name}'",
                    {"name": m.name, "templates": [t.model_dump() for t in m.templates]},
                )
                plan.add(
                    "model.updateStyling",
                    f"Update CSS for model '{m.name}'",
                    {"name": m.name, "css": m.css},
                )
        if cfg.prune.models:
            for m in sorted(existing_models - desired_models):
                plan.add("model.delete", f"Delete unmanaged model '{m}'", {"name": m})

        # Notes
        for n in cfg.notes:
            # We require model's uniqueField to upsert
            model_cfg = next((m for m in cfg.models if m.name == n.model), None)
            if not model_cfg:
                plan.add(
                    "note.error",
                    f"Note targets unknown model '{n.model}'",
                    {"note": n.model_dump()},
                )
                continue
            uniq = model_cfg.uniqueField
            uniq_val = n.fields.get(uniq)
            if not uniq_val:
                plan.add(
                    "note.error",
                    f"Note missing unique field '{uniq}' for model '{n.model}'",
                    {"note": n.model_dump()},
                )
                continue
            # Quote the unique value if it contains spaces or special characters
            if ' ' in uniq_val or any(c in uniq_val for c in ['"', "'", ':']):
                quoted_val = f'"{uniq_val}"'
            else:
                quoted_val = uniq_val
            query = f"deck:{n.deck} note:{n.model} {uniq}:{quoted_val}"
            ids = self.backend.find_notes(query)
            if not ids:
                note_data = n.model_dump()
                media_desc = f" with {len(n.media)} media files" if n.media else ""
                plan.add(
                    "note.add",
                    f"Add note to deck '{n.deck}' model '{n.model}' keyed by {uniq}='{uniq_val}'{media_desc}",
                    {"note": note_data},
                )
            else:
                # If multiple, update first and warn
                note_id = ids[0]
                media_desc = f" with {len(n.media)} media files" if n.media else ""
                plan.add(
                    "note.update",
                    f"Update note id={note_id} in deck '{n.deck}' model '{n.model}'{media_desc}",
                    {"id": note_id, "fields": n.fields, "media": n.media},
                )
        # Prune notes not in config is optional and coarse; omitted for brevity or future work
        # It can be implemented by querying all notes in target decks/models and subtracting the upsert keys from config.

        return plan


def process_media_files(backend: Backend, media_paths: List[str], config_dir: Path) -> Dict[str, str]:
    """Process media files and return mapping of original paths to Anki filenames."""
    media_mapping = {}
    
    for media_path in media_paths:
        # Convert to Path and handle relative paths
        path = Path(media_path)
        if not path.is_absolute():
            path = config_dir / path
            
        if not path.exists():
            raise FileNotFoundError(f"Media file not found: {media_path} (resolved to {path})")
            
        # Read file content
        with path.open('rb') as f:
            file_data = f.read()
            
        # Generate a unique filename (preserve extension)
        filename = path.name
        
        # Check if file already exists in Anki
        existing_files = backend.get_media_files_names(filename)
        if filename not in existing_files:
            # Upload the file
            stored_name = backend.store_media_file(filename, file_data)
            media_mapping[media_path] = stored_name
        else:
            # File already exists, use existing name
            media_mapping[media_path] = filename
            
    return media_mapping


class Applier:
    def __init__(self, backend: Backend):
        self.backend = backend

    def apply(self, plan: Plan, config_dir: Path = None) -> None:
        # Get config directory for resolving relative media paths
        if config_dir is None:
            config_dir = Path.cwd()
            
        # Execute in order
        for s in plan.steps:
            if s.kind == "deck.create":
                self.backend.create_deck(s.payload["name"])
            elif s.kind == "deck.delete":
                self.backend.delete_decks([s.payload["name"]], cards_too=s.payload.get("cardsToo", False))
            elif s.kind == "model.create":
                p = s.payload
                self.backend.create_model(p["name"], p["fields"], p["templates"], p["css"])
            elif s.kind == "model.updateTemplates":
                p = s.payload
                self.backend.update_model_templates(p["name"], p["templates"]) 
            elif s.kind == "model.updateStyling":
                p = s.payload
                self.backend.update_model_styling(p["name"], p["css"]) 
            elif s.kind == "model.delete":
                self.backend.delete_model(s.payload["name"]) 
            elif s.kind == "note.add":
                n = s.payload["note"]
                # Process media files if present
                if "media" in n and n["media"]:
                    media_mapping = process_media_files(self.backend, n["media"], config_dir)
                    # TODO: We could optionally replace media references in field content
                    # For now, user needs to reference media files by filename in their fields
                self.backend.add_note(n["model"], n["deck"], n["fields"], n.get("tags", []))
            elif s.kind == "note.update":
                # Handle media for updates too if present in payload
                if "media" in s.payload and s.payload["media"]:
                    media_mapping = process_media_files(self.backend, s.payload["media"], config_dir)
                self.backend.update_note_fields(s.payload["id"], s.payload["fields"])
            elif s.kind.startswith("note.error") or s.kind == "model.note":
                # No-op; informational only
                continue
            else:
                raise RuntimeError(f"Unknown plan step kind: {s.kind}")