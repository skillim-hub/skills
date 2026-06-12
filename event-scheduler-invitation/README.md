# Event Scheduler & Invitation Manager

Bilingual planning package for Israeli lifecycle events, Hebrew RSVP management, venue operations, supplier coordination, and small-business event workflows.

## Install

```bash
cd event-scheduler-invitation
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a plan, extract the returned `event_id`, then reuse it in the next command.

```bash
CREATE_RESPONSE=$(event-scheduler-invitation create-plan \
  --event-type wedding \
  --date 18/06/2026 \
  --title "חתונת מאיה ויונתן" \
  --city רחובות \
  --output plan.json)

EVENT_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["event_id"])' <<< "$CREATE_RESPONSE")

event-scheduler-invitation add-guest \
  --plan plan.json \
  --event-id "$EVENT_ID" \
  --name דנה \
  --phone 050-123-4567 \
  --party-size 2 \
  --status מגיעים

event-scheduler-invitation summary --csv scripts/examples/sample_guests.csv
```

## Use the package directly

```python
from event_scheduler_invitation import EventSchedulerClient, EventType, Guest, RSVPStatus

client = EventSchedulerClient()
plan = client.create_plan(
    event_type=EventType.WEDDING,
    event_date="18/06/2026",
    title="חתונת מאיה ויונתן",
    city="רחובות",
)
client.add_guest(plan, Guest("דנה", phone="050-123-4567", party_size_invited=2, status=RSVPStatus.CONFIRMED))
print(client.plan_response(plan))
```

## CLI commands

```bash
event-scheduler-invitation --help
event-scheduler-invitation budget --guests 120 --per-plate 280 --fixed-costs 18000
event-scheduler-invitation tax-check --amount-before-vat 6000 --invoice-date 02/06/2026 --vat-amount 1080
event-scheduler-invitation music-license --event-type wedding --date 18/06/2026
event-scheduler-invitation brit-date --birth-date 03/03/2026
event-scheduler-invitation tables --csv scripts/examples/sample_guests.csv --table-size 10
event-scheduler-invitation timeline --event-type bar_mitzvah --date 07/11/2026 --title "בר המצווה של נועם"
```

The wrapper script remains available for direct execution:

```bash
python scripts/event-scheduler-invitation-cli.py budget --guests 250 --per-plate 330 --fixed-costs 40000
```

## Runnable examples

Each example accepts `--env sandbox|production`, reads environment variables, and prints JSON with Hebrew preserved.

```bash
EVENT_SCHEDULER_DEFAULT_CITY=רחובות python scripts/examples/create_wedding_timeline.py --env sandbox
EVENT_SCHEDULER_DEFAULT_CITY=ירושלים python scripts/examples/bar_mitzvah_seating.py --env sandbox
EVENT_SCHEDULER_CONTACT_PHONE=050-123-4567 python scripts/examples/brit_milah_quick_plan.py --env production
python scripts/examples/rsvp_import_and_reminders.py --env sandbox
python scripts/examples/vendor_payment_milestones.py --env sandbox
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Israeli APIs, portals, adapter contracts, and regulation checkpoints |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Failure modes and recovery playbooks |
| `references/test-scenarios.md` | Concrete scenarios for acceptance testing |
| `references/migration-checklist.md` | Migration from older packages or spreadsheets |
| `references/branding-audit.md` | Branding, authorship, visual-asset and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology correction log |
| `references/verification-log.md` | Web validation log with two-pass source checks |
| `event_scheduler_invitation/` | Installable Python package |
| `scripts/event_scheduler_invitation_client.py` | Underscored client module copy for script-based use |
| `scripts/event-scheduler-invitation-cli.py` | CLI wrapper for direct execution |
| `scripts/test_event_scheduler_invitation_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario examples |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Release history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Installable Python project configuration |
| `requirements-dev.txt` | Development dependencies |

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## Localization

Use `₪12,345` for currency, `DD/MM/YYYY` for Hebrew-facing dates, and `Asia/Jerusalem` for event operations. As verified on 04/06/2026, use 18% as the VAT planning rate and flag Israel invoice allocation-number follow-up at ₪10,000 before VAT through 31/05/2026 and ₪5,000 before VAT from 01/06/2026. Normalize Israeli phone numbers to `+972...` where possible.

## Privacy and compliance

Store only operational data needed for the event. Delete dietary, accessibility, and sensitive family notes after closeout unless a legitimate retention reason exists. Verify official requirements for messaging, accessibility, tax, invoice allocation numbers, music licensing, religious procedures, and medical procedures before execution.
