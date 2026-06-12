# Domestic Bank Transfer Form Helper

Neutral helper for preparing Israeli domestic bank transfer forms for MASAV and Zahav. Validate fields, recommend a transfer method, produce reports, stage local review records, and run regression tests before bank portal entry.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

`pip install -e .` installs importable modules and the `domestic-bank-transfer-helper` command. `pip install -r requirements-dev.txt` installs test tooling, including async test support.

## Quick start

Create a local transfer record in sandbox:

```bash
CREATE_RESPONSE="$(domestic-bank-transfer-helper --env sandbox create   --recipient-name "Example Supplier Ltd"   --bank-code 12   --branch-code 456   --account-number 123456789   --amount-ils "2450.80"   --value-date "03/06/2026"   --purpose "Invoice 1007"   --reference "INV-1007")"

echo "$CREATE_RESPONSE"
```

Extract the transfer identifier from the create response:

```bash
TRANSFER_ID="$(printf '%s' "$CREATE_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
```

Use the identifier in the next step:

```bash
domestic-bank-transfer-helper --env sandbox payload "$TRANSFER_ID"
```

Validate without storing a record:

```bash
domestic-bank-transfer-helper --env sandbox validate   --recipient-name "Example Supplier Ltd"   --bank-code 12   --branch-code 456   --account-number 123456789   --amount-ils "2450.80"   --value-date "03/06/2026"   --purpose "Invoice 1007"   --json-output
```

## Python use

```python
from datetime import date
from domestic_bank_transfer_helper_client import TransferRequest, create_transfer_record, record_payload

request = TransferRequest(
    recipient_name="Example Supplier Ltd",
    bank_code="12",
    branch_code="456",
    account_number="123456789",
    amount_ils="2450.80",
    value_date="03/06/2026",
    purpose="Invoice 1007",
)
created = create_transfer_record(request, env="sandbox", today=date(2026, 6, 2))
transfer_id = created["id"]
payload = record_payload(transfer_id, env="sandbox")
print(payload)
```

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DOMESTIC_TRANSFER_ENV` | Default environment for CLI and examples | `sandbox` |
| `DOMESTIC_TRANSFER_STATE_DIR` | Local state directory for create/show/payload examples | `.domestic-bank-transfer-helper` |
| `DBTF_RECIPIENT_NAME` | Example recipient override | scenario-specific |
| `DBTF_BANK_CODE` | Example bank code override | `12` |
| `DBTF_BRANCH_CODE` | Example branch override | `456` |
| `DBTF_ACCOUNT_NUMBER` | Example account override | `123456789` |
| `DBTF_AMOUNT_ILS` | Example amount override | scenario-specific |
| `DBTF_VALUE_DATE` | Example value date override | `03/06/2026` |
| `DBTF_PURPOSE` | Example purpose override | scenario-specific |
| `DBTF_REFERENCE` | Example reference override | scenario-specific |
| `DBTF_APPROVED_BY` | Example approver override | `Finance Manager` |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with decision trees, examples, edge cases, anti-patterns, troubleshooting, and production checklist. |
| `SKILL_HE.md` | Hebrew skill guide with Israeli professional terminology, ₪ examples, and `DD/MM/YYYY` localization. |
| `references/api-reference.md` | Internal API model, Israeli operational and regulatory references, examples, and error tables. |
| `references/workflow-guide.md` | End-to-end payment workflows for suppliers, Zahav, payroll, refunds, rent, and tax payments. |
| `references/troubleshooting.md` | Detailed troubleshooting guide for rejected forms, unknown bank codes, batch issues, and approval gaps. |
| `references/test-scenarios.md` | More than 20 concrete QA scenarios. |
| `references/migration-checklist.md` | Checklist for moving from ad hoc spreadsheets to controlled payment preparation. |
| `references/branding-audit.md` | Audit notes for branding, provenance, visual assets, and neutral packaging. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log. |
| `references/verification-log.md` | Web validation log with two-pass official-source checks and package actions. |
| `scripts/domestic_bank_transfer_helper_client.py` | Typed sync and async validation client plus local record helpers. |
| `scripts/domestic_bank_transfer_helper_cli.py` | Importable Click CLI implementation. |
| `scripts/domestic-bank-transfer-helper-cli.py` | Compatibility wrapper for direct script execution. |
| `scripts/test_domestic_bank_transfer_helper_client.py` | Pytest suite covering validation, async helpers, CLI, and record chaining. |
| `scripts/examples/` | Runnable scenario scripts using environment variables and `--env sandbox|production`. |

## Run tests

```bash
python -m compileall scripts/ -q
pytest
```

## Operational notes

- Use sandbox while designing forms, tests, and workflow automation.
- Use production only for controlled review before bank entry.
- Keep bank portal credentials and banking authorization outside this helper.
- Confirm current bank cutoffs, fees, limits, and branch lists with the relevant bank.
- Use Bank of Israel identification-code and branch sources as current references; expect the code format to expand to three digits by the end of 2026.
- Use independent recipient-detail confirmation for new, changed, urgent, or high-value payments.
