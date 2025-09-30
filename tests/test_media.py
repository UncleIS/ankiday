#!/usr/bin/env python3
"""Test media functionality."""

import tempfile
from pathlib import Path
from ankiday.config import Config, Model, Template, Deck, Note

def test_media_config_validation():
    """Test that media field is properly validated in config."""
    
    # Create a test config with media
    config = Config(
        models=[
            Model(
                name="TestMedia",
                fields=["Front", "Back", "Image"],
                templates=[
                    Template(name="Card 1", qfmt="{{Front}}", afmt="{{Back}}<br>{{Image}}")
                ],
                uniqueField="Front"
            )
        ],
        decks=[
            Deck(name="TestDeck")
        ],
        notes=[
            Note(
                model="TestMedia",
                deck="TestDeck",
                fields={"Front": "Test", "Back": "Answer", "Image": "test.png"},
                media=["test.png", "audio.mp3"]
            )
        ]
    )
    
    assert config.notes[0].media == ["test.png", "audio.mp3"]
    assert len(config.notes[0].media) == 2

def test_media_file_paths():
    """Test that media can handle different path formats."""
    
    note = Note(
        model="Test",
        deck="Test", 
        fields={"Front": "Test"},
        media=[
            "relative/path.png",
            "/absolute/path.jpg",
            "simple.wav"
        ]
    )
    
    assert len(note.media) == 3
    assert "relative/path.png" in note.media
    assert "/absolute/path.jpg" in note.media
    assert "simple.wav" in note.media

def test_empty_media_list():
    """Test that empty media list works correctly."""
    
    note = Note(
        model="Test",
        deck="Test",
        fields={"Front": "Test"}
        # No media specified - should default to empty list
    )
    
    assert note.media == []
    assert len(note.media) == 0

if __name__ == "__main__":
    print("🧪 Testing AnkiDAY Media Functionality")
    print("=" * 40)
    
    try:
        test_media_config_validation()
        print("✅ Media config validation test passed")
        
        test_media_file_paths()
        print("✅ Media file paths test passed") 
        
        test_empty_media_list()
        print("✅ Empty media list test passed")
        
        print("\n🎉 All media tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)