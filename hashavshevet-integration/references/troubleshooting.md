# Troubleshooting

Use this checklist before changing mappings or retrying production imports.

## Triage order

1. Confirm the target company ID and environment.
2. Preserve the raw input file or original API payload.
3. Identify the operation type: customer/supplier sync, journal pull, document import, BTKN generation, OPENFORMAT handoff, or allocation-number request.
4. Validate encoding, dates, VAT numbers, and money fields.
5. Reconcile record counts and totals.
6. Retry only after the root cause is known.

## Encoding failures

| Symptom | Diagnosis | Fix |
|---|---|---|
| Hebrew appears as gibberish | Windows-1255 or ISO-8859-8 opened as UTF-8 | Read the raw file with automatic detection, then write UTF-8 staging output. |
| Question marks replace Hebrew | File was converted with lossy settings | Return to the raw export and reconvert. |
| Excel shows broken Hebrew | UTF-8 CSV lacks BOM | Use UTF-8 BOM CSV for analyst-facing files. |
| Import rejects Hebrew names | Target expects Windows-1255 | Write target import files with the encoding required by the target interface. |

## Journal-entry failures

| Symptom | Cause | Fix |
|---|---|---|
| Entry is not balanced | Missing VAT, rounding drift, or partial data | Reject the entry and compare source document totals. |
| VAT line is wrong | Historical rate or special VAT treatment ignored | Determine VAT rate by invoice date and document type. |
| Duplicate reference | Source sent the same invoice twice | Use idempotency key: company ID plus document type plus source document number. |
| Unmapped account | Customer, supplier, income, expense, or VAT account missing | Add mapping in configuration and re-run staging. |

## Customer and supplier sync failures

| Symptom | Cause | Fix |
|---|---|---|
| Duplicate customer | Different account IDs for the same VAT number | Normalize VAT number and maintain a cross-reference table. |
| Supplier overwrites customer | Shared account ID namespace | Prefix external IDs or keep separate account namespaces. |
| Missing customer VAT number | Private consumer or incomplete B2B record | Mark as consumer flow or block B2B invoice allocation. |
| Wrong payment terms | Default applied across companies | Store payment terms per company and account type. |

## Allocation-number failures

| Symptom | Cause | Fix |
|---|---|---|
| Allocation required but missing | Net amount exceeds threshold and document is a B2B tax invoice | Submit through the approved SHAAM flow before delivery. |
| SHAAM rejects payload | Missing invoice or customer details | Run `validate-invoice` and resubmit after correction. |
| User lacks permission | Token was not authorized by an eligible company user | Recreate authorization under the correct company. |
| Duplicate submission concern | Network timeout after submission | Check status or idempotency records before sending again. |

## Multi-company failures

| Symptom | Cause | Fix |
|---|---|---|
| Data sent to wrong company | Shared token or folder | Split secrets and folders by company ID. |
| Wrong VAT rate applied | Global configuration used | Store VAT rate in the company config and evaluate by invoice date. |
| Mixed customer identifiers | Shared customer master without company scoping | Use `(company_id, external_id)` as the key. |
| Archive is incomplete | Files overwritten between companies | Use a company/date/import-id archive path. |

## BTKN and file bundle failures

| Symptom | Cause | Fix |
|---|---|---|
| Target rejects BTKN text | Target expects a different import structure | Confirm the accepted production format and adjust the adapter. |
| Hebrew fails in BTKN | Wrong target encoding | Generate Windows-1255 unless the target requires UTF-8. |
| Missing allocation number | Source invoice lacks approved number | Block export for qualifying B2B tax invoices until resolved. |
| Record count mismatch | Input JSON filtered rows unexpectedly | Compare input row count to generated row count and rejected-row log. |

## Escalation packet

Collect these items before escalation:

- Company ID and target environment.
- Source filename or payload ID.
- Import batch ID.
- Command or endpoint path used.
- Raw input checksum.
- Staging output checksum.
- Rejected-row report.
- Accountant-approved account mapping.
- Exact error message and timestamp.
