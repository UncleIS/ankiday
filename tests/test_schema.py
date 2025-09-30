#!/usr/bin/env python3
"""Test script to validate example YAML files against the JSON schema."""

import json
import yaml
from pathlib import Path
import jsonschema

def test_schema_validation():
    """Test that our example files validate against the schema."""
    
    # Load the schema
    schema_path = Path(__file__).parent.parent / "schema" / "ankiday-config.schema.json"
    with schema_path.open() as f:
        schema = json.load(f)
    
    # Test files to validate
    test_files = [
        "examples/config.example.yaml",
        "examples/config.comprehensive.yaml"
    ]
    
    base_path = Path(__file__).parent.parent
    
    for test_file in test_files:
        print(f"Validating {test_file}...")
        
        file_path = base_path / test_file
        with file_path.open() as f:
            # Skip the schema modeline
            content = f.read()
            if content.startswith("# yaml-language-server:"):
                lines = content.split('\n')[1:]  # Skip first line
                content = '\n'.join(lines)
            
            config = yaml.safe_load(content)
        
        try:
            jsonschema.validate(config, schema)
            print(f"  ✅ {test_file} is valid")
        except jsonschema.ValidationError as e:
            print(f"  ❌ {test_file} validation error: {e.message}")
            print(f"     Path: {' -> '.join(str(p) for p in e.path)}")
            return False
        except jsonschema.SchemaError as e:
            print(f"  ❌ Schema error: {e.message}")
            return False
    
    return True

def test_schema_itself():
    """Test that the schema itself is valid."""
    print("Validating schema...")
    
    schema_path = Path(__file__).parent.parent / "schema" / "ankiday-config.schema.json"
    with schema_path.open() as f:
        schema = json.load(f)
    
    try:
        # Validate against the JSON Schema meta-schema
        jsonschema.Draft7Validator.check_schema(schema)
        print("  ✅ Schema is valid JSON Schema Draft 7")
        return True
    except jsonschema.SchemaError as e:
        print(f"  ❌ Schema validation error: {e.message}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AnkiDAY YAML Schema")
    print("=" * 40)
    
    success = True
    
    # Test the schema itself
    success &= test_schema_itself()
    print()
    
    # Test example files
    success &= test_schema_validation()
    print()
    
    if success:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)