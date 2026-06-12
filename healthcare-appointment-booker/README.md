# Healthcare Appointment Booker

Neutral skill package for planning and supporting healthcare appointment booking in Israel through official HMO channels.

## What it does

- Routes appointment requests for Clalit, Maccabi, Meuhedet, and Leumit.
- Handles primary care, specialists, imaging, labs, nursing, urgent-care routing, and administrative approvals.
- Provides English and Hebrew guides.
- Includes an importable Python module, Typer CLI, examples, and pytest coverage.
- Avoids credential capture, portal scraping, and diagnosis.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained create and show

Create a plan and save the response:

```bash
python -m healthcare_appointment_booker.cli create \
  --hmo maccabi \
  --service "skin mole check" \
  --city "Rishon LeZion" \
  --date-from 2026-07-01 \
  --date-to 2026-07-31 \
  --referral-status unknown \
  --urgency routine \
  --store ./plans.json > create-response.json
```

Extract the id from the create response:

```bash
PLAN_ID=$(python -c 'import json; print(json.load(open("create-response.json", encoding="utf-8"))["id"])')
```

Use that id in the next step:

```bash
python -m healthcare_appointment_booker.cli show \
  --id "$PLAN_ID" \
  --store ./plans.json \
  --format text
```

## Direct CLI plan

```bash
python -m healthcare_appointment_booker.cli plan \
  --hmo clalit \
  --service "כאב אוזניים וחום לילד" \
  --city "חיפה" \
  --age-group child \
  --urgency same_day \
  --date-from 01/07/2026 \
  --date-to 05/07/2026 \
  --language he \
  --format text
```

## Python import

```python
from healthcare_appointment_booker import HealthcareAppointmentBookerClient, build_request

request = build_request(
    hmo="maccabi",
    service="dermatology skin mole check",
    city="Rishon LeZion",
    date_from="2026-07-01",
    date_to="2026-07-31",
    referral_status="unknown",
)

plan = HealthcareAppointmentBookerClient().plan(request)
print(plan.to_json())
```

The compatibility module also works:

```python
from healthcare_appointment_booker_client import HealthcareAppointmentBookerClient
```

## Examples

Each example reads environment variables, accepts `--env sandbox` or `--env production`, and prints JSON with Hebrew preserved.

```bash
HAB_HMO=maccabi HAB_CITY="Rishon LeZion" python scripts/examples/specialist_with_referral.py --env sandbox
HAB_HMO=meuhedet HAB_CITY="Jerusalem" python scripts/examples/imaging_mri.py --env production
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | Full English operating guide. |
| `SKILL_HE.md` | Full Hebrew operating guide with Israeli localization. |
| `references/api-reference.md` | Israeli official-channel, privacy, and workflow reference. |
| `references/workflow-guide.md` | End-to-end appointment workflows. |
| `references/troubleshooting.md` | Operational troubleshooting guide. |
| `references/test-scenarios.md` | Concrete validation scenarios. |
| `references/migration-checklist.md` | Migration checklist for older assistants/processes. |
| `references/branding-audit.md` | Branding and attribution audit summary. |
| `references/hebrew-qa-log.md` | Hebrew localization review log. |
| `references/verification-log.md` | Two-pass web validation log with official sources. |
| `healthcare_appointment_booker_client.py` | Typed sync and async workflow client. |
| `healthcare_appointment_booker/` | Installable package and CLI module. |
| `scripts/healthcare_appointment_booker_cli.py` | Script wrapper for CLI execution. |
| `scripts/examples/` | Runnable scenario examples. |
| `scripts/test_healthcare_appointment_booker_client.py` | Pytest suite with more than 20 tests. |
| `metadata.json` | Skill metadata without attribution fields. |
| `CHANGELOG.md` | Keep a Changelog format. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Python project config. |
| `requirements-dev.txt` | Development dependencies. |

## Safety boundary

This package supports administrative appointment booking only. It does not provide medical diagnosis, does not guarantee appointment availability, and does not replace official HMO channels.

Never collect:

- HMO passwords.
- SMS verification codes.
- Full ID numbers.
- Medical files unless handled through official secure upload channels.
- Unnecessary medical details.

## Development

```bash
pytest -q
python -m compileall scripts/ -q
python scripts/examples/routine_family_doctor.py --env sandbox
python scripts/examples/specialist_with_referral.py --env sandbox
python scripts/examples/imaging_mri.py --env sandbox
python scripts/examples/no_slots_fallback.py --env sandbox
python scripts/examples/hebrew_business_client.py --env sandbox
```
