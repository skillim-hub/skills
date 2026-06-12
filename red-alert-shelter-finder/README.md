# Red-Alert & Shelter Finder

Neutral package for checking Home Front Command alert payloads through configurable sources and finding nearest public shelters from configured local or municipal datasets.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a locality watch, extract the returned `watch_id`, and use it in the next command:

```bash
CREATE_RESPONSE=$(red-alert-shelter-finder create-watch --env sandbox --area "חיפה" --output .watch-haifa.json)
WATCH_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["watch_id"])' <<< "$CREATE_RESPONSE")
red-alert-shelter-finder check-watch --env sandbox --watch-id "$WATCH_ID" --watch-file .watch-haifa.json
```

Check active alerts directly:

```bash
red-alert-shelter-finder alerts --env sandbox --area "חיפה"
```

Find nearest shelters from CSV:

```bash
red-alert-shelter-finder nearest --env sandbox --lat 32.074 --lon 34.779 --shelters scripts/examples/sample_shelters.csv --limit 5
```

Generate a business procedure:

```bash
red-alert-shelter-finder business-procedure --env sandbox --city "אשדוד" --business-type "restaurant" --staff 8 --customers --deliveries
```

Run tests and syntax checks:

```bash
pytest -q
python -m compileall scripts/ -q
```

## Python import

```python
from red_alert_shelter_finder import RedAlertShelterFinderClient

client = RedAlertShelterFinderClient()
```

## Environment variables

| Variable | Use |
|---|---|
| `RED_ALERT_ALERTS_URL` | Override the production alert endpoint |
| `RED_ALERT_SANDBOX_ALERTS_FILE` | Read sandbox alert payload from a local JSON file |
| `RED_ALERT_PRODUCTION_ALERTS_FILE` | Read production-like alert payload from a local JSON file |
| `RED_ALERT_SHELTERS_FILE` | Default shelter dataset path for examples |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | API, data, and regulation reference |
| `references/workflow-guide.md` | End-to-end operational workflows |
| `references/troubleshooting.md` | Detailed troubleshooting guide |
| `references/test-scenarios.md` | Concrete test and release scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding, author, logo, and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance log |
| `src/red_alert_shelter_finder/client.py` | Typed sync and async client |
| `src/red_alert_shelter_finder/cli.py` | Click CLI module |
| `scripts/red_alert_shelter_finder_client.py` | Compatibility import script |
| `scripts/red_alert_shelter_finder_cli.py` | CLI runner script |
| `scripts/test_red_alert_shelter_finder_client.py` | pytest suite |
| `scripts/examples/` | Runnable examples |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Python packaging and test config |
| `requirements-dev.txt` | Development dependencies |

## Data note

The client supports live alert fetches through a configurable endpoint and local shelter lookup through CSV, JSON, or GeoJSON. Public shelter datasets vary by municipality. Validate dataset freshness, coordinate format, and access or opening status before production use.

## Safety note

During an alarm, enter the nearest protected space immediately and follow official Home Front Command and municipal instructions.


## Web-validated notes

- Official Home Front Command channels provide alerts and life-saving information in real time through the official app and National Emergency Portal.
- The bundled client keeps the alert endpoint configurable because no official public API contract for `alerts.json` was confirmed.
- Shelter lookup depends on the configured dataset. Municipal shelter pages confirm public shelter lists, but coverage and opening status remain source-dependent.
- The package does not calculate VAT. If business-cost examples are extended, verify current VAT before using a rate.
