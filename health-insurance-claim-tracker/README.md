# Health-Insurance Claim Tracker

Offline-first tracker for Israeli health-insurance claims, missing documents, appeals, and reimbursements. Suitable for households, freelancers, small businesses, and clinic administrators that need a local operational record.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a claim and save the returned id:

```bash
CREATE_RESPONSE="$(hict --env sandbox create \
  --claimant-reference client-7788 \
  --policy-type private \
  --provider "Example Insurance" \
  --service-date 15/04/2026 \
  --submission-date 20/04/2026 \
  --amount 850.00 \
  --description "Private specialist consultation" \
  --channel portal \
  --service-kind consultation \
  --follow-up-date 20/05/2026)"

echo "$CREATE_RESPONSE"
CLAIM_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
echo "$CLAIM_ID"
```

Use the extracted id in the next step:

```bash
hict --env sandbox document "$CLAIM_ID" \
  --name receipt.pdf \
  --document-type tax_invoice_or_receipt

hict --env sandbox reimburse "$CLAIM_ID" \
  --amount 300.00 \
  --paid-date 10/05/2026 \
  --payer "Example Insurance"

hict --env sandbox show "$CLAIM_ID"
```

## Python quick start

```python
from health_insurance_claim_tracker import HealthInsuranceClaimTrackerClient

client = HealthInsuranceClaimTrackerClient("claims.json")
claim = client.create_claim(
    claimant_reference="client-7788",
    policy_type="private",
    provider="Example Insurance",
    service_date="15/04/2026",
    submission_date="20/04/2026",
    amount_claimed_ils="850.00",
    description="Private specialist consultation",
)
client.add_document(claim.id, name="receipt.pdf", document_type="tax_invoice_or_receipt")
client.add_reimbursement(claim.id, amount_ils="300.00", paid_date="10/05/2026", payer="Example Insurance")
print(client.get_claim(claim.id).to_dict(redact=True))
```

## Environment variables

| Variable | Use |
|---|---|
| `HICT_STORAGE_PATH` | Local JSON storage path. |
| `HICT_ENV` | Default example environment: `sandbox` or `production`. |
| `HICT_CLAIMANT_REF` | Example claimant reference. |
| `HICT_PROVIDER` | Example provider name. |
| `HICT_AMOUNT` | Example claim amount. |
| `HICT_SERVICE_DATE` | Example service date. |
| `HICT_SUBMISSION_DATE` | Example submission date. |
| `HICT_FOLLOW_UP_DATE` | Example follow-up date. |
| `HICT_CSV_PATH` | Example CSV path. |
| `HICT_DESCRIPTION` | Example claim description. |
| `HICT_CHANNEL` | Example submission channel. |
| `HICT_SERVICE_KIND` | Example service category. |
| `HICT_REIMBURSEMENT_AMOUNT` | Example reimbursement amount. |
| `HICT_PAID_DATE` | Example reimbursement date. |
| `HICT_PAYER` | Example reimbursement payer. |
| `HICT_AS_OF_DATE` | Example overdue-review date. |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, edge cases, decision tree, troubleshooting, anti-patterns, and production checklist. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology, ₪ amounts, and `DD/MM/YYYY` examples. |
| `references/api-reference.md` | Local schema, CLI examples, Python examples, error table, and Israeli source reference. |
| `references/workflow-guide.md` | End-to-end workflows for private policies, supplementary plans, bookkeeping, missing documents, appeals, and weekly review. |
| `references/troubleshooting.md` | Installation, storage, validation, document, reimbursement, import, export, and escalation guidance. |
| `references/test-scenarios.md` | More than 20 concrete acceptance and regression scenarios. |
| `references/migration-checklist.md` | Migration from older package layouts, spreadsheets, portal notes, and mixed personal or business records. |
| `references/branding-audit.md` | Branding, attribution, logo, badge, and emoji audit. |
| `references/hebrew-qa-log.md` | Hebrew terminology, localization, and style review log. |
| `references/verification-log.md` | Web-validated Israeli source log with two-pass verification. |
| `health_insurance_claim_tracker/client.py` | Typed synchronous and asynchronous client implementation. |
| `health_insurance_claim_tracker/cli.py` | Typer-based CLI implementation. |
| `scripts/health_insurance_claim_tracker_client.py` | Underscored compatibility import module. |
| `scripts/health_insurance_claim_tracker_cli.py` | CLI wrapper. |
| `scripts/examples/` | Runnable scenario scripts. |
| `scripts/test_health_insurance_claim_tracker_client.py` | Pytest suite. |
| `pyproject.toml` | Installable project configuration and console entry point. |
| `requirements-dev.txt` | Development and test dependencies. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## Notes for production use

- Store only the identifiers needed for the operational workflow.
- Avoid full identity numbers unless a lawful and necessary purpose exists.
- Keep medical summaries in restricted folders.
- Redact exports before sharing them with advisers or external service providers.
- Verify current Israeli legal, insurance, privacy, and tax requirements before relying on operational deadlines or retention periods.
- Record gross receipt amounts. Do not calculate VAT automatically inside the tracker; the standard Israeli VAT rate was verified as 18% from 01/01/2025, but claim reimbursement and input-tax treatment depend on the payer, expense type, and accounting classification.
- For business files, store any Israel Invoice allocation number in notes or tags when relevant; this package does not validate Tax Authority allocation thresholds or API responses.
