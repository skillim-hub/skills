# Arnona Payment Reminder

Create reminder plans, payment instructions, receipt workflows, and validation checks for Israeli municipal Arnona payments.

This package supports consumers, freelancers, small businesses, property managers, and accounting workflows that need to handle Arnona bills across Israeli municipalities without guessing payment details or relying on stale vouchers. It uses municipality-specific profiles and generic workflows; it does not claim a single national Arnona payment API.

## Installation for Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
pytest
```

## Quick Start

Create a local bill record, extract the returned id, then use that id in the next command.

```bash
CREATE_RESPONSE=$(arnona-payment-reminder --env sandbox create \
  --municipality "Tel Aviv-Yafo" \
  --account-reference "123456789" \
  --bill-number "2026-ARN-000123" \
  --taxpayer-name "Sample Business Ltd." \
  --property-address "Ibn Gabirol 1, Tel Aviv-Yafo" \
  --period-start "2026-01-01" \
  --period-end "2026-02-28" \
  --issue-date "2026-01-05" \
  --due-date "2026-02-28" \
  --amount-nis "1540.20" \
  --store-dir .arnona-payments)

BILL_ID=$(python -c 'import json, sys; print(json.loads(sys.stdin.read())["id"])' <<< "$CREATE_RESPONSE")
arnona-payment-reminder plan-id "$BILL_ID" --store-dir .arnona-payments --as-of 2026-02-01 --format text
```

File-based usage is also supported.

```bash
arnona-payment-reminder sample-bill sample-bill.json
arnona-payment-reminder validate sample-bill.json
arnona-payment-reminder plan sample-bill.json --as-of 2026-02-01 --format json
arnona-payment-reminder export-ics sample-bill.json arnona.ics --as-of 2026-02-01
```

## Python Usage

```python
from arnona_payment_reminder import ArnonaBill, ArnonaPaymentReminderClient

client = ArnonaPaymentReminderClient.with_default_profiles()
bill = ArnonaBill.from_dict({
    "municipality": "Tel Aviv-Yafo",
    "account_reference": "123456789",
    "bill_number": "2026-ARN-000123",
    "taxpayer_name": "Sample Business Ltd.",
    "property_address": "Ibn Gabirol 1, Tel Aviv-Yafo",
    "period_start": "2026-01-01",
    "period_end": "2026-02-28",
    "issue_date": "2026-01-05",
    "due_date": "2026-02-28",
    "amount_nis": "1540.20",
    "status": "unpaid",
})
plan = client.build_reminder_plan(bill, as_of="2026-02-01", language="en")
print(plan.to_json())
```

## Environment Variables Used by Examples

The scripts in `scripts/examples/` read environment variables and accept `--env sandbox|production`.

Common variables:

| Variable | Purpose |
|---|---|
| `ARNONA_PAYMENT_REMINDER_ENV` | Default example environment. |
| `ARNONA_AS_OF` | Reference date for status and reminder generation. |
| `ARNONA_OUTPUT_DIR` | Output directory for generated files. |
| `ARNONA_MUNICIPALITY` | Municipality name. |
| `ARNONA_ACCOUNT_REFERENCE` | Payer or account reference. |
| `ARNONA_BILL_NUMBER` | Voucher or bill number. |
| `ARNONA_AMOUNT_NIS` | Amount in new Israeli shekels. |

Run an example after installation:

```bash
python scripts/examples/04_hebrew_household_instructions.py --env sandbox
```

## File Index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with examples, edge cases, decision trees, anti-patterns, troubleshooting, and production checklist. |
| `SKILL_HE.md` | Hebrew skill guide with Israeli professional terminology and localized date/currency conventions. |
| `arnona_payment_reminder/client.py` | Typed sync and async Python implementation. |
| `arnona_payment_reminder/cli.py` | Installable Click command-line implementation. |
| `scripts/arnona_payment_reminder_client.py` | Compatibility import module using the underscored name. |
| `scripts/arnona-payment-reminder-cli.py` | Command-line wrapper. |
| `scripts/test_arnona_payment_reminder_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable scenario scripts. |
| `references/api-reference.md` | Regulatory and adapter reference for municipal payment integrations. |
| `references/workflow-guide.md` | End-to-end household, business, freelancer, tenant, overdue, corrected bill, standing order, and accounting workflows. |
| `references/troubleshooting.md` | Operational troubleshooting guide. |
| `references/test-scenarios.md` | More than 20 concrete QA scenarios. |
| `references/migration-checklist.md` | Migration from calculators, spreadsheets, and optimizer workflows. |
| `references/branding-audit.md` | Neutrality and attribution audit. |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance log. |
| `metadata.json` | Skill metadata without creator metadata. |
| `pyproject.toml` | Build, installation, console script, and test configuration. |
| `requirements-dev.txt` | Development dependencies. |
| `LICENSE` | MIT license. |

## Safety Notes

- Use the official municipality payment page or the link printed on the bill.
- Do not pay from unofficial links.
- Verify property address, billing period, payer or account number, voucher number, amount, and due date before payment.
- For overdue bills, request a current balance before payment.
- Store a receipt before marking a bill as paid.
- Treat payer IDs, account references, addresses, and receipts as sensitive data.
