# AnkiDAY

A Python CLI to manage Anki decks, note types (models), and notes from YAML configuration.

**AnkiDAY** = **Anki - Deck as YAML**

- Default backend: AnkiConnect (localhost:8765)
- Future backend: Anki Python API (out-of-process collection manipulation)

Features
- Create/update/delete decks
- Create/update note types (fields, templates, CSS)
- Upsert notes idempotently using a model-defined unique field
- **Media file support**: Automatically upload images, audio, and other media files
- Optional pruning of entities not present in config
- Validate config and print a diff before applying

## Installation

1. **Prerequisites**: Ensure Python 3.10+
2. **Install Anki**: Download and install [Anki](https://apps.ankiweb.net/)
3. **Install AnkiConnect add-on**: 
   - In Anki, go to Tools > Add-ons > Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki
4. **Install this tool**:
   ```bash
   git clone <this-repo>
   cd ankiday
   pip3 install -e .
   ```
5. **Keep Anki running** with AnkiConnect enabled (verify at http://127.0.0.1:8765)

## Usage

### Quick Start

1. See the example config at `examples/config.example.yaml`
2. **IDE Support**: Add this line at the top of your YAML files for autocompletion and validation:
   ```yaml
   # yaml-language-server: $schema=../schema/ankiday-config.schema.json
   ```
2. Validate your config:
   ```bash
   ./run_ankiday.py validate -f examples/config.example.yaml
   ```
3. Preview changes (dry-run):
   ```bash
   ./run_ankiday.py diff -f examples/config.example.yaml
   ```
4. Apply the configuration:
   ```bash
   ./run_ankiday.py apply -f examples/config.example.yaml
   ```

### Commands

**Validate config**
```bash
./run_ankiday.py validate -f examples/config.example.yaml
```

**Show a diff of intended changes (no side effects)**
```bash
./run_ankiday.py diff -f examples/config.example.yaml
```

**Apply changes**
```bash
./run_ankiday.py apply -f examples/config.example.yaml
```

**List current entities from Anki**
```bash
./run_ankiday.py list --decks --models --notes-limit 20
```

**Delete entities explicitly (dangerous)**
```bash
./run_ankiday.py delete --deck "My::Deck" --model "MyModel" --note-query "deck:My::Deck tag:obsolete"
```

Configuration design (YAML)
```yaml
version: 1
backend: ankiConnect  # or "ankiPython" (not yet implemented)
server:
  url: http://127.0.0.1:8765
  timeoutSeconds: 30
prune:
  decks: false
  models: false
  notes: false  # prune notes not in config within targeted decks/models

models:
  - name: BasicExt
    css: |
      .card { font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 20px; }
    fields: [Front, Back, Extra]
    templates:
      - name: Card 1
        qfmt: "{{Front}}"
        afmt: "{{Front}}<hr id=answer>{{Back}}<br>{{Extra}}"
    uniqueField: Front  # used to upsert notes

# Decks can be nested with ::
decks:
  - name: Languages::Spanish
    config: {}

notes:
  - model: BasicExt
    deck: Languages::Spanish
    fields:
      Front: "hola"
      Back: "hello"
      Extra: "greeting"
    tags: [spanish, greeting]
    media:  # Optional: list of media files to upload
      - "audio/hola.mp3"
      - "images/hola.jpg"
  - model: BasicExt
    deck: Languages::Spanish
    fields:
      Front: "adiós"
      Back: "goodbye"
    tags: [spanish]
```

## Schema Support

**IDE Integration**: Full YAML schema support with autocompletion, validation, and documentation.

- **Schema file**: `schema/ankiday-config.schema.json`
- **Documentation**: See `docs/SCHEMA.md` for IDE setup instructions
- **Examples**: 
  - Basic: `examples/config.example.yaml`
  - Comprehensive: `examples/config.comprehensive.yaml`
  - Media Support: `examples/config.with-media.yaml`

**Supported IDEs**: VS Code, JetBrains IDEs, Neovim, Sublime Text

## Media Support

AnkiDAY supports automatic upload and management of media files (images, audio, video) for your flashcards.

### Basic Usage

Add media files to your notes using the `media` field:

```yaml
notes:
  - model: LanguageModel
    deck: Spanish
    fields:
      Word: "hola"
      Audio: "[sound:hola.mp3]"      # Reference the uploaded audio
      Image: "<img src='hola.jpg'>"   # Reference the uploaded image
    media:
      - "audio/hola.mp3"    # Will be uploaded as "hola.mp3"
      - "images/hola.jpg"   # Will be uploaded as "hola.jpg"
    tags: [spanish]
```

### Media Configuration

The `media` field accepts a list of file paths:
- **Relative paths**: Resolved relative to your config file's directory
- **Absolute paths**: Used as-is
- **File types**: Images (PNG, JPG, SVG, etc.), Audio (MP3, WAV, etc.), Video (MP4, etc.)

### Media References in Fields

**Images:**
```html
<img src="filename.jpg" alt="Description">
```

**Audio/Video:**
```html
[sound:filename.mp3]
[sound:pronunciation.wav]
```

### Example Directory Structure

```
my-flashcards/
├── config.yaml
├── media/
│   ├── images/
│   │   └── spain_flag.png
│   └── audio/
│       └── hola.mp3
└── README.md
```

### Key Features

- **Automatic Upload**: Media files are uploaded to Anki when applying configuration
- **Idempotent**: Files are only uploaded once, preventing duplicates
- **Path Resolution**: Supports both relative and absolute file paths
- **Error Handling**: Reports missing files and upload failures
- **Multiple Formats**: Supports various image, audio, and video formats

### Workflow

1. Place media files in your project directory
2. Reference them in the `media` field of your notes
3. Reference uploaded files in note fields using HTML or `[sound:]` syntax
4. Run `./run_ankiday.py apply` to upload media and create/update notes

## Design Notes

- **Idempotent upsert**: Each model specifies a uniqueField; notes are matched using AnkiConnect findNotes with a field filter plus deck restriction.
- **Non-destructive by default**: pruning is disabled. Turn it on per entity type to delete unmanaged entities.
- **Backend abstraction**: all Anki operations go through a backend interface; you can add an Anki Python backend later.
- **YAML schema**: JSON Schema provides IDE support with validation, autocompletion, and inline documentation.

Limitations
- Template and CSS updates use model-wide operations (styling/templates). Field reordering is supported, but removing a field that has data in Anki may require manual cleanup.

## Media Support Implementation

This section documents the technical implementation of media file support in AnkiDAY.

### 🎯 What Was Implemented

Complete media file support for AnkiDAY, allowing users to automatically upload and reference images, audio, and other media files in their Anki flashcards.

### 🔧 Technical Changes

#### 1. Configuration Schema Extension (`ankiday/config.py`)
- Extended `Note` model with `media` field: `List[str]` with default empty list
- Updated JSON schema to include media field validation
- Maintains backward compatibility (media field is optional)

#### 2. Backend Interface (`ankiday/backends/base.py`)
- Added abstract methods for media operations:
  - `store_media_file(filename: str, data: bytes) -> str`
  - `get_media_files_names(pattern: str = "*") -> List[str]`
  - `retrieve_media_file(filename: str) -> bytes`
  - `delete_media_file(filename: str) -> None`

#### 3. AnkiConnect Backend (`ankiday/backends/ankiconnect.py`)
- Implemented all media methods using AnkiConnect API
- Uses base64 encoding for file transfer
- Maps to AnkiConnect actions: `storeMediaFile`, `getMediaFilesNames`, `retrieveMediaFile`, `deleteMediaFile`

#### 4. Operations Logic (`ankiday/ops/apply.py`)
- Extended `upload_media_for_note()` helper function
- Resolves media file paths relative to config directory
- Uploads media files before adding/updating notes
- Handles file existence checking and error reporting

#### 5. JSON Schema (`schema/ankiday-config.schema.json`)
- Added `media` property to note definition
- Type: array of strings
- Description and examples included

### 📁 Files Created/Modified

#### Modified Files
- `ankiday/config.py` - Added media field to Note model
- `ankiday/backends/base.py` - Added abstract media methods
- `ankiday/backends/ankiconnect.py` - Implemented media operations
- `ankiday/ops/apply.py` - Added media upload logic
- `schema/ankiday-config.schema.json` - Extended schema for media
- `.vscode/settings.json.example` - Fixed schema reference

#### New Files
- `examples/config.with-media.yaml` - Comprehensive media example
- `examples/media/sample.svg` - Sample media file
- `examples/media/audio.txt` - Placeholder audio file
- `tests/test_media.py` - Unit tests for media functionality
- `tests/test_media_integration.py` - Integration tests

### ✅ Features Implemented

#### Core Functionality
- ✅ Media file path specification in config
- ✅ Automatic media upload to Anki
- ✅ Relative and absolute path support
- ✅ Base64 encoding/decoding for file transfer
- ✅ Idempotent behavior (no duplicate uploads)

#### Configuration Support
- ✅ YAML configuration with `media` field
- ✅ JSON schema validation
- ✅ Backward compatibility
- ✅ File path resolution

#### API Integration
- ✅ AnkiConnect media commands
- ✅ Error handling and reporting
- ✅ File existence checking
- ✅ Media listing functionality

#### Testing & Validation
- ✅ Unit tests for media configuration
- ✅ Integration tests for backend operations
- ✅ Schema validation tests
- ✅ File path resolution tests
- ✅ Base64 encoding tests

### 🏗️ Architecture

```
User Config (YAML)
       ↓
   Config Parser (validates media field)
       ↓
   Apply Operations (resolves paths, uploads media)
       ↓  
   AnkiConnect Backend (base64 transfer)
       ↓
   AnkiConnect Server (stores in Anki collection)
```

### 🔄 Implementation Workflow

1. User specifies media files in `media` field of notes
2. AnkiDAY resolves file paths relative to config directory  
3. Files are read and base64-encoded
4. Media files uploaded via AnkiConnect `storeMediaFile`
5. Notes created/updated with media references in fields
6. Subsequent runs check existing media to avoid duplicates

### 🧪 Testing Coverage

- **Unit Tests**: Media field validation, path resolution, encoding
- **Integration Tests**: Backend methods, config loading, file operations
- **Schema Tests**: JSON schema validation of media configurations
- **Manual Tests**: End-to-end workflow with real AnkiConnect
