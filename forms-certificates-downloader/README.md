# Forms & Certificates Downloader

Neutral Python package and skill guide for locating, downloading, and version-tracking public Israeli government forms and certificates.

The package helps small businesses, freelancers, bookkeepers, payroll teams, and consumers maintain an auditable local register of public official documents from portals such as gov.il, the Israel Tax Authority, the National Insurance Institute, ministry pages, and public registry pages.

## Scope

Use this package for public pages that do not require login. Keep personal-area actions manual.

Supported tasks:

- Discover public document links from an official index page.
- Download PDF, Word, Excel, CSV, and ZIP files.
- Compute SHA-256 checksums.
- Write a manifest with source URL, document URL, timestamp, local path, file size, and version hint.
- Report added, updated, and unchanged documents.
- Save a download request, extract its request id, and run the saved request later.
- Validate Israeli identity numbers, phone numbers, and seven-digit postal codes.
- Run offline fixture tests without network access.

Excluded tasks:

- Login to personal government areas.
- Bypass CAPTCHA, one-time password, smart-card, biometric, or queue controls.
- Submit forms or sign declarations.
- Download private certificates.
- Provide tax, legal, accounting, payroll, or benefit advice.

## Installation

From the extracted package directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
```

## Quick start with chained request id

Create a saved request. The command returns JSON containing a `request_id`.

```bash
CREATE_RESPONSE=$(forms-certificates-downloader create-request tax-authority-public-forms \
  --query "1301" \
  --limit 5 \
  --env production \
  --download-dir ./downloads \
  --json-output)
```

Extract the id from the create response.

```bash
REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$CREATE_RESPONSE")
```

Use that id in the next step.

```bash
forms-certificates-downloader run-request "$REQUEST_ID" \
  --env production \
  --download-dir ./downloads \
  --json-output
```

View the manifest:

```bash
forms-certificates-downloader manifest --download-dir ./downloads --json-output
```

Export the register for bookkeeping review:

```bash
forms-certificates-downloader export-csv ./downloads/forms-register.csv --download-dir ./downloads
```

## Direct Python use

```python
from forms_certificates_downloader import FormsCertificatesClient

client = FormsCertificatesClient(download_dir="downloads", env="production")
records = client.discover("bituach-leumi-forms", query="דמי לידה", max_results=10)
downloaded = [client.download(record) for record in records]
changes = client.track_records(downloaded)

for change in changes:
    print(change.status, change.title)
```

Async use:

```python
import asyncio
from forms_certificates_downloader import FormsCertificatesClient

async def main():
    client = FormsCertificatesClient(download_dir="downloads", env="production")
    records, changes = await client.async_refresh_source("tax-authority-public-forms", query="1301", max_results=3)
    return records, changes

records, changes = asyncio.run(main())
```

## Environment variables used by examples

The example scripts read these optional variables:

```bash
export FORMS_DOWNLOADER_ENV=sandbox
export FORMS_DOWNLOADER_DOWNLOAD_DIR=example-downloads
export FORMS_DOWNLOADER_QUERY="1301"
export FORMS_DOWNLOADER_LIMIT=5
export FORMS_DOWNLOADER_REGISTRY=data/portal-registry.json
```

Each example also accepts `--env sandbox` or `--env production`.

## File index

```text
forms_certificates_downloader/
  __init__.py
  client.py
  cli.py
  data/
    portal-registry.json
data/
  portal-registry.json
scripts/
  forms_certificates_downloader_client.py
  forms_certificates_downloader_cli.py
  test_forms_certificates_downloader_client.py
  examples/
    check_registry.py
    download_tax_forms.py
    track_bituach_leumi_certificate.py
    download_gov_service_forms.py
    export_manifest.py
    offline_fixture_scan.py
references/
  api-reference.md
  workflow-guide.md
  troubleshooting.md
  test-scenarios.md
  migration-checklist.md
  branding-audit.md
  hebrew-qa-log.md
  verification-log.md
SKILL.md
SKILL_HE.md
README.md
CHANGELOG.md
LICENSE
metadata.json
pyproject.toml
requirements-dev.txt
```

## Default public sources after web validation

The default registry uses the current public Tax Authority department page, the current income-tax topic page, dedicated National Insurance forms and certificates pages, the plural gov.il services index, and the current Corporations Authority department page. See `references/verification-log.md` for the two-pass source audit.

## Registry

Edit `data/portal-registry.json` to add public official sources. Review `references/verification-log.md` before changing a default URL. Prefer official public index pages and small focused queries. Avoid authenticated pages and pages with anti-automation controls.

A registry entry uses this shape:

```json
{
  "name": "tax-authority-public-forms",
  "authority": "Israel Tax Authority",
  "index_url": "https://www.gov.il/he/departments/topics/income_tax_israel_tax_authority",
  "base_url": "https://www.gov.il",
  "portal_type": "public-index",
  "language": "he",
  "tags": ["tax", "income-tax", "forms"],
  "notes": "Public index only. Authenticated filing remains manual."
}
```

## Operational notes

Use version tracking for repeatable evidence. Keep the manifest under ordinary backup. When a downloaded file changes checksum, open the source page manually and confirm whether the authority published a new version, reorganized links, or replaced a file without a visible version label.
