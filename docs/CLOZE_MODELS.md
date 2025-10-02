# Cloze Models in AnkiDAY

AnkiDAY now supports creating proper Cloze deletion models, which enable you to create flashcards where parts of the text are hidden and must be recalled.

## What are Cloze Deletion Cards?

Cloze deletion is a learning technique where you remove key words or phrases from a sentence, and the learner must fill in the blanks. For example:

**Original text:** "The capital of France is Paris."
**Cloze version:** "The capital of {{c1::France}} is {{c2::Paris}}."

This creates two cards:
1. "The capital of **[...]** is Paris." → Answer: "France"
2. "The capital of France is **[...]**." → Answer: "Paris"

## Configuration

To create a Cloze model in AnkiDAY, you must set `isCloze: true` in your model configuration:

```yaml
models:
  - name: MyClozeModel
    isCloze: true  # This is REQUIRED for cloze models
    css: |
      .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
      }
      .cloze {
        font-weight: bold;
        color: blue;
      }
    fields: [Text, Extra]
    templates:
      - name: Cloze
        qfmt: '{{cloze:Text}}'
        afmt: '{{cloze:Text}}<br>{{#Extra}}{{Extra}}{{/Extra}}'
    uniqueField: Text
```

## Key Requirements

1. **`isCloze: true`** - This parameter is absolutely required. Without it, the model will be created as a regular note type and cloze deletions won't work.

2. **`{{cloze:FieldName}}` syntax** - Use this in your templates instead of regular `{{FieldName}}` syntax.

3. **Cloze deletion syntax** - Use `{{c1::text}}`, `{{c2::text}}`, etc. in your note content.

## Basic Example

```yaml
version: 1
backend: ankiConnect

models:
  - name: BasicCloze
    isCloze: true
    fields: [Text, Extra]
    templates:
      - name: Cloze
        qfmt: '{{cloze:Text}}'
        afmt: '{{cloze:Text}}<br>{{Extra}}'
    uniqueField: Text

decks:
  - name: Study

notes:
  - model: BasicCloze
    deck: Study
    fields:
      Text: "The {{c1::mitochondria}} is the {{c2::powerhouse}} of the cell."
      Extra: "Basic biology fact"
    tags: [biology, cell]
```

## Advanced Example with Multiple Fields

```yaml
models:
  - name: AdvancedCloze
    isCloze: true
    css: |
      .card {
        font-family: Georgia, serif;
        font-size: 18px;
        padding: 20px;
        max-width: 600px;
        margin: 0 auto;
      }
      .cloze {
        font-weight: bold;
        color: #d73502;
        background-color: #ffe6e1;
        padding: 2px 4px;
        border-radius: 3px;
      }
      .hint {
        color: #888;
        font-style: italic;
        margin-bottom: 10px;
      }
      .source {
        color: #666;
        font-size: 14px;
        margin-top: 15px;
        border-top: 1px solid #ddd;
        padding-top: 10px;
      }
    fields: [Text, Hint, Source, Extra]
    templates:
      - name: Cloze
        qfmt: |
          {{#Hint}}<div class="hint">💡 {{Hint}}</div>{{/Hint}}
          {{cloze:Text}}
        afmt: |
          {{#Hint}}<div class="hint">💡 {{Hint}}</div>{{/Hint}}
          {{cloze:Text}}
          {{#Extra}}<hr>{{Extra}}{{/Extra}}
          {{#Source}}<div class="source">📖 Source: {{Source}}</div>{{/Source}}
    uniqueField: Text

notes:
  - model: AdvancedCloze
    deck: Programming
    fields:
      Text: "In Python, {{c1::list comprehensions}} provide a {{c2::concise}} way to create lists. The syntax is {{c3::[expression for item in iterable]}}."
      Hint: "A Pythonic way to create lists"
      Source: "Python Documentation"
      Extra: "More efficient than traditional for loops"
    tags: [python, list-comprehensions]
```

## Cloze Deletion Syntax

### Basic Cloze Deletions
- `{{c1::text}}` - Creates the first cloze deletion
- `{{c2::text}}` - Creates the second cloze deletion
- `{{c3::text}}` - Creates the third cloze deletion, etc.

### Cloze with Hints
- `{{c1::Paris::capital of France}}` - Shows "capital of France" as a hint when the cloze is hidden

### Multiple Deletions on Same Card
```yaml
Text: "{{c1::Python}} is a {{c1::programming language}} that is {{c2::easy to learn}}."
```
This creates two cards:
1. Both "Python" and "programming language" are hidden together (c1)
2. Only "easy to learn" is hidden (c2)

## Template Guidelines

### Question Format (qfmt)
Always use `{{cloze:FieldName}}` syntax:
```yaml
qfmt: '{{cloze:Text}}'
```

### Answer Format (afmt)
Include the cloze field and any additional information:
```yaml
afmt: '{{cloze:Text}}<br>{{#Extra}}{{Extra}}{{/Extra}}'
```

### Conditional Fields
Use Anki's conditional syntax to show fields only when they have content:
```yaml
afmt: |
  {{cloze:Text}}
  {{#Hint}}<div class="hint">{{Hint}}</div>{{/Hint}}
  {{#Extra}}<hr>{{Extra}}{{/Extra}}
```

## CSS Styling

### Default Cloze Styling
Anki automatically applies the `.cloze` class to cloze deletions:

```css
.cloze {
  font-weight: bold;
  color: blue;
}
```

### Night Mode Support
```css
.nightMode .cloze {
  color: lightblue;
}
```

### Custom Styling Examples
```css
/* Highlighted cloze */
.cloze {
  background-color: yellow;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: bold;
}

/* Subtle cloze */
.cloze {
  border-bottom: 2px solid #007acc;
  font-weight: bold;
  color: #007acc;
}
```

## Best Practices

### 1. Keep Deletions Focused
- Delete key information, not trivial words
- Avoid deleting too much text at once
- Focus on the most important concepts

### 2. Use Meaningful Context
```yaml
# Good
Text: "The {{c1::French Revolution}} began in {{c2::1789}} and led to major social changes."

# Avoid
Text: "{{c1::The}} {{c2::French}} {{c3::Revolution}} {{c4::began}} {{c5::in}} {{c6::1789}}."
```

### 3. Logical Grouping
Group related information under the same cloze number:
```yaml
Text: "{{c1::DNA}} is made of {{c1::nucleotides}}, while {{c2::RNA}} is made of {{c2::ribonucleotides}}."
```

### 4. Use Hints Sparingly
Only add hints when the context isn't enough:
```yaml
Text: "The largest planet is {{c1::Jupiter::gas giant}}."
```

### 5. Provide Context in Extra Field
Use the Extra field for additional explanation or examples:
```yaml
Extra: "Jupiter is more than twice as massive as all other planets combined."
```

## Common Pitfalls

### 1. Forgetting `isCloze: true`
Without this parameter, your model will be created as a regular note type and cloze syntax won't work.

### 2. Using Wrong Template Syntax
```yaml
# Wrong
qfmt: '{{Text}}'

# Correct
qfmt: '{{cloze:Text}}'
```

### 3. Over-clozing
Deleting too many words makes cards difficult to answer and reduces learning effectiveness.

### 4. Not Testing Cards
Always review your cloze cards in Anki to ensure they display correctly and provide appropriate difficulty.

## Migration from Existing Cloze Models

If you have existing cloze models created manually in Anki:

1. Export your existing cloze notes
2. Delete the old model (backup first!)
3. Create the new model with `isCloze: true` in AnkiDAY
4. Re-import your notes

## Troubleshooting

### "Cannot create note for unknown reason"
This usually means the model wasn't created as a proper cloze model. Ensure:
- `isCloze: true` is set in your model configuration
- You're using `{{cloze:FieldName}}` in your templates
- Your notes contain valid cloze syntax like `{{c1::text}}`

### Cloze Deletions Not Working
- Verify the model has `isCloze: true`
- Check that you're using the correct template syntax
- Ensure your note text contains cloze deletion markers

### Styling Issues
- Use `.cloze` class in your CSS to style cloze deletions
- Test your styling in Anki's card preview
- Consider night mode compatibility

## Complete Working Example

```yaml
version: 1
backend: ankiConnect

models:
  - name: StudyCloze
    isCloze: true
    css: |
      .card {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 20px;
        line-height: 1.5;
        color: #333;
        background: #fff;
        padding: 20px;
        max-width: 600px;
        margin: 0 auto;
      }
      .cloze {
        font-weight: bold;
        color: #007acc;
        background-color: #e8f4f8;
        padding: 2px 6px;
        border-radius: 4px;
      }
      .extra {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid #eee;
        color: #666;
        font-size: 16px;
      }
    fields: [Text, Extra]
    templates:
      - name: Cloze
        qfmt: '{{cloze:Text}}'
        afmt: '{{cloze:Text}}{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}'
    uniqueField: Text

decks:
  - name: Geography

notes:
  - model: StudyCloze
    deck: Geography
    fields:
      Text: "The {{c1::Amazon River}} is the {{c2::longest}} river in {{c3::South America}} and flows into the {{c4::Atlantic Ocean}}."
      Extra: "The Amazon River system is approximately 6,400 km (4,000 miles) long."
    tags: [geography, rivers, south-america]
```

This will create a functional cloze model that generates four separate cards from the single note, each testing different pieces of information about the Amazon River.