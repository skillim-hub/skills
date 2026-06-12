# WhatsApp Scheduling Bot

A neutral skill package for building a Hebrew WhatsApp appointment scheduling bot for Israeli small businesses, freelancers, clinics, salons, tutors, consultants, and local service providers. The package books appointments, sends WhatsApp confirmations and reminders, parses simple replies, and keeps Israeli defaults for phone numbers, timezone, prices, and Hebrew wording.

## Install

```bash
cd whatsapp-scheduling-bot
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
python -m pytest
```

## Environment

```bash
export WHATSAPP_SANDBOX_ACCESS_TOKEN="sandbox-token"
export WHATSAPP_SANDBOX_PHONE_ID="sandbox-phone-id"
export WHATSAPP_ACCESS_TOKEN="production-token"
export WHATSAPP_PHONE_ID="production-phone-id"
export WHATSAPP_API_VERSION="v25.0"
export BOT_BUSINESS_NAME="קליניקת הדוגמה"
```

Use `--env sandbox` during development and switch to `--env production` only after templates, webhooks, calendars, opt-out handling, and logs are verified.

## Quick Start

Create an appointment in Python, extract the generated identifier from the create response, then reuse that identifier in the next step.

```python
from whatsapp_scheduling_bot import WhatsAppSchedulingClient

client = WhatsAppSchedulingClient(access_token="dry", phone_number_id="dry")
appointment = client.create_appointment(
    customer_name="דנה",
    customer_phone="054-123-4567",
    service_name="ייעוץ ראשוני",
    start_at="2026-06-18T10:30:00+03:00",
    duration_minutes=45,
    business_name="קליניקת הדוגמה",
    price_ils=250,
    location="רחוב הרצל 10, תל אביב",
)
appointment_id = appointment.appointment_id

client.update_appointment_status(appointment_id, "confirmed")
result = client.send_appointment_confirmation(appointment, dry_run=True)
print(result.raw)
```

Preview the same confirmation from the CLI:

```bash
python scripts/whatsapp-scheduling-bot-cli.py confirm \
  --env sandbox \
  --to "054-123-4567" \
  --customer "דנה" \
  --service "ייעוץ ראשוני" \
  --start "2026-06-18T10:30:00+03:00" \
  --duration 45 \
  --business "קליניקת הדוגמה" \
  --price 250 \
  --location "רחוב הרצל 10, תל אביב" \
  --dry-run
```

Validate a phone number:

```bash
python scripts/whatsapp-scheduling-bot-cli.py validate-phone "054-123-4567"
```

Run examples:

```bash
python scripts/examples/01_send_confirmation.py --env sandbox
python scripts/examples/02_due_reminders.py --env sandbox
python scripts/examples/03_parse_webhook.py --env sandbox
python scripts/examples/04_import_csv_preview.py --env sandbox
python scripts/examples/05_async_bulk_reminders.py --env sandbox
```


## Web-validated defaults

The package was rechecked on 03/06/2026 against live official sources. Use Graph API `v25.0` by default, keep `WHATSAPP_API_VERSION` configurable, treat WhatsApp pricing as per-message pricing by market and category, and use Israeli VAT `18%` only when a workflow explicitly displays tax-inclusive pricing or invoice guidance. Service reminders should stay logistical; marketing content requires a separate lawful basis and opt-out handling.

## File Index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with examples, edge cases, decision trees, troubleshooting, anti-patterns, and checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ prices, and `DD/MM/YYYY` localization |
| `references/api-reference.md` | API and Israeli regulation reference with request/response examples and error tables |
| `references/workflow-guide.md` | End-to-end appointment workflows |
| `references/troubleshooting.md` | Troubleshooting and recovery playbooks |
| `references/test-scenarios.md` | Concrete test scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Neutrality and public-file audit report |
| `references/hebrew-qa-log.md` | Hebrew quality review log |
| `whatsapp_scheduling_bot/client.py` | Typed sync and async Python client |
| `whatsapp_scheduling_bot/cli.py` | Installable Typer CLI module |
| `scripts/whatsapp_scheduling_bot_client.py` | Import compatibility wrapper for the client |
| `scripts/whatsapp-scheduling-bot-cli.py` | Script wrapper for the CLI |
| `scripts/test_whatsapp_scheduling_bot_client.py` | Pytest suite |
| `scripts/examples/` | Five runnable scenario scripts |
| `metadata.json` | Neutral skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Installable package and test configuration |
| `requirements-dev.txt` | Development dependencies |

## Development Rules

- Use timezone-aware datetimes with `Asia/Jerusalem`.
- Store WhatsApp phone numbers as `972...` without `+`.
- Display dates as `DD/MM/YYYY`.
- Display prices with `₪`.
- Separate service reminders from marketing.
- Persist idempotency keys before retrying sends.
- Do not commit access tokens, customer exports, full webhook bodies, or sensitive service notes.

## Test

```bash
python -m pytest
python -m compileall scripts/ -q
```

## License

MIT. See `LICENSE`.
