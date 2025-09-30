"""Basic tests for ankiday configuration."""

import pytest
from pathlib import Path
from ankiday.config import Config, Model, Template, Deck, Note


def test_config_validation():
    """Test basic config validation."""
    config = Config(
        models=[
            Model(
                name="Basic",
                fields=["Front", "Back"],
                templates=[
                    Template(
                        name="Card 1",
                        qfmt="{{Front}}",
                        afmt="{{Back}}"
                    )
                ],
                uniqueField="Front"
            )
        ],
        decks=[
            Deck(name="TestDeck")
        ],
        notes=[
            Note(
                model="Basic",
                deck="TestDeck", 
                fields={"Front": "Question", "Back": "Answer"}
            )
        ]
    )
    
    assert config.version == 1
    assert config.backend == "ankiConnect"
    assert len(config.models) == 1
    assert config.models[0].name == "Basic"
    assert len(config.decks) == 1
    assert config.decks[0].name == "TestDeck"


def test_unique_field_validation():
    """Test that uniqueField must be in fields."""
    with pytest.raises(ValueError, match="uniqueField 'Invalid' must be one of fields"):
        Model(
            name="BadModel",
            fields=["Front", "Back"],
            templates=[
                Template(name="Card 1", qfmt="{{Front}}", afmt="{{Back}}")
            ],
            uniqueField="Invalid"  # Not in fields!
        )


if __name__ == "__main__":
    test_config_validation()
    print("Basic config validation test passed!")
    
    try:
        test_unique_field_validation()
    except ValueError:
        print("Unique field validation test passed!")
    else:
        print("ERROR: Unique field validation should have failed!")