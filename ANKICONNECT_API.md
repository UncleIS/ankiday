# AnkiConnect API Documentation

This document summarizes the correct AnkiConnect API format for model template and styling updates, discovered during AnkiDAY implementation.

## Version
- AnkiConnect version: 6
- Tested with Anki 2.x

## Model Templates

### Get Templates (Read)
```json
{
  "action": "modelTemplates",
  "version": 6,
  "params": {
    "modelName": "ModelName"
  }
}
```

**Returns:**
```json
{
  "result": {
    "Card 1": {
      "Front": "{{Front}}",
      "Back": "{{Front}}<hr id=answer>{{Back}}"
    }
  },
  "error": null
}
```

### Update Templates (Write)
```json
{
  "action": "updateModelTemplates",
  "version": 6,
  "params": {
    "model": {
      "name": "ModelName",
      "templates": {
        "Card 1": {
          "Front": "{{Front}}",
          "Back": "{{Front}}<hr id=answer>{{Back}}"
        }
      }
    }
  }
}
```

**Key differences:**
- Read operation uses `modelName` parameter
- Write operation uses nested `model.name` parameter
- Write operation expects templates as nested object, not array

## Model Styling

### Get Styling (Read)
```json
{
  "action": "modelStyling",
  "version": 6,
  "params": {
    "modelName": "ModelName"
  }
}
```

**Returns:**
```json
{
  "result": {
    "css": ".card { font-size: 20px; }"
  },
  "error": null
}
```

### Update Styling (Write)
```json
{
  "action": "updateModelStyling",
  "version": 6,
  "params": {
    "model": {
      "name": "ModelName",
      "css": ".card { font-size: 24px; }"
    }
  }
}
```

**Key differences:**
- Read operation uses `modelName` parameter
- Write operation uses nested `model.name` and `model.css` parameters

## Implementation Notes

1. **Parameter naming inconsistency**: Read operations use `modelName`, write operations use `model.name`
2. **Template format conversion**: Our internal format uses arrays with `qfmt`/`afmt`, AnkiConnect expects object with `Front`/`Back`
3. **Both operations return null on success**: Check for `error` field to detect failures

## Testing Commands

```bash
# Test styling update
curl -X POST -d '{"action": "updateModelStyling", "version": 6, "params": {"model": {"name": "BasicExt", "css": ".card { color: red; }"}}}' http://127.0.0.1:8765

# Test template update  
curl -X POST -d '{"action": "updateModelTemplates", "version": 6, "params": {"model": {"name": "BasicExt", "templates": {"Card 1": {"Front": "{{Front}}", "Back": "{{Back}}"}}}}}' http://127.0.0.1:8765

# Verify changes
curl -X POST -d '{"action": "modelStyling", "version": 6, "params": {"modelName": "BasicExt"}}' http://127.0.0.1:8765
curl -X POST -d '{"action": "modelTemplates", "version": 6, "params": {"modelName": "BasicExt"}}' http://127.0.0.1:8765
```