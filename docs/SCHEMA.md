# YAML Schema for AnkiDAY

This document explains how to use the YAML schema for AnkiDAY configuration files to get IDE support, autocompletion, and validation.

## Schema Location

The schema is located at: `schema/ankiday-config.schema.json`

## IDE Setup

### VS Code

1. **Install YAML Extension**: Install the [YAML extension by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

2. **Method 1: File-level schema association**
   Add this line at the top of your YAML file:
   ```yaml
   # yaml-language-server: $schema=../schema/ankiday-config.schema.json
   ```

3. **Method 2: Workspace settings**
   Add to your `.vscode/settings.json`:
   ```json
   {
     "yaml.schemas": {
       "./schema/ankiday-config.schema.json": ["*.ankiday.yaml", "ankiday-*.yaml"]
     }
   }
   ```

4. **Method 3: Global settings**
   Add to your global VS Code settings:
   ```json
   {
     "yaml.schemas": {
       "https://raw.githubusercontent.com/your-repo/ankiday/main/schema/ankiday-config.schema.json": ["*.ankiday.yaml"]
     }
   }
   ```

### JetBrains IDEs (PyCharm, IntelliJ, WebStorm)

1. **Go to Settings** → **Languages & Frameworks** → **Schemas and DTDs** → **JSON Schema Mappings**

2. **Add new mapping**:
   - Name: `AnkiDAY Configuration`
   - Schema file or URL: `schema/ankiday-config.schema.json`
   - File path pattern: `*.ankiday.yaml` or `config*.yaml`

3. **Alternative**: Use modeline in YAML file:
   ```yaml
   # yaml-language-server: $schema=../schema/ankiday-config.schema.json
   ```

### Neovim/Vim

1. **With coc.nvim and coc-yaml**:
   ```vim
   " In your coc-settings.json
   {
     "yaml.schemas": {
       "./schema/ankiday-config.schema.json": ["*.ankiday.yaml", "config*.yaml"]
     }
   }
   ```

2. **With vim-lsp and yaml-language-server**:
   Set up yaml-language-server to recognize the schema through file modelines.

### Sublime Text

1. **Install LSP package and LSP-yaml**
2. **Configure in LSP settings**:
   ```json
   {
     "yaml-language-server": {
       "settings": {
         "yaml.schemas": {
           "./schema/ankiday-config.schema.json": ["*.ankiday.yaml"]
         }
       }
     }
   }
   ```

## Schema Features

The schema provides:

### ✅ **Validation**
- Required fields validation
- Type checking (string, integer, boolean, array, object)
- Format validation (URLs, patterns)
- Value constraints (min/max, enum values)

### ✅ **Autocompletion**
- Property names
- Enum values (`backend: ankiConnect | ankiPython`)
- Template field references

### ✅ **Documentation**
- Hover tooltips with descriptions
- Property documentation
- Default values
- Usage examples

### ✅ **Error Detection**
- Invalid property names
- Type mismatches
- Missing required fields
- Invalid patterns (e.g., deck names with invalid `::` syntax)

## Schema Structure

```
ankiday-config.schema.json
├── version (required)           # Schema version (1)
├── backend                      # ankiConnect | ankiPython
├── server                       # AnkiConnect settings
│   ├── url                      # http://127.0.0.1:8765
│   └── timeoutSeconds           # 1-300
├── prune                        # Deletion settings
│   ├── decks                    # boolean
│   ├── models                   # boolean
│   └── notes                    # boolean
├── models[]                     # Note types array
│   ├── name (required)          # string
│   ├── fields[] (required)      # array of strings
│   ├── templates[] (required)   # array of template objects
│   │   ├── name (required)      # string
│   │   ├── qfmt (required)      # HTML template
│   │   └── afmt (required)      # HTML template
│   ├── css                      # CSS styling
│   └── uniqueField (required)   # field name for upserts
├── decks[]                      # Deck array
│   ├── name (required)          # string with :: pattern
│   └── config                   # deck options
└── notes[]                      # Individual notes array
    ├── model (required)         # model name reference
    ├── deck (required)          # deck name reference
    ├── fields (required)        # field values object
    └── tags                     # array of tag strings
```

## Examples

### Basic Configuration
```yaml
# yaml-language-server: $schema=../schema/ankiday-config.schema.json
version: 1
backend: ankiConnect

models:
  - name: Basic
    fields: [Front, Back]
    templates:
      - name: Card 1
        qfmt: "{{Front}}"
        afmt: "{{Back}}"
    uniqueField: Front

decks:
  - name: Study
    config: {}

notes:
  - model: Basic
    deck: Study
    fields:
      Front: "Question"
      Back: "Answer"
    tags: [example]
```

### Advanced Configuration
See `examples/config.comprehensive.yaml` for a complete example showcasing:
- Multiple models with different field sets
- Complex CSS styling
- Multiple card templates per model
- Nested deck hierarchies
- Cloze deletion notes
- Rich field content with HTML

## Validation Rules

The schema enforces several validation rules:

1. **Required Fields**: `version`, model `name`/`fields`/`templates`/`uniqueField`, etc.
2. **Field References**: `uniqueField` must exist in the model's `fields` array
3. **Deck Names**: Must follow pattern for `::` nested decks
4. **Tags**: No spaces allowed (pattern: `^[^\s]+$`)
5. **URLs**: Server URL must be valid URI format
6. **Ranges**: timeoutSeconds between 1-300

## Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Property 'uniqueField' is not allowed` | Typo in property name | Check spelling |
| `uniqueField must be one of fields` | Field name mismatch | Update Pydantic validation or schema |
| `Expected array, got string` | Wrong data type | Use `[item]` instead of `item` |
| `Pattern '^[^:]*(::[^:]+)*$' failed` | Invalid deck name | Use proper `::` syntax for nesting |
| `Additional property 'xyz' is not allowed` | Unknown property | Remove or fix property name |

## Troubleshooting

### Schema Not Working?

1. **Check file association**: Ensure your YAML file is associated with the schema
2. **Verify schema path**: Make sure the path in the modeline is correct
3. **IDE restart**: Restart your IDE after changing schema settings
4. **YAML extension**: Ensure you have a YAML language server installed
5. **Syntax errors**: Fix any YAML syntax errors first

### Autocompletion Not Showing?

1. **Trigger manually**: Use Ctrl+Space (VS Code) or IDE-specific shortcut
2. **Check context**: Autocompletion works best in the right context (e.g., under `models:`)
3. **Schema validation**: Ensure the schema is valid JSON

### Performance Issues?

Large configuration files with many notes may cause IDE slowdown. Consider:
- Splitting large configs into multiple files
- Using external data sources for bulk note creation
- Optimizing the JSON schema for better performance