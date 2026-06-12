# Migration Checklist

Use this checklist when moving from spreadsheets, insurer portal notes, or the previous package layout.

## From v1 package layout to v2

- Remove hyphenated Python module filenames from import paths.
- Import from the installable package:

```python
from health_insurance_claim_tracker import HealthInsuranceClaimTrackerClient
```

- Use `scripts/health_insurance_claim_tracker_client.py` only as a compatibility reference.
- Use the console entry point after installation:

```bash
pip install -e .
hict --env sandbox summary
```

- Replace any direct file execution of hyphenated client files with package imports.

## From spreadsheet tracking

1. Export the spreadsheet as CSV.
2. Rename columns to the expected import headers.
3. Convert dates to `YYYY-MM-DD`, `DD/MM/YYYY`, or `DD-MM-YYYY`.
4. Remove currency symbols from amount columns.
5. Use internal claimant references instead of full identity numbers.
6. Import into a sandbox storage file.
7. Compare totals with the spreadsheet.
8. Correct rejected rows.
9. Back up the original spreadsheet.
10. Move production work to the JSON store only after totals match.

## From insurer portal notes

1. Download claim confirmations and payment notices.
2. Create one tracker claim per payer route.
3. Add confirmation numbers to notes.
4. Add document names that match saved files.
5. Record actual bank deposits as reimbursements.
6. Add follow-up dates for open items.
7. Export CSV for operational review.

## From mixed household and business records

1. Separate personal household claims from business-relevant claims.
2. Use tags such as `household`, `self-employed`, or `bookkeeping`.
3. Redact sensitive details before giving files to external advisers.
4. Keep source documents in separate folders if access rules differ.
5. Reconcile business reimbursements against bank records before tax filing.

## Data protection migration checks

- Minimize personal identifiers.
- Remove full identity numbers where unnecessary.
- Restrict storage folder permissions.
- Back up encrypted or access-controlled copies.
- Document who may access medical summaries.
- Review retention requirements before deleting historical files.
