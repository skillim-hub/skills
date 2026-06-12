# Data.gov.il Explorer

Neutral skill package for retrieving, inspecting, querying, exporting, and analyzing public Israeli open-government datasets from data.gov.il through the CKAN API.

Use it for practical questions from small businesses, freelancers, and consumers: public transport checks, education data, city-level due diligence, government table exports, and repeatable evidence packs.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Verify the import surface:

```bash
python - <<'PY'
from datagovil_explorer import DatagovClient
print(DatagovClient().__class__.__name__)
PY
```

## Quick start

Create a search response file, extract the dataset id from that response, then use it in the next request.

```bash
datagovil-explorer search "תחבורה ציבורית" --rows 3 --json-output > create-response.json
DATASET_ID=$(python - <<'PY'
import json
with open("create-response.json", encoding="utf-8") as handle:
    payload = json.load(handle)
print(payload["results"][0]["name"])
PY
)
datagovil-explorer dataset "$DATASET_ID" --json-output > dataset.json
RESOURCE_ID=$(python - <<'PY'
import json
with open("dataset.json", encoding="utf-8") as handle:
    payload = json.load(handle)
print(next(item["id"] for item in payload.get("resources", []) if item.get("id")))
PY
)
datagovil-explorer resource "$RESOURCE_ID" --json-output
```

Python quick start:

```python
from datagovil_explorer import DatagovClient, extract_first_dataset_id, extract_first_resource_id

client = DatagovClient()
search = client.package_search("תחבורה ציבורית", rows=3)
dataset_id = extract_first_dataset_id(search)
dataset = client.package_show(dataset_id)
resource_id = extract_first_resource_id(dataset)
print(dataset_id, resource_id)
```

## Environment selection

The production default is `https://data.gov.il/api/3`. The `sandbox` selector is not an official data.gov.il sandbox; it is a safe switch for a user-provided CKAN-compatible endpoint during tests.

Configure an alternate endpoint when testing:

```bash
export DATAGOVIL_SANDBOX_BASE_URL="https://example.test/api/3"
datagovil-explorer --env sandbox search "חינוך" --rows 2 --json-output
```

| Environment | Variables checked in order |
|---|---|
| production | `DATAGOVIL_BASE_URL`, `DATAGOVIL_PRODUCTION_BASE_URL` |
| sandbox | `DATAGOVIL_SANDBOX_BASE_URL`, `DATAGOVIL_BASE_URL_SANDBOX` |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operational guide with examples, decision trees, anti-patterns, and checklist |
| `SKILL_HE.md` | Hebrew operational guide with Israeli terminology and DD/MM/YYYY examples |
| `references/api-reference.md` | CKAN endpoint reference, legal considerations, request and response examples |
| `references/workflow-guide.md` | End-to-end workflows for businesses, freelancers, and consumers |
| `references/troubleshooting.md` | Failure modes, diagnostics, and recovery steps |
| `references/test-scenarios.md` | More than 20 concrete test and acceptance scenarios |
| `references/migration-checklist.md` | Migration steps from older scripts or older layouts |
| `references/branding-audit.md` | Branding and provenance audit results |
| `references/hebrew-qa-log.md` | Hebrew correction log and terminology choices |
| `references/verification-log.md` | Two-pass web validation log with official sources, snippets, and correction status |
| `datagovil_explorer/` | Installable Python package |
| `scripts/datagovil_explorer_client.py` | Standalone typed sync and async client copy |
| `scripts/datagovil_explorer_cli.py` | Runnable CLI wrapper |
| `scripts/examples/` | Runnable scenario scripts |
| `scripts/test_datagovil_explorer_client.py` | Pytest suite |

## Common commands

```bash
datagovil-explorer search "רישוי עסקים" --rows 5
datagovil-explorer first-dataset-id "תחבורה ציבורית"
datagovil-explorer dataset DATASET_ID --json-output
datagovil-explorer first-resource-id DATASET_ID
datagovil-explorer query RESOURCE_ID --limit 20 --filter "שם_ישוב=חיפה" --json-output
datagovil-explorer export RESOURCE_ID --out output.csv --max-records 500
```

## Development checks

```bash
python -m compileall scripts/ -q
pytest
```

## Practical cautions

Inspect publisher, metadata update date, resource format, datastore status, fields, and sample rows before drawing a business conclusion. Treat public datasets as evidence to validate, not as a substitute for professional tax, privacy, planning, consumer, or licensing advice. For current statutory rates such as VAT, consult the relevant official source at decision time and record the access date.
