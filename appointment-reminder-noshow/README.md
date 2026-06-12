# Appointment Reminder & No-Show Tracker

Reduce appointment no-shows with WhatsApp/SMS reminders, Hebrew message templates, no-show tracking, and re-booking suggestions for Israeli small businesses, freelancers, clinics, instructors, and service providers.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

For direct script use without installation:

```bash
python scripts/appointment_reminder_noshow_cli.py --help
```

## Quick start

Validate an Israeli mobile number:

```bash
python scripts/appointment_reminder_noshow_cli.py validate-phone 050-123-4567
```

Render one Hebrew reminder:

```bash
python scripts/appointment_reminder_noshow_cli.py message \
  --name "יעל כהן" \
  --phone "050-123-4567" \
  --starts-at "2026-06-18T15:30:00+03:00" \
  --business-name "קליניקת אביב" \
  --service-name "פגישת המשך" \
  --location "רוטשילד 10, תל אביב" \
  --language he
```

Plan reminders from a JSON file:

```bash
python scripts/appointment_reminder_noshow_cli.py plan \
  --input appointments.json \
  --now "2026-06-16T08:00:00+03:00" \
  --hours-before "48,24,3"
```

Send through the mock provider:

```bash
python scripts/appointment_reminder_noshow_cli.py send \
  --message-json reminder.json \
  --provider mock
```

## Appointment input JSON

```json
[
  {
    "id": "a1",
    "starts_at": "2026-06-18T15:30:00+03:00",
    "business_name": "קליניקת אביב",
    "service_name": "פגישת המשך",
    "location": "רוטשילד 10, תל אביב",
    "price_ils": 250,
    "customer": {
      "id": "c1",
      "name": "יעל כהן",
      "phone": "050-123-4567",
      "preferred_language": "he",
      "consent_whatsapp": true,
      "consent_sms": true
    }
  }
]
```

## Provider configuration

Use environment variables for provider credentials:

| Provider | Variables |
|---|---|
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_FROM` or `TWILIO_MESSAGING_SERVICE_SID`, `STATUS_CALLBACK_URL` |
| WhatsApp Cloud API | `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_GRAPH_VERSION` |
| Generic webhook | `GENERIC_WEBHOOK_URL`, optional `GENERIC_WEBHOOK_TOKEN` |

Keep production credentials out of repository files and prompts.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with workflow, examples, decision tree, troubleshooting, and anti-patterns. |
| `SKILL_HE.md` | Hebrew skill guide with Israeli terminology, ₪, and `DD-MM-YYYY` examples. |
| `references/api-reference.md` | Web-validated Israeli rates, thresholds, regulations, forms, endpoint paths, and error tables. |
| `references/troubleshooting.md` | Operational troubleshooting for scheduling, WhatsApp, SMS, consent, no-show tracking, and CLI usage. |
| `references/test-scenarios.md` | Manual and automated acceptance scenarios. |
| `scripts/appointment_reminder_noshow_client.py` | Typed sync and async client. |
| `scripts/appointment_reminder_noshow_cli.py` | Click CLI for day-to-day use. |
| `scripts/test_appointment_reminder_noshow_client.py` | Pytest suite. |
| `metadata.json` | Skill metadata. |
| `CHANGELOG.md` | Keep-a-Changelog history. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Python project configuration. |
| `requirements-dev.txt` | Development dependencies. |

## Test

```bash
pytest -q
```

## Compliance notes

Use the API reference before production rollout. Separate transactional reminders from marketing, preserve consent records, minimize personal data, and review no-show fees before collection.
