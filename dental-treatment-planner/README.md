# Dental Treatment Planner

Offline Israeli dental-treatment planning helper for consumers, freelancers, and small businesses. Estimate treatment sequences, patient cost ranges, benefit assumptions, visit schedules, and provider comparisons for private dentists, Maccabident, Clalit Smile, and other HMO-affiliated dental routes.

This package is a planning aid. Do not treat any output as a diagnosis, medical instruction, binding quote, insurance approval, or legal advice.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create an editable plan, extract the generated id, and use the same id in the next command.

```bash
CREATE_RESPONSE=$(dental-treatment-planner create plan.json --env sandbox --provider private --region center)
echo "$CREATE_RESPONSE"
PLAN_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["plan_id"])' <<< "$CREATE_RESPONSE")
dental-treatment-planner estimate plan.json --plan-id "$PLAN_ID" --env sandbox --markdown
```

Use the Python client after `pip install -e .`:

```python
from dental_treatment_planner import DentalTreatmentPlannerClient, sample_plan

client = DentalTreatmentPlannerClient(environment="sandbox")
plan = sample_plan()
created = client.create_plan(plan, plan_id="case-001")
estimate = client.estimate(created["plan"])
print(estimate.to_markdown())
```


## Verified 2026 defaults

The default VAT simulation rate is 18% when `include_vat=true`. This package does not decide whether a dental invoice is taxable and keeps VAT disabled by default. Provider profiles are planning heuristics; load dated item-level clinic prices before production use.

## CLI commands

```bash
dental-treatment-planner sample
dental-treatment-planner create plan.json --env sandbox
dental-treatment-planner validate plan.json --strict
dental-treatment-planner estimate plan.json --output estimate.json
dental-treatment-planner compare plan.json --providers private,maccabident,clalit_smile
dental-treatment-planner schedule plan.json
dental-treatment-planner catalog list
dental-treatment-planner catalog export catalog.csv
```

## Environment variables for examples

Runnable examples under `scripts/examples/` read optional environment variables and also accept `--env sandbox|production`.

```bash
DTP_ENV=sandbox DTP_PROVIDER=maccabident DTP_REGION=center python scripts/examples/consumer_routine_compare.py --env sandbox
DTP_START_DATE=15/07/2026 DTP_TOOTH=46 python scripts/examples/urgent_root_canal.py --env sandbox
```

All examples print JSON with `ensure_ascii=False` and `indent=2`.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, troubleshooting, anti-patterns, checklist |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology, ₪ formatting, and DD/MM/YYYY dates |
| `references/api-reference.md` | Offline reference contracts, local data import shape, request and response examples, error tables |
| `references/workflow-guide.md` | End-to-end workflows for consumers, freelancers, and small businesses |
| `references/troubleshooting.md` | Diagnostic guide for common planning, coverage, and scheduling issues |
| `references/test-scenarios.md` | More than 20 concrete scenarios for validation and regression testing |
| `references/migration-checklist.md` | Migration steps from spreadsheets, ad hoc quotes, or earlier package layouts |
| `references/branding-audit.md` | Audit results for branding, authorship, visual assets, and emoji cleanup |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `references/verification-log.md` | Two-pass live-source verification log for VAT, eligibility, provider benefits, terminology, and API assumptions |
| `dental_treatment_planner/` | Installable Python package |
| `scripts/dental_treatment_planner_client.py` | Structured client helper for checkout-based execution |
| `scripts/dental-treatment-planner-cli.py` | Development CLI wrapper |
| `scripts/test_dental_treatment_planner_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## Safety boundaries

Use this tool to organize information before requesting binding documentation from a licensed dentist or clinic. Require professional confirmation for diagnosis, treatment necessity, imaging interpretation, medication, sedation, emergency care, insurance eligibility, and tax treatment. Replace default catalog ranges with dated local source data before production use.
