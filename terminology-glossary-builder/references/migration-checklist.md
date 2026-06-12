# Migration checklist

Use this checklist when moving from an earlier package layout to version 1.1.0.

## Python module layout

- Replace imports from hyphenated script filenames with package imports.
- Use `from terminology_glossary_builder import GlossaryBuilder`.
- Use `terminology_glossary_builder.client` for direct module imports.
- Keep direct scripts only as entry points, not as import targets.

## Deleted or replaced paths

| Earlier path | Replacement |
|---|---|
| `scripts/terminology-glossary-builder-client.py` | `terminology_glossary_builder/client.py` and `scripts/terminology_glossary_builder_client.py` |
| `scripts/terminology-glossary-builder-cli.py` | `terminology_glossary_builder/cli.py` and `scripts/terminology_glossary_builder_cli.py` |
| tests with hyphenated module names | `scripts/test_terminology_glossary_builder_client.py` |

## Installation

Run both commands from the package root:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## CLI chain update

Use the id returned by `create` in the next command:

```bash
CREATE_RESPONSE=$(tgb create "VAT" "Receipt" --industry tax --store ./glossaries.json)
GLOSSARY_ID=$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["id"])' <<< "$CREATE_RESPONSE")
tgb export "$GLOSSARY_ID" --store ./glossaries.json --format markdown
```

## Example scripts

- Pass `--env sandbox` or `--env production`.
- Set `TGB_TERMS` as a comma-separated override.
- Set `TGB_OUTPUT_DIR` to write Markdown output where supported.
- Keep `json.dumps(..., ensure_ascii=False, indent=2)` in custom examples.

## Hebrew content migration

- Remove nikud from technical prose.
- Replace transliterations with accepted Hebrew terms where available.
- Use DD/MM/YYYY for dates.
- Use ₪ for shekel amounts.
- Keep neutral imperative phrasing in documentation and output templates.

## Validation before release

```bash
pytest
python -m compileall scripts/ -q
python -m compileall terminology_glossary_builder/ -q
find . -type f | sort > /tmp/package-files.txt
```
