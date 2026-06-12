# Business Registration Assistant

A neutral skill package for preparing Israeli self-employed business registration as **עוסק פטור** or **עוסק מורשה**. The package helps gather documents, classify likely VAT status, plan filings with the Israel Tax Authority and Bituach Leumi, and produce structured checklists for users or accountants.

## What this package includes

- English and Hebrew skill guides.
- Israeli regulatory and API-style reference.
- Workflow guide for common registration paths.
- Troubleshooting guide.
- Migration checklist for moving from עוסק פטור to עוסק מורשה.
- Test scenarios.
- Installable Python package.
- Underscored script client.
- Typer-based CLI.
- Runnable examples.
- Pytest suite with more than 20 tests.

## Installation for local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Run a direct status classification:

```bash
bra-registration classify \
  --activity "Private English tutoring" \
  --turnover 72000 \
  --profit 5000 \
  --ceiling 122833
```

Create a local planning case, extract the returned id, and use it in the next step:

```bash
CREATE_RESPONSE="$(bra-registration case-create \
  --input scripts/examples/intake_tutor.json \
  --case-store /tmp/business-registration-cases.json)"

CASE_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"

bra-registration case-plan \
  --case-id "$CASE_ID" \
  --case-store /tmp/business-registration-cases.json
```

Build a checklist:

```bash
bra-registration checklist \
  --status osek_patur \
  --work-location home \
  --foreign-clients
```

Run a full plan from JSON:

```bash
bra-registration plan --input scripts/examples/intake_tutor.json
```

Use the module from Python:

```python
from business_registration_assistant import BusinessIntake, BusinessRegistrationClient

client = BusinessRegistrationClient()
intake = BusinessIntake(
    activity_description="Private English tutoring",
    expected_annual_turnover_nis=72000,
    expected_monthly_profit_nis=5000,
    current_osek_patur_ceiling_nis=122833,
)
print(client.build_full_plan(intake).to_dict())
```

Run tests and syntax checks:

```bash
pytest -q
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | Comprehensive English guide. |
| `SKILL_HE.md` | Comprehensive Hebrew guide. |
| `business_registration_assistant/` | Installable Python package. |
| `references/api-reference.md` | Official-source and structured API-style reference. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Troubleshooting playbook. |
| `references/test-scenarios.md` | Validation scenarios. |
| `references/migration-checklist.md` | עוסק פטור to עוסק מורשה migration. |
| `references/branding-audit.md` | Branding, author, logo, and emoji audit. |
| `references/hebrew-qa-log.md` | Hebrew quality assurance change log. |
| `scripts/business_registration_assistant_client.py` | Underscored script client. |
| `scripts/business-registration-assistant-cli.py` | CLI wrapper. |
| `scripts/test_business_registration_assistant_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable scenario scripts. |
| `metadata.json` | Skill metadata. |
| `CHANGELOG.md` | Keep-a-Changelog history. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Package and tooling configuration. |
| `requirements-dev.txt` | Development dependencies. |

## Compliance note

This package does not submit registrations to any government authority. It prepares structured guidance and checklists. Verify current thresholds, rates, forms, and occupation restrictions with official sources or a licensed professional before filing.
