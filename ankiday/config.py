from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Dict

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator


class Server(BaseModel):
    url: str = Field(default="http://127.0.0.1:8765")
    timeoutSeconds: int = Field(default=30, ge=1, le=300)


class Template(BaseModel):
    name: str
    qfmt: str
    afmt: str


class Model(BaseModel):
    name: str
    fields: List[str]
    templates: List[Template]
    css: str = Field(default="")
    uniqueField: str

    @field_validator("uniqueField")
    @classmethod
    def unique_in_fields(cls, v: str, info):
        fields = info.data.get("fields", [])
        if v not in fields:
            raise ValueError(f"uniqueField '{v}' must be one of fields: {fields}")
        return v


class Deck(BaseModel):
    name: str
    config: Dict = Field(default_factory=dict)


class Note(BaseModel):
    model: str
    deck: str
    fields: Dict[str, str]
    tags: List[str] = Field(default_factory=list)
    media: List[str] = Field(default_factory=list, description="List of local file paths to upload as media")


class Prune(BaseModel):
    decks: bool = False
    models: bool = False
    notes: bool = False


class Config(BaseModel):
    version: int = 1
    backend: str = Field(default="ankiConnect")
    server: Server = Field(default_factory=Server)
    prune: Prune = Field(default_factory=Prune)
    models: List[Model] = Field(default_factory=list)
    decks: List[Deck] = Field(default_factory=list)
    notes: List[Note] = Field(default_factory=list)


def load_config(path: Path) -> Config:
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:
        raise RuntimeError(f"Failed to read YAML: {e}")
    try:
        return Config.model_validate(data)
    except ValidationError as ve:
        raise RuntimeError(f"Config validation failed:\n{ve}")