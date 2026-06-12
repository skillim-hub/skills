# Migration Checklist

Use this checklist when moving from an earlier package version or from ad-hoc scripts.

## File-name migration

- Delete imports that load the legacy hyphenated client file by path.
- Import the package directly:

```python
from forms_certificates_downloader import FormsCertificatesClient
```

- Use the installed CLI command:

```bash
forms-certificates-downloader list-sources
```

- Keep `scripts/forms_certificates_downloader_client.py` only as a compatibility entry point.

## Installation migration

Use editable installation:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Do not rely on `sys.path` modifications inside scripts.

## Registry migration

1. Copy custom sources into `data/portal-registry.json`.
2. Verify each URL is public.
3. Run `list-sources` with the custom registry.
4. Run discovery with a small limit.
5. Keep old manifests until retention rules allow removal.

## Manifest migration

The manifest schema remains simple JSON:

```json
{
  "schema_version": 1,
  "updated_at": "2026-06-02T09:16:00+00:00",
  "documents": {}
}
```

Before replacing a manifest:

- Back up the old file.
- Export CSV.
- Confirm every important document key still resolves.
- Keep old checksums for audit comparison.

## CLI migration

Replace direct download commands with a saved request chain when repeatability matters:

```bash
CREATE_RESPONSE=$(forms-certificates-downloader create-request tax-authority-public-forms \
  --query "1301" --limit 5 --download-dir ./downloads --json-output)
REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$CREATE_RESPONSE")
forms-certificates-downloader run-request "$REQUEST_ID" --download-dir ./downloads --json-output
```

## Hebrew and localization migration

- Use ₪ for currency notes.
- Use DD/MM/YYYY in human-facing operating notes.
- Keep ISO timestamps in machine-readable JSON.
- Keep Hebrew file titles when possible.
- Avoid niqqud in technical prose.

## Validation before release

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
```

Check that public Markdown contains no decorative image-style references, maintainer metadata, or organization callouts.


## Migration from 2.1.0 to 2.2.0

- Replace stale registry URLs with the web-validated defaults.
- Change any scripts that use `https://www.gov.il/he/service` to `https://www.gov.il/he/services`.
- Use `bituach-leumi-forms` for forms and `bituach-leumi-certificates` for certificate information.
- Use `tax-authority-public-forms` with focused queries on the income-tax topic page.
- Recreate saved requests if they rely on old source behavior.
- Run `python -m pytest scripts -q` and `python -m compileall scripts/ -q`.
