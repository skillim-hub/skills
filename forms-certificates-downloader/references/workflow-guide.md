# Workflow Guide

## Workflow 1: Annual income-tax form refresh for a freelancer

Goal: download current public income-tax forms and store an auditable manifest.

1. Install the package.

```bash
pip install -e .
pip install -r requirements-dev.txt
```

2. Create a focused request.

```bash
CREATE_RESPONSE=$(forms-certificates-downloader create-request tax-authority-public-forms \
  --query "1301" \
  --limit 5 \
  --env production \
  --download-dir ./downloads/tax-annual \
  --json-output)
REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$CREATE_RESPONSE")
```

3. Run the request.

```bash
forms-certificates-downloader run-request "$REQUEST_ID" \
  --env production \
  --download-dir ./downloads/tax-annual \
  --json-output
```

4. Open each changed file and verify the authority page manually.

5. Export the register.

```bash
forms-certificates-downloader export-csv ./downloads/tax-annual/register.csv \
  --download-dir ./downloads/tax-annual
```

Acceptance criteria:

- `manifest.json` exists.
- Every downloaded file has a SHA-256 checksum.
- CSV opens correctly with Hebrew titles.
- Manual review notes are stored outside the manifest if required.

## Workflow 2: National Insurance public form tracking

Goal: monitor public forms related to a benefit topic without accessing personal areas.

```bash
forms-certificates-downloader download bituach-leumi-forms \
  --query "דמי לידה" \
  --limit 10 \
  --env production \
  --download-dir ./downloads/bituach-leumi \
  --json-output
```

Review each `added` or `updated` entry. Do not treat public form availability as benefit eligibility.

## Workflow 3: Consumer document preparation before a government appointment

Goal: find public service forms by topic.

```bash
forms-certificates-downloader discover gov-il-services \
  --query "שינוי כתובת" \
  --max-results 10 \
  --env production \
  --download-dir ./downloads/consumer \
  --json-output
```

If the service page requires login, stop automation and continue manually.

## Workflow 4: Corporation or nonprofit public forms

Goal: maintain a local reference folder for public registry forms.

```bash
forms-certificates-downloader download corporations-authority \
  --query "עמותה" \
  --limit 10 \
  --env production \
  --download-dir ./downloads/corporations
```

Store downloaded public forms separately from private corporate filings.

## Workflow 5: Offline acceptance test for a new source

Goal: validate parsing and tracking without network access.

1. Create fixture HTML with direct links to local files.
2. Create a custom registry JSON that points to the fixture page.
3. Run discovery.

```bash
forms-certificates-downloader discover fixture \
  --registry ./fixture-registry.json \
  --env sandbox \
  --download-dir ./downloads/fixture \
  --json-output
```

4. Run tests.

```bash
python -m pytest scripts -q
```

## Workflow 6: Month-end evidence pack

Goal: freeze evidence for bookkeeping review.

1. Run the relevant saved requests.
2. Export CSV from each download directory.
3. Copy `manifest.json`, CSV, and changed files into a dated review folder.
4. Use DD-MM-YYYY folder names for local review, for example `02-06-2026`.
5. Store private customer files outside this package unless access controls are defined.

## Workflow 7: Registry change review

Goal: update a source after an official portal reorganizes pages.

1. Open the old source URL manually.
2. Locate the new public index page.
3. Update `data/portal-registry.json`.
4. Run discovery with `--max-results 3`.
5. Compare document titles and URLs against the previous manifest.
6. Commit only the registry change and a short operational note.

## Decision points

| Question | Decision |
|---|---|
| Does the page require login | Keep it manual. |
| Does the page list public files directly | Add or use registry source. |
| Does discovery return too many results | Add a query and reduce limit. |
| Did checksum change | Review the file and source page manually. |
| Does a document contain private data | Move it outside the shared public download directory. |


## Workflow 8: Web validation before registry changes

Goal: avoid stale public portal paths.

1. Search the exact current URL and the authority name in Hebrew.
2. Search the same authority with a different query or language.
3. Record both sources in `references/verification-log.md`.
4. Update both `data/portal-registry.json` and `forms_certificates_downloader/data/portal-registry.json`.
5. Run tests and syntax checks.

Acceptance criteria:

- Every changed URL has two source checks.
- Every corrected row is tagged `✗→✓` in the verification log.
- The summary table has zero final failures.
