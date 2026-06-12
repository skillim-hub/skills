# Troubleshooting

## Installation problems

### `hict` command is not found

Cause: the package was not installed in editable mode or the virtual environment is inactive.

Fix:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

### Development dependencies are missing

Cause: pytest or pytest-asyncio was not installed.

Fix:

```bash
pip install -r requirements-dev.txt
```

## Storage problems

### Records disappear between commands

Cause: commands are using different storage paths.

Fix:

```bash
export HICT_STORAGE_PATH="$HOME/.hict/claims.json"
hict --env production --storage "$HICT_STORAGE_PATH" list
```

### JSON file is corrupted

Cause: manual edits, interrupted writes outside the client, or wrong file content.

Fix:

1. Stop writing to the file.
2. Copy the corrupted file for investigation.
3. Restore the latest backup.
4. Run `python -m json.tool claims.json` to verify syntax.
5. Re-enter only missing claims from confirmations and source documents.

## Claim validation problems

### Date format rejected

Accepted formats:

- `DD/MM/YYYY`
- `DD-MM-YYYY`
- `YYYY-MM-DD`

Avoid mixed values such as `31.05.2026`.

### Service date is in the future

The client rejects future service dates to prevent accidental entry of appointment dates instead of completed service dates. Enter the actual date the service was provided.

### Submission date is before service date

Correct either the service date or the submission date. For prior approval, record the approval document as a document, not as a claim submission.

### Policy last four digits rejected

Use digits only. Do not include spaces, dashes, or letters.

## Document problems

### Missing document remains missing after upload

The document type must match the required checklist value. Use the exact term returned by `missing_documents`.

Example:

```bash
hict document "$CLAIM_ID" --name referral.pdf --document-type medical_referral_or_summary
```

### Supplier gave only a credit-card slip

Request a tax invoice or receipt. Keep the credit-card slip as payment proof, not as the main tax document.

### Medical summary includes sensitive information

Store it in a protected folder and share only with parties that need it. Use redacted JSON exports for operational review.

## Reimbursement problems

### Claim changes to paid after reimbursement

The status changes to `paid` when total reimbursements cover the claimed amount. If further action is still needed, update the status manually and add a note.

### Partial payment does not close the claim

This is expected. The tracker keeps the reimbursement gap open so an appeal or write-off decision can be documented.

### Bank deposit differs from approval letter

Record the actual bank deposit as reimbursement. Add the approval letter as a document and keep the gap until reconciled.

## Import and export problems

### CSV import fails

Fix:

1. Export a sample CSV.
2. Keep the same header row.
3. Use UTF-8 encoding.
4. Keep dates in accepted formats.
5. Ensure amounts use decimal numbers without currency signs.

### Redacted export still contains sensitive details in notes

Redaction masks the claimant reference only. Review notes, descriptions, document names, and tags before sharing externally.

## Operational escalation

Escalate when:

- No response is received by the follow-up date.
- The same document is requested repeatedly.
- A rejection reason conflicts with written policy terms.
- A partial approval is not explained clearly.
- A privacy incident may have occurred.
- A business record is needed for tax filing and the claim remains unresolved.

Record every escalation date, channel, recipient, and confirmation number.


### VAT or invoice allocation dispute

The tracker stores claim amounts and reimbursement amounts. It does not decide whether VAT applies, whether input VAT can be deducted, or whether an Israel Invoice allocation number is required. Keep the supplier document, record the allocation number in notes when present, and send the exported CSV to the bookkeeping workflow.
