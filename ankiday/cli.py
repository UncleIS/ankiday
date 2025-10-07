from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

from .config import load_config, Config
from .ops.apply import Planner, Applier
from .backends.ankiconnect import AnkiConnectBackend

app = typer.Typer(add_completion=False, help="Manage Anki decks, models, and notes from YAML config")


def _load_backend(cfg: Config, verbose: bool = False):
    if cfg.backend == "ankiConnect":
        return AnkiConnectBackend(base_url=cfg.server.url, timeout=cfg.server.timeoutSeconds, verbose=verbose)
    else:
        raise typer.BadParameter("Only 'ankiConnect' backend is implemented at the moment")


@app.command()
def validate(
    file: Path = typer.Option(..., "-f", "--file", exists=True, readable=True, help="YAML config"),
    skip_model_validation: bool = typer.Option(False, "--skip-model-validation", help="Skip model validation and rely on existing models in Anki"),
) -> None:
    """Validate YAML config file."""
    cfg = load_config(file)
    
    if not skip_model_validation:
        # Perform model reference validation
        model_names = {m.name for m in cfg.models}
        for note in cfg.notes:
            if note.model not in model_names:
                typer.secho(f"Error: Note references unknown model '{note.model}'. Available models in config: {sorted(model_names)}", fg=typer.colors.RED)
                typer.secho("Hint: Use --skip-model-validation if the model exists in Anki but not in this config file.", fg=typer.colors.YELLOW)
                raise typer.Exit(code=1)
    
    typer.secho("Config is valid.", fg=typer.colors.GREEN)


@app.command()
def diff(
    file: Path = typer.Option(..., "-f", "--file", exists=True, readable=True, help="YAML config"),
    json_out: bool = typer.Option(False, "--json", help="Output machine-readable diff"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show verbose output with detailed progress"),
    skip_model_validation: bool = typer.Option(False, "--skip-model-validation", help="Skip model validation and rely on existing models in Anki"),
) -> None:
    cfg = load_config(file)
    backend = _load_backend(cfg, verbose=verbose)
    planner = Planner(backend, verbose=verbose, skip_model_validation=skip_model_validation)
    plan = planner.build_plan(cfg)
    if json_out:
        typer.echo(json.dumps(plan.to_dict(), indent=2))
    else:
        typer.echo(plan.pretty())


@app.command()
def apply(
    file: Path = typer.Option(..., "-f", "--file", exists=True, readable=True, help="YAML config"),
    assume_yes: bool = typer.Option(False, "-y", "--yes", help="Do not prompt for confirmation"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show verbose output with detailed progress"),
    skip_model_validation: bool = typer.Option(False, "--skip-model-validation", help="Skip model validation and rely on existing models in Anki"),
) -> None:
    cfg = load_config(file)
    backend = _load_backend(cfg, verbose=verbose)
    planner = Planner(backend, verbose=verbose, skip_model_validation=skip_model_validation)
    plan = planner.build_plan(cfg)
    if not plan.steps:
        typer.secho("Nothing to do.", fg=typer.colors.GREEN)
        raise typer.Exit(code=0)
    typer.echo(plan.pretty())
    if not assume_yes:
        proceed = typer.confirm("Apply these changes?", default=False)
        if not proceed:
            raise typer.Exit(code=1)
    Applier(backend, verbose=verbose).apply(plan, config_dir=file.parent)
    typer.secho("Apply complete.", fg=typer.colors.GREEN)


@app.command()
def list(
    decks: bool = typer.Option(False, "--decks", help="List decks"),
    models: bool = typer.Option(False, "--models", help="List models"),
    notes_limit: int = typer.Option(0, "--notes-limit", help="List up to N notes"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show verbose output with detailed progress"),
) -> None:
    """List current Anki entities via backend."""
    # Default to listing decks if nothing chosen
    if not any([decks, models, notes_limit]):
        decks = True
    backend = AnkiConnectBackend(verbose=verbose)
    if decks:
        names = backend.list_decks()
        typer.echo("Decks:")
        for n in names:
            typer.echo(f"  - {n}")
    if models:
        names = backend.list_models()
        typer.echo("Models:")
        for n in names:
            typer.echo(f"  - {n}")
    if notes_limit:
        ids = backend.find_notes("")
        ids = ids[:notes_limit]
        if ids:
            notes = backend.notes_info(ids)
            typer.echo(f"Notes (showing {len(notes)}):")
            for ni in notes:
                model = ni.get("modelName")
                deck = ni.get("fields", {}).get("Deck", {}).get("value") or ni.get("deckName")
                fields = {k: v.get("value") for k, v in ni.get("fields", {}).items()}
                typer.echo(f"  - id={ni['noteId']} model={model} deck={deck} fields={fields}")


@app.command()
def delete(
    deck: Optional[str] = typer.Option(None, "--deck", help="Delete deck by name (cards moved unless --cards too)"),
    cards_too: bool = typer.Option(False, "--cards", help="Delete cards within deck when deleting a deck"),
    model: Optional[str] = typer.Option(None, "--model", help="Delete model (note type) by name"),
    note_query: Optional[str] = typer.Option(None, "--note-query", help="JQL-like Anki browse query for notes to delete"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Do not prompt for confirmation"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show verbose output with detailed progress"),
) -> None:
    backend = AnkiConnectBackend(verbose=verbose)
    actions = []
    if deck:
        actions.append(f"Delete deck '{deck}' (cardsToo={cards_too})")
    if model:
        actions.append(f"Delete model '{model}'")
    if note_query:
        actions.append(f"Delete notes matching query '{note_query}'")
    if not actions:
        typer.secho("Nothing specified to delete.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
    typer.echo("Planned deletions:")
    for a in actions:
        typer.echo(f"  - {a}")
    if not yes and not typer.confirm("Proceed?", default=False):
        raise typer.Exit(code=1)
    if deck:
        backend.delete_decks([deck], cards_too=cards_too)
    if model:
        backend.delete_model(model)
    if note_query:
        ids = backend.find_notes(note_query)
        if ids:
            backend.delete_notes(ids)
    typer.secho("Deletion complete.", fg=typer.colors.GREEN)