# Advertising Campaign Planner

Plan Israeli advertising campaigns for small businesses, freelancers, and consumer-facing services. Produce audience segments, channel allocation, multilingual creative guidance, compliance checks, and ROI estimates for campaigns in Hebrew, Arabic, Russian, and English.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with create/show chain

Create a plan, extract the returned `plan_id`, then use that identifier in the next command:

```bash
CREATE_RESPONSE="$(python scripts/advertising-campaign-planner-cli.py create \
  --business "רואה חשבון עצמאי" \
  --goal leads \
  --monthly-budget 6000 \
  --avg-order-value 2400 \
  --gross-margin 0.70 \
  --language he \
  --language ru \
  --city "פתח תקווה" \
  --regulated-flag tax_advice \
  --state-file planner-state.json)"

PLAN_ID="$(printf '%s' "$CREATE_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["plan_id"])')"

python scripts/advertising-campaign-planner-cli.py show \
  --plan-id "$PLAN_ID" \
  --state-file planner-state.json
```

Generate a one-off JSON plan without saving state:

```bash
python scripts/advertising-campaign-planner-cli.py plan \
  --business "family dental clinic" \
  --goal bookings \
  --monthly-budget 12000 \
  --avg-order-value 1800 \
  --gross-margin 0.62 \
  --language he \
  --language ar \
  --city "Haifa" \
  --env sandbox \
  --output campaign-plan.json
```

Estimate ROI from known metrics:

```bash
python scripts/advertising-campaign-planner-cli.py estimate-roi \
  --spend 4500 \
  --clicks 1800 \
  --conversions 54 \
  --avg-order-value 350 \
  --gross-margin 0.48
```

Use the package from Python after installation:

```python
from advertising_campaign_planner import CampaignPlanner, CampaignRequest

planner = CampaignPlanner()
request = CampaignRequest(
    business="Local plumber",
    goal="calls",
    monthly_budget=3000,
    languages=["he"],
    cities=["Holon"],
)
print(planner.plan(request).to_json())
```

Run tests and syntax checks:

```bash
pytest
python -m compileall scripts/ -q
```

## Environment variables

| Variable | Purpose |
|---|---|
| `AD_PLANNER_STATE_FILE` | Default state file for `create` and `show` commands |
| `AD_PLANNER_DEFAULT_CITY` | Default city used by example scripts |
| `AD_PLANNER_DEFAULT_BUDGET` | Default budget used by example scripts |
| `AD_PLANNER_ENV` | Default example environment: `sandbox` or `production` |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, compliance checklist, anti-patterns |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology, ₪ formatting, and DD/MM/YYYY dates |
| `advertising_campaign_planner/` | Installable Python package |
| `references/api-reference.md` | Israeli regulatory/API reference, request/response formats, validation and error tables |
| `references/workflow-guide.md` | End-to-end campaign planning workflows |
| `references/troubleshooting.md` | Diagnosis and fixes for planning, compliance, and measurement problems |
| `references/test-scenarios.md` | Concrete scenarios for validation and QA |
| `references/migration-checklist.md` | Migration checklist for replacing old or branded packages |
| `references/branding-audit.md` | Neutrality, attribution, visual-reference, and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `scripts/advertising_campaign_planner_client.py` | Importable client wrapper |
| `scripts/advertising-campaign-planner-cli.py` | Full Typer CLI wrapper |
| `scripts/examples/` | Runnable scenario scripts |
| `pyproject.toml` | Package and tooling configuration |
| `requirements-dev.txt` | Development and test dependencies |

## Scope and caution

Use this package for operational planning. Advertising, privacy, accessibility, tax, and consumer-protection rules can change. Verify current Israeli legal requirements with qualified counsel or the relevant authority before launch, especially for regulated fields, promotions, health claims, financial services, alcohol, minors, lotteries, and personal-data processing.


## Web-validated v3 notes

The package treats VAT as 18% from 01/01/2025, corrects regulator terminology away from a single general advertising authority, and documents that no Israeli government API endpoint or webhook event is used by the local planner. See `references/verification-log.md` for source-by-source validation.
