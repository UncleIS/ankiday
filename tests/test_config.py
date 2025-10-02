"""Basic tests for ankiday configuration."""

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
    try:
        Model(
            name="BadModel",
            fields=["Front", "Back"],
            templates=[
                Template(name="Card 1", qfmt="{{Front}}", afmt="{{Back}}")
            ],
            uniqueField="Invalid"  # Not in fields!
        )
        raise Exception("Should have raised ValueError")
    except ValueError as e:
        if "uniqueField 'Invalid' must be one of fields" not in str(e):
            raise Exception(f"Wrong error message: {e}")


def test_cloze_model_configuration():
    """Test that cloze models can be configured with isCloze=True."""
    cloze_model = Model(
        name="ClozeModel",
        fields=["Text", "Extra"],
        templates=[
            Template(
                name="Cloze",
                qfmt="{{cloze:Text}}",
                afmt="{{cloze:Text}}<br>{{Extra}}"
            )
        ],
        isCloze=True,
        uniqueField="Text"
    )

    assert cloze_model.isCloze == True
    assert cloze_model.name == "ClozeModel"
    assert "Text" in cloze_model.fields
    assert "Extra" in cloze_model.fields
    assert cloze_model.templates[0].qfmt == "{{cloze:Text}}"


def test_regular_model_defaults_to_non_cloze():
    """Test that regular models default to isCloze=False."""
    regular_model = Model(
        name="RegularModel",
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

    assert regular_model.isCloze == False


if __name__ == "__main__":
    test_config_validation()
    print("Basic config validation test passed!")

    test_unique_field_validation()
    print("Unique field validation test passed!")

    test_cloze_model_configuration()
    print("Cloze model configuration test passed!")

    test_regular_model_defaults_to_non_cloze()
    print("Regular model defaults test passed!")
