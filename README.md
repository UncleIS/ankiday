# AnkiDAY

A Python CLI to manage Anki decks, note types (models), and notes from YAML configuration.

**AnkiDAY** = **Anki - Deck as YAML**

> **Disclaimer**: This project is NOT affiliated with, endorsed by, or connected to Anki or the AnkiWeb service. AnkiDAY is an independent third-party tool that interacts with Anki through the AnkiConnect add-on. All trademarks are property of their respective owners.

- Default backend: AnkiConnect (localhost:8765)
- Future backend: Anki Python API (out-of-process collection manipulation)

Features
- Create/update/delete decks
- Create/update note types (fields, templates, CSS)
- **Cloze deletion models**: Full support for creating proper cloze models with `isCloze: true`
- Upsert notes idempotently using a model-defined unique field
- **Media file support**: Automatically upload images, audio, and other media files
- Optional pruning of entities not present in config
- Validate config and print a diff before applying

## Installation

### Prerequisites
1. **Python 3.10+**: Ensure you have Python 3.10 or later installed
   - **Windows**: Download from [python.org](https://www.python.org/downloads/) (make sure to check "Add to PATH")
   - **macOS**: Use Homebrew (`brew install python`) or download from python.org
   - **Linux**: Use your package manager (`apt install python3`, `dnf install python3`, etc.)
2. **Anki Desktop**: Download and install [Anki](https://apps.ankiweb.net/) for your platform
3. **AnkiConnect Add-on**:
   - Open Anki
   - Go to Tools → Add-ons → Get Add-ons
   - Enter code: `2055492159`
   - Click OK and restart Anki
   - Verify AnkiConnect is working by visiting http://127.0.0.1:8765 in your browser (should show a simple page)

### Install AnkiDAY

**Method 1: From source (recommended)**
```bash
git clone https://github.com/yourusername/ankiday.git
cd ankiday
pip install -e .
```

**Method 2: Direct installation (when published)**
```bash
pip install ankiday
```

> **Note**: On some systems (especially macOS), you may need to add Python's bin directory to your PATH or create a symlink. See the troubleshooting section below if the `ankiday` command is not found after installation.

### Platform Support

- **macOS**: Tested and fully supported
- **Linux**: Should work (cross-platform dependencies)
- **Windows**: Should work but **untested** (see Windows-specific instructions below)

### Verify Installation
```bash
ankiday --help
```

### Troubleshooting Installation

**If `ankiday` command is not found:**

1. **Find where ankiday was installed:**
   ```bash
   python3 -c "import sys; print(sys.executable.replace('/python3', '/ankiday'))"
   ```

2. **Test the command directly:**
   ```bash
   # Use the path from step 1, for example:
   /Library/Frameworks/Python.framework/Versions/3.12/bin/ankiday --help
   ```

3. **Fix the PATH (choose one method):**

   **Option A - Add to PATH permanently:**
   ```bash
   # Replace with your actual path from step 1
   echo 'export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

   **Option B - Create symlink:**
   ```bash
   # Replace with your actual path from step 1
   sudo ln -sf /Library/Frameworks/Python.framework/Versions/3.12/bin/ankiday /usr/local/bin/ankiday
   ```

4. **Verify it works:**
   ```bash
   ankiday --help
   ```

**Windows users (untested):**

If `ankiday` command is not found on Windows:

1. **Find ankiday location:**
   ```cmd
   python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts\\ankiday.exe'))"
   ```

2. **Test command directly:**
   ```cmd
   # Use the path from step 1, for example:
   C:\Python310\Scripts\ankiday.exe --help
   ```

3. **Add to PATH (PowerShell):**
   ```powershell
   # Replace with your actual path from step 1
   $env:PATH += ";C:\Python310\Scripts"
   # To make permanent, add to your PowerShell profile
   ```

4. **Alternative - Use full path:**
   ```cmd
   C:\Python310\Scripts\ankiday.exe validate -f config.yaml
   ```

> **Windows Note**: AnkiDAY uses cross-platform Python libraries and should work on Windows, but hasn't been tested. The main difference is using `.exe` extensions and different path syntax. Please report any Windows-specific issues!

**Important**: Always keep Anki running with the AnkiConnect add-on enabled when using AnkiDAY.

## Usage

### Quick Start

1. **Start Anki** and ensure AnkiConnect is running (visit http://127.0.0.1:8765 to verify)
2. **Create a config file**: See the example at `examples/config.example.yaml`
3. **IDE Support** (optional): Add this line at the top of your YAML files for autocompletion:
   ```yaml
   # yaml-language-server: $schema=../schema/ankiday-config.schema.json
   ```
4. **Validate** your config:
   ```bash
   ankiday validate -f examples/config.example.yaml
   ```
5. **Preview changes** (dry-run):
   ```bash
   ankiday diff -f examples/config.example.yaml
   ```
6. **Apply** the configuration:
   ```bash
   ankiday apply -f examples/config.example.yaml
   ```

### Commands

**Validate config**
```bash
ankiday validate -f examples/config.example.yaml
```

**Show a diff of intended changes (no side effects)**
```bash
ankiday diff -f examples/config.example.yaml
```

**Apply changes**
```bash
ankiday apply -f examples/config.example.yaml
```

**List current entities from Anki**
```bash
ankiday list --decks --models --notes-limit 20
```

**Delete entities explicitly (dangerous)**
```bash
ankiday delete --deck "My::Deck" --model "MyModel" --note-query "deck:My::Deck tag:obsolete"
```

### Verbose Output

All commands support the `--verbose` (or `-v`) flag for detailed output:

```bash
# Show detailed output during operations
ankiday diff -f config.yaml --verbose
ankiday apply -f config.yaml --verbose
ankiday list --decks --verbose
```

Verbose mode shows:
- AnkiConnect API calls and parameters
- Step-by-step progress during plan generation and execution
- Media file upload details
- Success/failure status for each operation

This is useful for debugging, learning how AnkiDAY works, and monitoring progress during large operations.

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
4. Run `ankiday apply` to upload media and create/update notes

## Design Notes

- **Idempotent upsert**: Each model specifies a uniqueField; notes are matched using AnkiConnect findNotes with a field filter plus deck restriction.
- **Non-destructive by default**: pruning is disabled. Turn it on per entity type to delete unmanaged entities.
- **Backend abstraction**: all Anki operations go through a backend interface; you can add an Anki Python backend later.
- **YAML schema**: JSON Schema provides IDE support with validation, autocompletion, and inline documentation.

Limitations
- Template and CSS updates use model-wide operations (styling/templates). Field reordering is supported, but removing a field that has data in Anki may require manual cleanup.
