# Lead Qualification Bot

A neutral, brand-free skill package for building a Hebrew WhatsApp-first lead qualification bot for Israeli small businesses, freelancers, clinics, and consumer-facing service providers.

The package includes English and Hebrew implementation guides, Israeli workflow references, troubleshooting material, test scenarios, migration guidance, an importable Python package, a Typer command line interface, runnable examples, and pytest coverage.

## Install

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a lead and save the response:

```bash
lead-qualification-bot create \
  --message "צריך הצעת מחיר לתיקון נזילה היום בתל אביב, תקציב 500 שח" \
  --phone "050-123-4567" \
  --name "דנה" \
  --env sandbox > lead.json
```

Extract the lead identifier from the create response and use it in the next step:

```bash
LEAD_ID=$(python - <<'PY'
import json
with open("lead.json", encoding="utf-8") as f:
    print(json.load(f)["lead_id"])
PY
)

mv lead.json "${LEAD_ID}.json"

lead-qualification-bot get --lead-json "${LEAD_ID}.json"
```

Run tests:

```bash
pytest -q
python -m compileall scripts/ -q
```

## Python usage

```python
from lead_qualification_bot import LeadQualificationClient

client = LeadQualificationClient(environment="sandbox")
lead = client.create_lead(
    message="צריך תיקון נזילה היום בתל אביב תקציב 500 שח",
    phone="050-123-4567",
    name="דנה",
)
print(client.to_json(lead, ensure_ascii=False, indent=2))
```

## Batch mode

```bash
lead-qualification-bot batch \
  --input scripts/examples/sample_leads.csv \
  --output qualified_leads.csv \
  --env sandbox
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | Comprehensive English guide |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology and localization |
| `references/api-reference.md` | WhatsApp, CRM, privacy, marketing, consumer, and tax reference |
| `references/workflow-guide.md` | End-to-end implementation workflows |
| `references/troubleshooting.md` | Diagnostic and incident guide |
| `references/test-scenarios.md` | Concrete QA scenarios |
| `references/migration-checklist.md` | Migration plan from manual or legacy workflows |
| `references/branding-audit.md` | Branding, author, logo, and image audit |
| `references/hebrew-qa-log.md` | Hebrew quality correction log |
| `lead_qualification_bot/client.py` | Typed sync and async qualification client |
| `lead_qualification_bot/cli.py` | Typer command line interface |
| `scripts/lead_qualification_bot_client.py` | Underscored compatibility import module |
| `scripts/lead-qualification-bot-cli.py` | Executable CLI wrapper |
| `scripts/test_lead_qualification_bot_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario examples |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep a Changelog format |
| `LICENSE` | MIT license |
| `pyproject.toml` | Python packaging and test configuration |
| `requirements-dev.txt` | Development dependencies |

## Design goals

- Hebrew-first WhatsApp qualification.
- Local Israeli formats: ₪, DD/MM/YYYY, Israeli phone numbers, and Sunday-Thursday business assumptions.
- Minimal data collection.
- Separate service follow-up and marketing consent.
- Human handoff for sensitive topics.
- Practical scoring and routing.
- No branding, logos, author fields, or distribution callouts.

## Compliance note

This package is not legal advice. Verify current Israeli privacy, marketing, consumer-protection, accessibility, tax, payment, and platform requirements before production deployment.


## Web validation

The package includes `references/verification-log.md`, which records two independent validation passes for Israeli VAT, exempt dealer threshold, Israel Invoices thresholds, privacy/security references, spam-law references, consumer price display, accessibility, and WhatsApp Business Platform API/webhook details.

As of 03/06/2026, the package uses 18% VAT and 2026 Israeli tax thresholds as configurable reference defaults. Recheck before production.
