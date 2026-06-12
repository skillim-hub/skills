# Troubleshooting

## Quick checks

Run these commands before deeper investigation:

```bash
forms-certificates-downloader list-sources --json-output
python -m pytest scripts -q
python -m compileall scripts/ -q
```

## No matching documents found

Likely causes:

- Query is too specific.
- Portal page loads links dynamically.
- The source points to a landing page rather than a document index.
- The document exists only inside a personal area.

Actions:

1. Run discovery without a query and with a small limit.
2. Replace the source with a more focused public page.
3. Search by Hebrew topic, form number, and year separately.
4. Stop automation if the path requires login.

## Unknown source

Cause: source name does not exist in the registry loaded by the command.

Actions:

```bash
forms-certificates-downloader list-sources --registry data/portal-registry.json
```

Confirm spelling and environment. Add the source if needed.

## Fetch failure

Typical signals:

- HTTP error.
- Timeout.
- Unsupported scheme.
- Network failure.

Actions:

1. Open the URL manually.
2. Confirm the URL is public.
3. Retry with a smaller source and limit.
4. Use a local fixture when testing parsing.
5. Do not bypass access controls.

## Parse failure

Cause: the source response is not an HTML page with document links and is not a direct document URL.

Actions:

- Use an official HTML index page.
- Use a direct public document URL as source.
- Avoid pages that rely on logged-in session state.
- Avoid broad search pages with client-side rendering only.

## Hebrew file names look wrong in spreadsheet output

Use the CSV exported by `export-csv`; it is written as UTF-8 with BOM for spreadsheet compatibility. If a spreadsheet still displays unreadable text, import the file as UTF-8 rather than opening it by double-click.

## Checksum changed

A changed SHA-256 means the bytes changed. It does not explain why. Possible reasons:

- The authority published a new version.
- The authority replaced a file without updating the title.
- Metadata inside a generated PDF changed.
- The old URL now serves another file.

Actions:

1. Open the source page manually.
2. Compare visible version, title, and date.
3. Keep both previous and current files under retention rules.
4. Add a review note outside the manifest.

## Request id not found

Saved requests live under `<download_dir>/requests`. Use the same download directory for `create-request` and `run-request`.

Correct chain:

```bash
CREATE_RESPONSE=$(forms-certificates-downloader create-request tax-authority-public-forms \
  --query "1301" --limit 5 --download-dir ./downloads --json-output)
REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$CREATE_RESPONSE")
forms-certificates-downloader run-request "$REQUEST_ID" --download-dir ./downloads --json-output
```

## Network-free debugging

Use `scripts/examples/offline_fixture_scan.py` with `--env sandbox`. The fixture creates a local public HTML page and a local PDF, then runs discovery, download, and tracking without internet access.

## Escalation checklist

- Preserve command line, registry entry, manifest snippet, and error text.
- Confirm whether the URL is public.
- Confirm whether a direct document link exists in HTML.
- Confirm whether the issue reproduces with a `file://` fixture.
- Confirm package syntax with `compileall`.


## Bituach Leumi search page is inactive

Signal: the search page says `זמנית החיפוש אינו פעיל`.

Actions:

- Use the dedicated forms category source `bituach-leumi-forms`.
- Use `bituach-leumi-certificates` for public certificate information.
- Search by Hebrew category name, form number, or certificate title.
- Keep personal certificate printing inside the official personal service site.
