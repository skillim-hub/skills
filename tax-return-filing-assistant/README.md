# Tax Return Filing Assistant

A neutral bilingual skill package for preparing Israeli tax-return workflows for small businesses, freelancers, employers, and consumers. Covers Forms **1301**, **135**, **126**, **856**, and **6111** with form selection, field-by-field help, deadline reminders, validation, troubleshooting, and CLI helpers.

This package is a preparation assistant. It does not submit tax returns, provide legal representation, or replace a licensed Israeli tax adviser or accountant.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained profile ID

Create a local profile, extract the returned ID, and reuse it in the next step.

```bash
PROFILE_ID=$(tax-return-filing-assistant create-profile \
  --env sandbox \
  --tax-year 2025 \
  --taxpayer-type sole_proprietor \
  --business-income \
  --annual-turnover-ils 420000 \
  --paid-suppliers \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')

tax-return-filing-assistant report --profile-id "$PROFILE_ID"
tax-return-filing-assistant checklist --profile-id "$PROFILE_ID"
tax-return-filing-assistant deadline 1301 --tax-year 2025 --env sandbox
```

Alternative file-based flow:

```bash
tax-return-filing-assistant init-profile --output profile.json --tax-year 2025
tax-return-filing-assistant recommend --profile profile.json
tax-return-filing-assistant fields 856 withholding_rate
tax-return-filing-assistant export-report --profile profile.json --output report.json
```

## Python import quick start

```python
from tax_return_filing_assistant_client import FilingProfile, TaxReturnAssistantClient

client = TaxReturnAssistantClient()
profile = FilingProfile(
    tax_year=2025,
    taxpayer_type="sole_proprietor",
    business_income=True,
    annual_turnover_ils=420000,
    paid_suppliers=True,
)
report = client.generate_report(profile)
```

## Environment variables

| Variable | Purpose |
|---|---|
| `TAX_ASSISTANT_ENV` | Default CLI/example environment, `sandbox` or `production` |
| `TAX_ASSISTANT_TAX_YEAR` | Default tax year used by examples and selected CLI commands |
| `TAX_ASSISTANT_STATE_PATH` | Optional JSON path for local profile ID storage |
| `TAX_ASSISTANT_PROFILE` | Optional profile JSON path when `--profile` is omitted |
| `TAX_ASSISTANT_TURNOVER_ILS` | Example turnover amount in ₪ |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with decision trees, examples, edge cases, troubleshooting, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ amounts, and DD/MM/YYYY dates |
| `references/api-reference.md` | Official source categories, regulatory anchors, local request/response examples, and error table |
| `references/workflow-guide.md` | End-to-end filing workflows for Forms 1301, 135, 126, 856, and 6111 |
| `references/troubleshooting.md` | Detailed problem diagnosis and resolution guide |
| `references/test-scenarios.md` | 30 concrete manual and automated test scenarios |
| `references/migration-checklist.md` | Migration checklist for replacing older packages |
| `references/branding-audit.md` | Branding, authorship, visual-asset, and emoji audit report |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log |
| `references/verification-log.md` | Two-pass web validation log with source snippets, URLs, and corrections |
| `scripts/tax_return_filing_assistant_client.py` | Typed sync and async client/helper library |
| `scripts/tax_return_filing_assistant_cli.py` | Click-based command-line interface |
| `scripts/test_tax_return_filing_assistant_client.py` | Pytest suite with 20+ tests |
| `scripts/examples/` | Runnable scenario scripts using env vars and `--env sandbox|production` |
| `metadata.json` | Package metadata without author field |
| `CHANGELOG.md` | Keep a Changelog format |
| `LICENSE` | MIT license |

## Example profile

```json
{
  "tax_year": 2025,
  "taxpayer_type": "sole_proprietor",
  "salary_only": false,
  "wants_refund": false,
  "business_income": true,
  "annual_turnover_ils": 420000,
  "has_employees": false,
  "paid_suppliers": true,
  "foreign_income": false,
  "capital_gains": false,
  "rental_income": false,
  "is_online": true,
  "represented_by_cpa": false
}
```

Expected recommendation:

```json
{
  "forms": ["1301", "856", "6111"]
}
```

## Development

```bash
pip install -e .
pip install -r requirements-dev.txt
pytest -q
python -m compileall scripts/ -q
tax-return-filing-assistant --help
```

## Safety and compliance

- Verify current official Tax Authority instructions for each filing year.
- Redact identity, payroll, bank, and medical data before sharing.
- Do not use screen scraping or unofficial portal automation.
- Treat deadlines and thresholds as planning defaults until officially confirmed.
