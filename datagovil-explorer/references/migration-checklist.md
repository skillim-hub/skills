# Migration Checklist

## File and import changes

- Replace hyphenated Python script imports with underscore or package imports.
- Use `from datagovil_explorer import DatagovClient` after installation.
- Use `scripts/datagovil_explorer_client.py` only as a standalone script copy.
- Use `datagovil-explorer` as the console command after `pip install -e .`.
- Remove local path edits or dynamic loaders used only to import hyphenated filenames.

## Installation changes

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Confirm:

```bash
python - <<'PY'
from datagovil_explorer import DatagovClient
print(DatagovClient().action_url("tag_list"))
PY
```

## Environment changes

- Production default: `https://data.gov.il/api/3`.
- Production override: `DATAGOVIL_BASE_URL` or `DATAGOVIL_PRODUCTION_BASE_URL`.
- Sandbox override: `DATAGOVIL_SANDBOX_BASE_URL` or `DATAGOVIL_BASE_URL_SANDBOX`; this is a user-provided test endpoint, not an official data.gov.il sandbox.
- CLI selection: `--env sandbox` or `--env production`.

## Date, currency, and export changes

- Format Israeli dates as DD/MM/YYYY.
- Format money with ₪, for example `₪12,345.50`.
- Keep raw source values for audit before formatting.
- Default CSV encoding is UTF-8 with signature.
- Store query parameters next to exported files.
- Re-check schema with `resource_show` before replacing reports.

## Removal checklist

- Remove generated cache directories.
- Remove public visual references and creator metadata.
- Remove obsolete hyphenated client and test filenames.
- Remove hardcoded endpoints where environment variables now apply.
