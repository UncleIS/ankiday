from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import httpx

from .base import Backend


class AnkiConnectBackend(Backend):
    def __init__(self, base_url: str = "http://127.0.0.1:8765", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _invoke(self, action: str, params: Optional[dict] = None) -> Any:
        payload = {"action": action, "version": 5}
        if params is not None:
            payload["params"] = params
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.base_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if data.get("error") is not None:
                raise RuntimeError(f"AnkiConnect error: {data['error']}")
            return data.get("result")

    # Decks
    def list_decks(self) -> List[str]:
        return list(self._invoke("deckNames") or [])

    def create_deck(self, name: str) -> None:
        self._invoke("createDeck", {"deck": name})

    def delete_decks(self, names: List[str], cards_too: bool = False) -> None:
        self._invoke("deleteDecks", {"decks": names, "cardsToo": cards_too})

    # Models
    def list_models(self) -> List[str]:
        return list(self._invoke("modelNames") or [])

    def model_field_names(self, model_name: str) -> List[str]:
        return list(self._invoke("modelFieldNames", {"modelName": model_name}) or [])

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

        # Debug logging
        print(f"DEBUG: Creating model '{name}' with is_cloze={is_cloze}")
        print(f"DEBUG: Params being sent to AnkiConnect: {params}")

        try:
            result = self._invoke("createModel", params)
            print(f"DEBUG: Model creation result: {result}")
        except Exception as e:
            print(f"DEBUG: Model creation failed: {e}")
            raise

    def update_model_templates(self, name: str, templates: List[Dict[str, str]]) -> None:
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

    def update_model_styling(self, name: str, css: str) -> None:
        self._invoke(
            "updateModelStyling",
            {
                "model": {
                    "name": name,
                    "css": css
                }
            }
        )

    def delete_model(self, name: str) -> None:
        self._invoke("deleteModel", {"model": name})

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

        # Debug logging
        print(f"DEBUG: Adding note to model '{model}' in deck '{deck}'")
        print(f"DEBUG: Note data: {note_data}")

        try:
            nid = self._invoke("addNote", note_data)
            print(f"DEBUG: Note creation result: {nid}")
            return int(nid)
        except Exception as e:
            print(f"DEBUG: Note creation failed: {e}")
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
