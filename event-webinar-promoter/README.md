# Event & Webinar Promoter

Plan and promote events and webinars for Israeli audiences. The package includes bilingual guidance, Israeli operational references, a typed Python helper, a Click CLI, runnable examples, and a pytest suite.

## What this package does

- Builds event and webinar promotion plans.
- Uses `Asia/Jerusalem` timezone.
- Generates Hebrew-first copy.
- Uses ₪ pricing and Hebrew-facing `DD/MM/YYYY` dates.
- Creates reminder schedules.
- Recommends Israeli channel mixes.
- Adds consent, privacy, accessibility, VAT, cancellation, and recording checks.
- Builds UTM links.
- Supports synchronous and asynchronous Python use.
- Runs without network access or external credentials.

## Install for local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with stored event id

Create a sample event file:

```bash
python -m event_webinar_promoter.cli sample > event.json
```

Store the event and capture the create response:

```bash
python -m event_webinar_promoter.cli create event.json --store .event-webinar-promoter-state > create-response.json
```

Extract the `event_id` from the create response:

```bash
EVENT_ID="$(python - <<'PY'
import json
print(json.load(open("create-response.json", encoding="utf-8"))["event_id"])
PY
)"
```

Use the stored `event_id` in the next step:

```bash
python -m event_webinar_promoter.cli plan --event-id "$EVENT_ID" --store .event-webinar-promoter-state --output plan.json
```

Validate the stored event:

```bash
python -m event_webinar_promoter.cli validate --event-id "$EVENT_ID" --store .event-webinar-promoter-state
```

Generate copy only:

```bash
python -m event_webinar_promoter.cli copy --event-id "$EVENT_ID" --store .event-webinar-promoter-state
```

Print checklist:

```bash
python -m event_webinar_promoter.cli checklist --event-id "$EVENT_ID" --store .event-webinar-promoter-state
```

Build a UTM link:

```bash
python -m event_webinar_promoter.cli utm \
  https://example.co.il/register \
  --source facebook \
  --medium social \
  --campaign pricing_webinar \
  --content launch_post
```

The console command is also available after installation:

```bash
event-webinar-promoter sample
```

Run tests:

```bash
pytest -q
```

Confirm script syntax:

```bash
python -m compileall scripts/ -q
```

## Python usage

```python
from event_webinar_promoter import EventWebinarPromoterClient, sample_event

client = EventWebinarPromoterClient()
event = sample_event()
plan = client.plan(event)
print(plan.to_json())
```

Async:

```python
import asyncio
from event_webinar_promoter import EventWebinarPromoterClient, sample_event

async def main():
    client = EventWebinarPromoterClient()
    plan = await client.aplan(sample_event())
    print(plan.starts_at)

asyncio.run(main())
```

## Examples

Each example accepts `--env sandbox|production` and reads environment variables for production details.

```bash
python scripts/examples/plan_webinar.py --env sandbox
python scripts/examples/paid_workshop.py --env production
python scripts/examples/partner_campaign.py --env sandbox
```

Useful environment variables:

| Variable | Purpose |
|---|---|
| `EWP_ENV` | Default environment for examples |
| `EWP_REGISTRATION_URL` | Production registration URL |
| `EWP_ACCESSIBILITY_CONTACT` | Production accessibility contact |
| `EWP_SANDBOX_REGISTRATION_URL` | Sandbox registration URL |
| `EWP_SANDBOX_ACCESSIBILITY_CONTACT` | Sandbox accessibility contact |
| `EWP_WORKSHOP_DATE` | Workshop date in machine format `DD-MM-YYYY` |
| `EWP_WORKSHOP_TIME` | Workshop time in `HH:MM` |
| `EWP_CITY` | Workshop city |
| `EWP_AUDIENCE` | Audience override |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with workflows, examples, decision trees, checklist, and anti-patterns |
| `SKILL_HE.md` | Hebrew guide with Israeli phrasing, ₪, `DD/MM/YYYY`, and local operational guidance |
| `references/api-reference.md` | Israeli regulation and schema reference |
| `references/workflow-guide.md` | End-to-end campaign workflows |
| `references/troubleshooting.md` | Diagnosis and recovery playbooks |
| `references/test-scenarios.md` | 30 concrete QA and evaluation scenarios |
| `references/migration-checklist.md` | Upgrade and cleanup checklist |
| `references/branding-audit.md` | Branding, creator identity, visual asset, and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `event_webinar_promoter/client.py` | Installable typed sync/async planning helper |
| `event_webinar_promoter/cli.py` | Installable Click CLI |
| `scripts/event_webinar_promoter_client.py` | Script copy of the typed helper for standalone review |
| `scripts/event-webinar-promoter-cli.py` | Direct CLI entrypoint after editable install |
| `scripts/test_event_webinar_promoter_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Neutral skill metadata |
| `CHANGELOG.md` | Keep a Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project and pytest configuration |
| `requirements-dev.txt` | Development dependencies |

## Input format

The machine interface accepts `DD-MM-YYYY` dates so JSON values stay ASCII and easy to validate. Hebrew-facing copy and documentation display dates as `DD/MM/YYYY`.

```json
{
  "event_name": "איך לתמחר שירותים בלי להפסיד לקוחות",
  "format": "webinar",
  "audience": "פרילנסרים בתחילת הדרך",
  "date": "24-06-2026",
  "time": "20:00",
  "duration_minutes": 60,
  "price_nis": 0,
  "goal": "qualified_leads",
  "language": "he",
  "consent_status": "opt_in",
  "registration_url": "https://example.co.il/register"
}
```

## Output highlights

The plan includes:

- `starts_at` and `ends_at` with timezone offset.
- `recommended_channels`.
- `reminders`.
- `compliance_flags`.
- `warnings`.
- `copy`.
- `utm_links`.
- `checklist`.

## Web validation status

Version 2.2.0 includes `references/verification-log.md`, which records two-pass web validation for official Israeli regulatory and technical sources accessed on 2026-06-03. The package still avoids legal or tax advice and requires re-checking before launch.

## Operational cautions

This package provides campaign operations support, not legal advice. Verify current Israeli law, platform policies, and business-specific obligations before publication.
