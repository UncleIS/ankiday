from __future__ import annotations

from typing import Any, Dict, List


class Backend:
    """Abstract backend interface."""

    # Decks
    def list_decks(self) -> List[str]:
        raise NotImplementedError

    def create_deck(self, name: str) -> None:
        raise NotImplementedError

    def delete_decks(self, names: List[str], cards_too: bool = False) -> None:
        raise NotImplementedError

    # Models
    def list_models(self) -> List[str]:
        raise NotImplementedError

    def model_field_names(self, model_name: str) -> List[str]:
        raise NotImplementedError

    def create_model(
        self,
        name: str,
        fields: List[str],
        templates: List[Dict[str, str]],
        css: str,
        is_cloze: bool = False,
    ) -> None:
        raise NotImplementedError

    def update_model_templates(self, name: str, templates: List[Dict[str, str]]) -> None:
        raise NotImplementedError

    def update_model_styling(self, name: str, css: str) -> None:
        raise NotImplementedError

    def delete_model(self, name: str) -> None:
        raise NotImplementedError

    # Notes
    def find_notes(self, query: str) -> List[int]:
        raise NotImplementedError

    def add_note(self, model: str, deck: str, fields: Dict[str, str], tags: List[str]) -> int:
        raise NotImplementedError

    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> None:
        raise NotImplementedError

    def delete_notes(self, ids: List[int]) -> None:
        raise NotImplementedError

    def notes_info(self, ids: List[int]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    # Media
    def store_media_file(self, filename: str, data: bytes) -> str:
        raise NotImplementedError

    def get_media_files_names(self, pattern: str = "*") -> List[str]:
        raise NotImplementedError

    def retrieve_media_file(self, filename: str) -> bytes:
        raise NotImplementedError

    def delete_media_file(self, filename: str) -> None:
        raise NotImplementedError
