# Migration Checklist

Use this checklist when upgrading from a manual template, a previous prototype, or a package that used non-importable script names.

## Package layout

1. Use `free_text_invoice_explanation` as the importable Python module.
2. Import from the package, not from a script path.
3. Keep script launchers in `scripts/`.
4. Keep the client compatibility entry at `scripts/free_text_invoice_explanation_client.py`.
5. Do not use a hyphenated Python module for imports.
6. Run `pip install -e .` before examples or tests.

## Imports

Replace path-based imports with package imports.

Old pattern:

```python
# Avoid importing by file path or editing sys.path.
```

New pattern:

```python
from free_text_invoice_explanation import InvoiceExplanationClient
```

## CLI

Use the installed command:

```bash
invoice-explain explain --input invoice.json --env sandbox
```

Use the launcher only when working from the source tree:

```bash
python scripts/free-text-invoice-explanation-cli.py explain --input invoice.json --env sandbox
```

## Data model

1. Move line descriptions into `lines[].description`.
2. Move business classification into `context.business_type`.
3. Move document type into `context.document_type`.
4. Keep amounts as decimal strings.
5. Use `reimbursable`, `reverse_charge`, and `exempt_from_vat` for edge cases.

## README quick-start

Use this install sequence:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

After generating a response, extract the first explanation title and reuse it for selection:

```bash
EXPLANATION_ID="$(python - <<'PY'
import json
data = json.load(open("response.json", encoding="utf-8"))
print(data["explanations"][0]["title"])
PY
)"
```

## Hebrew content

1. Use `חשבונית מס`, not transliterated terms.
2. Use `קבלה`, `חשבונית מס/קבלה`, and `חשבונית זיכוי`.
3. Use `עוסק פטור` and `עוסק מורשה`.
4. Use `מע״מ` and `מע״מ תשומות`.
5. Use `₪` and `DD/MM/YYYY`.
6. Remove vowel marks from technical prose.
7. Keep the voice impersonal and neutral.

## Validation

Run:

```bash
pytest -q
python -m compileall scripts/ -q
```

Review:

1. Branding audit.
2. Hebrew quality log.
3. Test scenarios.
4. Production checklist.
