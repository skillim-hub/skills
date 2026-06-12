# Bituach Leumi Payment Scheduler

Create local payment schedules, reminders, and exports for Israeli National Insurance payment workflows. Suitable for self-employed workers, freelancers, small employers, small businesses, and consumers tracking official installments or balances.

## Install

Use Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

For a lightweight runtime, only `click` is required by the CLI. Development and verification require `pytest` and `pytest-asyncio`.

## Quick start

Create a local plan record, extract the id from the create response, then use the id in the next command.

```bash
CREATE_RESPONSE=$(bituach-leumi-payment-scheduler --env sandbox create \
  --payer-type self-employed \
  --payer-name "Freelance Studio" \
  --start-month 2026-01 \
  --months 12 \
  --income 14000)

PLAN_ID=$(printf '%s' "$CREATE_RESPONSE" | python -c 'import json, sys; print(json.load(sys.stdin)["plan_id"])')

bituach-leumi-payment-scheduler show "$PLAN_ID" --format json
```

Generate an ICS calendar file from an official amount:

```bash
bituach-leumi-payment-scheduler plan \
  --payer-type self-employed \
  --payer-name "Independent Designer" \
  --start-month 2026-01 \
  --months 12 \
  --amount 1240 \
  --format ics \
  --output bituach-leumi-2026.ics
```

Generate an employer CSV:

```bash
bituach-leumi-payment-scheduler --env production plan \
  --payer-type employer \
  --payer-name "Small Employer Ltd" \
  --start-month 2026-01 \
  --months 6 \
  --payroll 65000 \
  --format csv \
  --output form-102-calendar.csv
```

Import the installable module:

```python
from bituach_leumi_payment_scheduler import BusinessProfile, BusinessType, ScheduleOptions, generate_payment_plan
```

Run tests and syntax checks:

```bash
python -m pytest -q
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | official-channel, regulation, local request/response, and error reference |
| `references/workflow-guide.md` | end-to-end operational workflows |
| `references/troubleshooting.md` | common issues and fixes |
| `references/test-scenarios.md` | manual and automated scenario list |
| `references/migration-checklist.md` | migration from spreadsheets, calendars, or prior packages |
| `references/branding-audit.md` | branding and authorship audit |
| `references/hebrew-qa-log.md` | Hebrew localization review notes |
| `bituach_leumi_payment_scheduler/` | installable Python package |
| `scripts/bituach_leumi_payment_scheduler_client.py` | typed sync and async helper implementation |
| `scripts/bituach-leumi-payment-scheduler-cli.py` | runnable CLI wrapper |
| `scripts/test_bituach_leumi_payment_scheduler_client.py` | pytest coverage |
| `scripts/examples/` | runnable scenario scripts |
| `metadata.json` | neutral skill metadata |
| `CHANGELOG.md` | version history |
| `LICENSE` | MIT license |
| `pyproject.toml` | install and test configuration |
| `requirements-dev.txt` | development dependencies |

## Data handling

Do not store passwords, card details, one-time codes, or full identity numbers in exported schedules. Use internal payer codes where possible.

## Verification rule

Verify official amount, status, due date, and payment channel in Bituach Leumi systems before payment. The scheduler is a planning aid, not a final assessment.

## Web-validated 2026 assumptions

The bundled default estimates use the 2026 Bituach Leumi planning values verified on 02/06/2026: self-employed standard adult rates of 7.70% up to ₪7,703 and 18.00% above that level up to the monthly ceiling, employer Form 102 resident-employee combined rates of 8.78% and 19.77%, and the minimum no-income consumer amount of ₪266. Treat these as planning defaults only. Override the amount with the official voucher, payroll-system total, personal-area balance, or accountant workpaper before paying.

VAT is not used by the scheduler, but the verification pass confirmed the current Israeli standard VAT rate as 18% from 01/01/2025 and still current in 2026. Keep VAT logic outside this package unless a downstream workflow explicitly needs it.
