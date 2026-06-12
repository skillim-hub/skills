# Real-Estate Search Assistant

Create structured Israeli real-estate search plans for Yad2, Madlan, and Komo. Use the package to translate buyer, renter, freelancer, or small-business requirements into source-specific links, neighborhood-aware manual review, checklists, comparison scoring, and CLI workflows.

This package does not claim private access to listing databases. It builds source-specific search links, normalizes requirements, and supports manual verification without bypassing access controls, paywalls, terms, or rate limits.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a plan and save the response:

```bash
real-estate-search create \
  --city "חיפה" \
  --deal-type rent \
  --neighborhoods "בת גלים,כרמליה" \
  --max-price 5200 \
  --min-rooms 2.5 \
  --output plan.json
```

Extract the plan id from the create response, then use it in the next step:

```bash
PLAN_ID=$(python -c "import json; print(json.load(open('plan.json', encoding='utf-8'))['plan_id'])")
real-estate-search show --file plan.json --plan-id "$PLAN_ID"
```

Use Python after installation:

```python
from real_estate_search import RealEstateSearchClient, SearchCriteria

client = RealEstateSearchClient("sandbox")
criteria = SearchCriteria(
    city="רמת גן",
    deal_type="rent",
    neighborhoods=("מרום נווה", "הראשונים"),
    max_price=8500,
    min_rooms=3.5,
    parking=True,
)
plan = client.build_search_plan(criteria)
print(plan.to_json())
```

## Environment variables

Examples and automation scripts read these variables when present:

| Variable | Purpose | Example |
| --- | --- | --- |
| `REAL_ESTATE_SEARCH_ENV` | `sandbox` or `production` | `sandbox` |
| `REAL_ESTATE_SEARCH_CITY` | Default city | `חיפה` |
| `REAL_ESTATE_SEARCH_NEIGHBORHOODS` | Comma-separated neighborhoods | `בת גלים,כרמליה` |
| `REAL_ESTATE_SEARCH_MAX_PRICE` | Maximum price in ₪ | `5200` |
| `REAL_ESTATE_SEARCH_MIN_ROOMS` | Minimum rooms | `2.5` |
| `REAL_ESTATE_SEARCH_DEAL_TYPE` | Search mode | `rent` |
| `REAL_ESTATE_SEARCH_TIMEOUT` | Optional HTTP timeout for link checks | `10` |

## File index

| Path | Purpose |
| --- | --- |
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, and checklist. |
| `SKILL_HE.md` | Hebrew operating guide localized for Israeli users. |
| `references/api-reference.md` | Source, regulation, schema, and error reference for non-API listing workflows. |
| `references/workflow-guide.md` | End-to-end workflows for consumers, freelancers, and small businesses. |
| `references/troubleshooting.md` | Common failures, diagnostics, and safe recovery steps. |
| `references/test-scenarios.md` | More than 20 concrete test scenarios. |
| `references/migration-checklist.md` | Migration checklist from ad-hoc or earlier package workflows. |
| `references/branding-audit.md` | Branding and visual-mark audit report. |
| `references/hebrew-qa-log.md` | Hebrew quality assurance log. |
| `references/verification-log.md` | Web validation log with two-pass source checks. |
| `src/real_estate_search/` | Installable Python package. |
| `scripts/real_estate_search_client.py` | Underscored client import entry for script users. |
| `scripts/real-estate-search-cli.py` | Direct CLI wrapper. |
| `scripts/examples/` | Runnable scenario scripts. |
| `scripts/test_real_estate_search_client.py` | Pytest suite. |

## Run checks

```bash
pytest
python -m compileall scripts/ -q
```

## Safety and compliance

Use generated links manually. Yad2 and Madlan expose visible neighborhood controls; Komo city pages expose neighborhood labels in listings, so apply neighborhood filtering manually unless a verified neighborhood id is available. Do not scrape at volume, bypass access controls, reuse personal data without a lawful basis, or treat listing text as verified fact. Confirm rights, taxes, planning, lease terms, broker status, and business licensing through official sources and licensed professionals where needed.
