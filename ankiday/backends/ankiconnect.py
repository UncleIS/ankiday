from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import httpx

from .base import Backend


class AnkiConnectBackend(Backend):
    def __init__(self, base_url: str = "http://127.0.0.1:8765", timeout: int = 30, verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verbose = verbose
    
    def _log_verbose(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[VERBOSE] {message}")

    def _invoke(self, action: str, params: Optional[dict] = None) -> Any:
        payload = {"action": action, "version": 5}
        if params is not None:
            payload["params"] = params
        
        self._log_verbose(f"Invoking AnkiConnect action: {action}")
        if self.verbose and params:
            self._log_verbose(f"Parameters: {params}")
        
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.base_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if data.get("error") is not None:
                raise RuntimeError(f"AnkiConnect error: {data['error']}")
            
            result = data.get("result")
            self._log_verbose(f"Action {action} completed successfully")
            return result

    # Decks
    def list_decks(self) -> List[str]:
        self._log_verbose("Listing all decks")
        result = list(self._invoke("deckNames") or [])
        self._log_verbose(f"Found {len(result)} decks")
        return result

    def create_deck(self, name: str) -> None:
        self._log_verbose(f"Creating deck '{name}'")
        self._invoke("createDeck", {"deck": name})
        self._log_verbose(f"Deck '{name}' created successfully")

    def delete_decks(self, names: List[str], cards_too: bool = False) -> None:
        self._log_verbose(f"Deleting {len(names)} deck(s): {names} (cards_too={cards_too})")
        self._invoke("deleteDecks", {"decks": names, "cardsToo": cards_too})
        self._log_verbose(f"Deck deletion completed")

    # Models
    def list_models(self) -> List[str]:
        self._log_verbose("Listing all models")
        result = list(self._invoke("modelNames") or [])
        self._log_verbose(f"Found {len(result)} models")
        return result

    def model_field_names(self, model_name: str) -> List[str]:
        self._log_verbose(f"Getting field names for model '{model_name}'")
        result = list(self._invoke("modelFieldNames", {"modelName": model_name}) or [])
        self._log_verbose(f"Model '{model_name}' has {len(result)} fields: {result}")
        return result

    def create_model(self, name: str, fields: List[str], templates: List[Dict[str, str]], css: str, is_cloze: bool = False) -> None:
        # anki-connect expects templates array of {Name, Front, Back}
        tps = [{"Name": t["name"], "Front": t["qfmt"], "Back": t["afmt"]} for t in templates]
        params = {
            "modelName": name,
            "inOrderFields": fields,
            "css": css,
            "cardTemplates": tps,
        }
        if is_cloze:
            params["isCloze"] = True

        self._log_verbose(f"Creating model '{name}' with {len(fields)} fields, {len(templates)} templates, is_cloze={is_cloze}")
        
        try:
            result = self._invoke("createModel", params)
            self._log_verbose(f"Model '{name}' created successfully")
        except Exception as e:
            self._log_verbose(f"Model creation failed: {e}")
            raise

    def update_model_templates(self, name: str, templates: List[Dict[str, str]]) -> None:
        self._log_verbose(f"Updating templates for model '{name}' ({len(templates)} templates)")
        # Convert our template format to AnkiConnect's expected format
        # Our format: [{"name": "Card 1", "qfmt": "...", "afmt": "..."}]
        # AnkiConnect format: {"Card 1": {"Front": "...", "Back": "..."}}
        ankiconnect_templates = {}
        for t in templates:
            ankiconnect_templates[t["name"]] = {
                "Front": t["qfmt"],
                "Back": t["afmt"]
            }

        self._invoke(
            "updateModelTemplates",
            {
                "model": {
                "name": name,
                "templates": ankiconnect_templates
                }
            },
        )
        self._log_verbose(f"Templates for model '{name}' updated successfully")

    def update_model_styling(self, name: str, css: str) -> None:
        self._log_verbose(f"Updating CSS styling for model '{name}'")
        self._invoke(
            "updateModelStyling",
            {
                "model": {
                    "name": name,
                    "css": css
                }
            }
        )
        self._log_verbose(f"CSS styling for model '{name}' updated successfully")

    def delete_model(self, name: str) -> None:
        self._log_verbose(f"Deleting model '{name}'")
        self._invoke("deleteModel", {"model": name})
        self._log_verbose(f"Model '{name}' deleted successfully")

    # Notes
    def find_notes(self, query: str) -> List[int]:
        return list(self._invoke("findNotes", {"query": query}) or [])

    def add_note(self, model: str, deck: str, fields: Dict[str, str], tags: List[str]) -> int:
        note_data = {
            "note": {
                "deckName": deck,
                "modelName": model,
                "fields": fields,
                "tags": tags,
                # options could be extended
            }
        }

        self._log_verbose(f"Adding note to model '{model}' in deck '{deck}' with {len(fields)} fields")
        
        try:
            nid = self._invoke("addNote", note_data)
            self._log_verbose(f"Note created successfully with ID: {nid}")
            return int(nid)
        except Exception as e:
            self._log_verbose(f"Note creation failed: {e}")
            raise

    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> None:
        self._invoke("updateNoteFields", {"note": {"id": note_id, "fields": fields}})

    def delete_notes(self, ids: List[int]) -> None:
        self._invoke("deleteNotes", {"notes": ids})

    def notes_info(self, ids: List[int]):
        return list(self._invoke("notesInfo", {"notes": ids}) or [])

    # Media
    def store_media_file(self, filename: str, data: bytes) -> str:
        """Store a media file in Anki's media collection."""
        encoded_data = base64.b64encode(data).decode('utf-8')
        result = self._invoke("storeMediaFile", {
            "filename": filename,
            "data": encoded_data
        })
        return str(result)

    def get_media_files_names(self, pattern: str = "*") -> List[str]:
        """Get list of media filenames matching pattern."""
        return list(self._invoke("getMediaFilesNames", {"pattern": pattern}) or [])

    def retrieve_media_file(self, filename: str) -> bytes:
        """Retrieve a media file's content."""
        encoded_data = self._invoke("retrieveMediaFile", {"filename": filename})
        return base64.b64decode(encoded_data)

    def delete_media_file(self, filename: str) -> None:
        """Delete a media file from Anki's collection."""
        self._invoke("deleteMediaFile", {"filename": filename})
