# Passport & ID Appointment Scheduler

Neutral skill package for planning Israeli Population and Immigration Authority appointments for passports, Teudat Zehut identity cards, biometric documentation, address updates, and related document workflows.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

## Quick start

Create a local request record, extract the returned id, then pass that id to the next command:

```bash
python scripts/passport_id_scheduler_cli.py create-request \
  --service passport_renewal \
  --city "Tel Aviv-Yafo" \
  --date-from 2026-08-01 \
  --date-to 2026-08-31 \
  --output request.json \
  --env sandbox

REQUEST_ID=$(python - <<'PY'
import json
print(json.load(open('request.json', encoding='utf-8'))['id'])
PY
)

python scripts/passport_id_scheduler_cli.py show-request \
  --input request.json \
  --request-id "$REQUEST_ID"
```

Validate an Israeli ID number:

```bash
python scripts/passport_id_scheduler_cli.py validate-id 123456782
```

Normalize an Israeli phone number:

```bash
python scripts/passport_id_scheduler_cli.py normalize-phone "+972 52 123 4567"
```

Create a planning checklist:

```bash
python scripts/passport_id_scheduler_cli.py plan --service passport_renewal --city "Tel Aviv-Yafo" --date-from 2026-08-01 --date-to 2026-08-31
```

Rank user-provided official slots:

```bash
python scripts/passport_id_scheduler_cli.py rank-slots --input slots.json
```

Create a calendar reminder:

```bash
python scripts/passport_id_scheduler_cli.py make-ics --title "Passport renewal appointment" --date 2026-08-15 --time 09:30 --location "Population and Immigration Authority bureau" --output appointment.ics
```

Run tests:

```bash
pytest -q scripts/test_passport_id_scheduler_client.py
```

## Import from Python

```python
from passport_id_scheduler_client import AppointmentRequest, PassportIdSchedulerClient

plan = PassportIdSchedulerClient().build_plan(AppointmentRequest(service="passport_renewal"))
print(plan.to_dict())
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Public source and local interface reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | 20+ concrete tests and manual scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding and visual-asset audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `references/verification-log.md` | Web-validation log with two-pass source checks |
| `scripts/passport_id_scheduler_client.py` | Typed sync and async local client/helper |
| `scripts/passport_id_scheduler_cli.py` | Typer CLI |
| `scripts/test_passport_id_scheduler_client.py` | pytest suite |
| `scripts/examples/` | Runnable scenario scripts |

## Safe boundaries

This package prepares and validates data, builds checklists, ranks slots supplied by the user, and creates reminders. It does not log in, solve CAPTCHA, bypass queues, scrape restricted systems, store one-time codes, collect card data, or guarantee processing times.

## Data handling

Treat Teudat Zehut, phone, email, and appointment confirmations as personal data. Mask IDs in logs and shared files. Delete temporary files when they are no longer needed.

## Official appointment channel

Use gov.il and GoVisit (`https://govisit.gov.il/`) for live appointment booking. Complete login, identity verification, payment, and confirmation only through authorized official channels.
