# CBS Data Analyzer

A neutral skill package for fetching, normalizing, and explaining Israeli Central Bureau of Statistics data for small-business planning, freelance pricing, consumer checks, and market analysis.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Search the CBS index catalog, extract an index identifier from the JSON response, then use that identifier in the next command:

```bash
cbs-data-analyzer catalog-search "Consumer Price Index" --json > /tmp/cbs-catalog.json
INDEX_ID="$(python - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('/tmp/cbs-catalog.json').read_text(encoding='utf-8'))
first = payload[0] if payload else {"mainCode": 120010}
print(first.get('mainCode') or first.get('code') or 120010)
PY
)"
cbs-data-analyzer fetch-index "$INDEX_ID" --last 6 --limit 6 --json
```

Run the same flow directly in Python:

```python
from cbs_data_analyzer_client import CBSDataAnalyzerClient

with CBSDataAnalyzerClient() as client:
    matches = client.search_catalog("Consumer Price Index")
    index_id = matches[0].get("mainCode") if matches else 120010
    series = client.get_price_index(index_id)

print(series.latest.to_dict() if series.latest else None)
```

Calculate an index-linked rent or contract amount:

```bash
cbs-data-analyzer indexation --amount 5200 --base-index 103.1 --target-index 106.4 --json
```

Run tests and syntax checks:

```bash
pytest scripts/test_cbs_data_analyzer_client.py
python -m compileall scripts/ -q
```

## Runnable examples

Every example accepts `--env sandbox|production`, reads environment variables, and prints JSON using `ensure_ascii=False` and `indent=2`.

```bash
python scripts/examples/01_rent_indexation.py --env sandbox
python scripts/examples/02_cpi_latest.py --env sandbox
python scripts/examples/03_catalog_search.py --env sandbox --query "דירות"
python scripts/examples/04_small_business_market_brief.py --env sandbox
python scripts/examples/05_async_fetch.py --env sandbox
python scripts/examples/06_export_series_csv.py --env sandbox
```

For production calls, optional environment variables are supported:

```bash
export CBS_ENV=production
export CBS_API_BASE_URL=https://api.cbs.gov.il/index
export CBS_DATA_GOV_BASE_URL=https://data.gov.il/api/3/action
# The client sends a User-Agent header by default, as required by CBS API guidance.
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision tree, edge cases, anti-patterns, checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, `₪`, and `DD/MM/YYYY` localization. |
| `references/api-reference.md` | API endpoints, request/response examples, regulation caveats, error table. |
| `references/workflow-guide.md` | End-to-end workflows for rent, pricing, location, suppliers, housing, freelancers, and consumers. |
| `references/troubleshooting.md` | Diagnostic paths and fixes. |
| `references/test-scenarios.md` | Validation scenarios. |
| `references/migration-checklist.md` | Migration from spreadsheets or older helpers. |
| `references/branding-audit.md` | Neutrality and visual-reference audit report. |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance changes and terminology decisions. |
| `references/verification-log.md` | Two-pass web validation of official/API/regulatory claims. |
| `scripts/cbs_data_analyzer_client.py` | Typed synchronous and asynchronous Python client. |
| `scripts/cbs_data_analyzer_cli.py` | Typer CLI. |
| `scripts/test_cbs_data_analyzer_client.py` | Offline pytest suite. |
| `scripts/examples/` | Runnable scenario scripts. |
| `metadata.json` | Skill metadata without creator attribution. |
| `CHANGELOG.md` | Keep-a-Changelog history. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Installable Python project configuration. |
| `requirements-dev.txt` | Development dependencies. |

## Design principles

- Use official CBS sources where possible.
- Show reference periods for every number.
- Treat data as evidence for planning, not as a legal or tax conclusion.
- Keep Hebrew output professional and localized.
- Preserve raw source references for audit-sensitive calculations.
