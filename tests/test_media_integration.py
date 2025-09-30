#!/usr/bin/env python3
"""Integration tests for media functionality."""

import tempfile
import json
import base64
from pathlib import Path
from unittest.mock import Mock, patch

from ankiday.config import load_config
from ankiday.backends.ankiconnect import AnkiConnectBackend
# Import the ops module functions (adjust as needed based on actual structure)
# from ankiday.ops import plan_changes, apply_changes

def test_media_planning():
    """Test that media files are correctly loaded from config."""
    
    # Load config with media
    config = load_config(Path("examples/config.with-media.yaml"))
    
    # Check that media is included in notes
    media_notes = [n for n in config.notes if n.media]
    
    assert len(media_notes) > 0, "Should have notes with media"
    
    first_media_note = media_notes[0]
    assert len(first_media_note.media) > 0, "Note should have media files"
    
    print(f"✅ Found {len(media_notes)} notes with media")
    print(f"   First note has {len(first_media_note.media)} media files")

def test_media_file_resolution():
    """Test that media file paths are correctly resolved."""
    
    config = load_config(Path("examples/config.with-media.yaml"))
    config_dir = Path("examples")
    
    # Get notes with media
    media_notes = [n for n in config.notes if n.media]
    assert len(media_notes) > 0, "Should have notes with media"
    
    note = media_notes[0]
    media_file = note.media[0]
    
    # Resolve the path
    if not Path(media_file).is_absolute():
        resolved_path = config_dir / media_file
    else:
        resolved_path = Path(media_file)
    
    print(f"✅ Media file path resolution works")
    print(f"   Original: {media_file}")
    print(f"   Resolved: {resolved_path}")
    
    # Check that the file exists (for our test examples)
    if resolved_path.name == "sample.svg":
        expected_path = Path("examples/media/sample.svg")
        assert expected_path.exists(), f"Test media file should exist: {expected_path}"
        print(f"   File exists: {expected_path}")

def test_backend_media_methods():
    """Test that AnkiConnect backend has all required media methods."""
    
    backend = AnkiConnectBackend("http://localhost:8765", 30)
    
    # Check that all media methods exist
    assert hasattr(backend, 'store_media_file'), "Backend should have store_media_file method"
    assert hasattr(backend, 'retrieve_media_file'), "Backend should have retrieve_media_file method"  
    assert hasattr(backend, 'get_media_files_names'), "Backend should have get_media_files_names method"
    assert hasattr(backend, 'delete_media_file'), "Backend should have delete_media_file method"
    
    print("✅ Backend has all required media methods")

def test_base64_encoding():
    """Test base64 encoding/decoding for media files."""
    
    # Create a small test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test media content")
        test_file = Path(f.name)
    
    try:
        # Read and encode
        content = test_file.read_bytes()
        encoded = base64.b64encode(content).decode('utf-8')
        
        # Decode back
        decoded = base64.b64decode(encoded)
        
        assert content == decoded, "Round-trip encoding should preserve content"
        print("✅ Base64 encoding/decoding works correctly")
        
    finally:
        test_file.unlink()  # Clean up

def test_media_validation():
    """Test media field validation in config."""
    
    from ankiday.config import Note
    
    # Test valid media list
    note = Note(
        model="Test",
        deck="Test",
        fields={"Front": "Test"},
        media=["image.png", "audio.mp3"]
    )
    
    assert note.media == ["image.png", "audio.mp3"]
    
    # Test empty media list (default)
    note_empty = Note(
        model="Test", 
        deck="Test",
        fields={"Front": "Test"}
    )
    
    assert note_empty.media == []
    
    print("✅ Media field validation works correctly")

if __name__ == "__main__":
    print("🧪 Testing AnkiDAY Media Integration")
    print("=" * 45)
    
    try:
        test_media_validation()
        print("✅ Media validation test passed")
        
        test_base64_encoding() 
        print("✅ Base64 encoding test passed")
        
        test_backend_media_methods()
        print("✅ Backend methods test passed")
        
        test_media_file_resolution()
        print("✅ Media file resolution test passed") 
        
        test_media_planning()
        print("✅ Media config loading test passed")
        
        print("\n🎉 All integration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)