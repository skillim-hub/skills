# Employee Onboarding Guide

Neutral package for preparing Israeli employee onboarding checklists, document requests, payroll handoffs, and training materials.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start: create a record and use its id

Create a local onboarding record:

```bash
CREATE_RESPONSE=$(employee-onboarding-guide create \
  --name "Dana Levi" \
  --start-date 01-09-2026 \
  --role "Sales Coordinator" \
  --other-employer \
  --active-pension \
  --bank-details-received \
  --employment-notice-status drafted)

RECORD_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

employee-onboarding-guide checklist --id "$RECORD_ID"
employee-onboarding-guide validate --id "$RECORD_ID"
```

The create response contains the local record id and the file path. Use the id in the next command.

## Python import

After `pip install -e .`:

```python
from employee_onboarding_guide_client import EmployeeProfile, create_record, generate_checklist

profile = EmployeeProfile(
    full_name="Dana Levi",
    start_date="01-09-2026",
    role="Sales Coordinator",
    has_other_employer=True,
    has_active_pension=True,
)

response = create_record(profile)
print(response["id"])
print(generate_checklist(profile))
```

## CLI commands

```bash
employee-onboarding-guide create --name "Dana Levi" --start-date 01-09-2026
employee-onboarding-guide checklist --name "Dana Levi" --start-date 01-09-2026
employee-onboarding-guide message --name "דנה לוי" --due-date 25/08/2026 --language he
employee-onboarding-guide sample --path onboarding-sample.json
employee-onboarding-guide validate --path onboarding-sample.json
```

## Environment variables

| Variable | Use |
|---|---|
| `ONBOARDING_DATA_DIR` | Override the local record storage directory. |
| `ONBOARDING_EMPLOYEE_NAME` | Default employee name in example scripts. |
| `ONBOARDING_START_DATE` | Default start date in example scripts. |
| `ONBOARDING_ENV` | Default example environment: `sandbox` or `production`. |

## File index

```text
SKILL.md
SKILL_HE.md
references/api-reference.md
references/workflow-guide.md
references/troubleshooting.md
references/test-scenarios.md
references/migration-checklist.md
references/branding-audit.md
references/hebrew-qa-log.md
references/verification-log.md
scripts/employee_onboarding_guide_client.py
scripts/employee_onboarding_guide_cli.py
scripts/employee-onboarding-guide-cli.py
scripts/test_employee_onboarding_guide_client.py
scripts/examples/
metadata.json
CHANGELOG.md
LICENSE
pyproject.toml
requirements-dev.txt
```

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## Web-validated references

See `references/verification-log.md` for the two-pass source validation performed on 04-06-2026. Recheck official sources before using rates, thresholds, forms, or deadlines in production.

## Data handling

The helper stores records locally. Do not commit real Form 101 files, ID documents, bank details, pension records, or medical documents. Use restricted storage for real employee information.
