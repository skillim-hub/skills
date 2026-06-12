# Troubleshooting

## Import and installation issues

### `ModuleNotFoundError: terminology_glossary_builder`

Cause: The package was not installed from the package root.

Fix:

```bash
cd terminology-glossary-builder
pip install -e .
```

### Command `tgb` is unavailable

Cause: Console scripts were not installed into the active environment.

Fix:

```bash
pip install -e .
python -m terminology_glossary_builder.cli --help
```

### Tests do not discover async tests

Cause: `pytest-asyncio` is missing.

Fix:

```bash
pip install -r requirements-dev.txt
pytest
```

## Glossary quality issues

### Unknown term appears with review warning

Cause: The term is not in the built-in template library.

Fix:

- Keep the warning for drafts.
- Add an Israeli authority source before external use.
- Add a custom template when the term repeats across glossaries.

### Hebrew term is literal or awkward

Cause: Missing industry context or an English-first phrase.

Fix:

- Set a precise industry such as `tax`, `freelance`, `retail`, `privacy`, `corporate`, or `import`.
- Prefer accepted Israeli professional terms.
- Avoid transliteration when a real Hebrew term exists.

### VAT, thresholds, or fees look outdated

Cause: Date-sensitive values were copied from old material.

Fix:

- Remove the number or verify it against the relevant authority.
- Add a DD/MM/YYYY validity date.
- Add a warning when the amount may change.

## Source issues

### A source is too broad

Cause: Landing pages often identify the authority but not the exact term.

Fix:

- Keep the landing page only for draft context.
- Link a more specific page before publication.
- Add a note that the exact source page needs verification.

### A consumer term uses a tax source only

Cause: Retail and consumer workflows can mix accounting and consumer rights.

Fix:

- Cite the Tax Authority for VAT and invoice terms.
- Cite the Consumer Protection and Fair Trade Authority for cancellation and warranty terms.
- Split the entry when one term has separate tax and consumer meanings.

## CLI and store issues

### Export cannot find the glossary id

Cause: The export command uses a different store path from the create command.

Fix:

```bash
CREATE_RESPONSE=$(tgb create "VAT" --store ./glossaries.json)
GLOSSARY_ID=$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["id"])' <<< "$CREATE_RESPONSE")
tgb export "$GLOSSARY_ID" --store ./glossaries.json
```

### JSON output contains escaped Hebrew

Cause: A custom script did not use `ensure_ascii=False`.

Fix:

```python
json.dumps(payload, ensure_ascii=False, indent=2)
```

### CSV Hebrew appears broken in spreadsheet software

Cause: The file was opened with the wrong encoding.

Fix: Import the file as UTF-8 or use Markdown/JSON for review.

## Packaging issues

### Hyphenated script imports fail

Cause: Hyphens are not valid in Python import names.

Fix: Use the package import path:

```python
from terminology_glossary_builder import GlossaryBuilder
```

### Direct script execution cannot find the package

Cause: The current environment does not include the editable install.

Fix:

```bash
pip install -e .
python scripts/examples/build_freelancer_tax_glossary.py --env sandbox
```
