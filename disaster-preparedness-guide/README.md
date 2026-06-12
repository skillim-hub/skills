# Disaster-Preparedness Guide

A neutral, bilingual emergency-preparedness skill for Israeli households, consumers, freelancers, and small businesses. It summarizes practical Home Front Command-style behavior for common Israeli emergencies and adds business continuity, accessibility, troubleshooting, workflows, test scenarios, and local helper scripts.

Official current instructions override this guide.

## Install

```bash
cd disaster-preparedness-guide
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Look up an emergency protocol:

```bash
disaster-preparedness lookup missile --json
```

Create a household plan, extract the id from the create response, and use that id in the next step:

```bash
CREATE_RESPONSE="$(disaster-preparedness create-household-plan \
  --city Haifa \
  --people 4 \
  --pets \
  --accessibility-needs \
  --env sandbox \
  --output .generated/household-plan.json)"

PLAN_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"

disaster-preparedness review-plan \
  --plan-file .generated/household-plan.json \
  --plan-id "$PLAN_ID" \
  --env sandbox
```

Generate a business plan:

```bash
disaster-preparedness plan-business \
  --city Ashdod \
  --business-type shop \
  --employees 3 \
  --customers-peak 10 \
  --stores-chemicals \
  --env sandbox
```

Run tests:

```bash
pytest
python -m compileall scripts/ -q
```

## Local script alternatives

```bash
python scripts/disaster_preparedness_guide_client.py earthquake --json --env sandbox
python scripts/disaster-preparedness-guide-cli.py lookup "רעידת אדמה" --json --env sandbox
```

## Importable module

```python
from disaster_preparedness_guide import HouseholdProfile, PreparednessClient

client = PreparednessClient(environment="sandbox")
plan = client.household_plan(HouseholdProfile(city="Haifa", people=4, pets=True))
print(plan.plan_id)
```

## Environment variables

Examples and CLI commands accept `--env sandbox|production`. They also read:

| Variable | Purpose |
|---|---|
| `DPG_ENV` | Default environment when `--env` is omitted |
| `DPG_CITY` | Example-script city |
| `DPG_PEOPLE` | Example-script household size |
| `DPG_BUSINESS_TYPE` | Example-script business type |
| `DPG_EMPLOYEES` | Example-script employee count |
| `DPG_CUSTOMERS_PEAK` | Example-script peak customer count |
| `DPG_DAILY_REVENUE_NIS` | Example-script daily revenue baseline |
| `DPG_OUTPUT` | Optional output path for examples that write files |

The helper is intentionally offline. It does not fetch alerts and does not claim access to any official public Home Front Command API.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with decision trees, examples, edge cases, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israel-local terminology, ₪ examples, and DD/MM/YYYY dates |
| `references/api-reference.md` | Non-API official-channel/regulation reference with request/response schemas and error table |
| `references/workflow-guide.md` | End-to-end household, building, business, freelancer, hazmat, pet, and reopening workflows |
| `references/troubleshooting.md` | Troubleshooting and recovery guide |
| `references/test-scenarios.md` | Scenario prompts for validation |
| `references/migration-checklist.md` | Checklist for migrating from older emergency notes/packages |
| `references/branding-audit.md` | Branding, attribution, visual-asset and badge, and emoji audit report |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log |
| `disaster_preparedness_guide/` | Installable Python module |
| `scripts/disaster_preparedness_guide_client.py` | Underscored client entry point |
| `scripts/disaster-preparedness-guide-cli.py` | CLI script wrapper |
| `scripts/test_disaster_preparedness_guide_client.py` | pytest suite with more than 20 tests |
| `scripts/examples/` | Runnable examples that read environment variables and support `--env` |
| `metadata.json` | Skill metadata without attribution field |
| `CHANGELOG.md` | Keep-a-Changelog style release history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Python project, package, and console-script configuration |
| `requirements-dev.txt` | Development and test dependencies |

## Safety and scope

Use this guide for preparedness, training, checklists, and assistant behavior. Do not use it as a live alerting service, legal opinion, engineering approval, medical order, or substitute for official instructions.


## Web validation

Version 2.1.0 adds `references/verification-log.md`, which records live-source validation for emergency numbers, Home Front Command alert behavior, hostile-aircraft alerts, earthquake guidance, tsunami guidance, hazardous-materials guidance, VAT-rate context, hazardous-materials permit notes, and non-API scope.
