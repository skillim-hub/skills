# Troubleshooting

## Hebrew text appears corrupted

Cause: encoding mismatch, usually Windows-1255 vs UTF-8. Re-export the bank file, prefer UTF-8 with BOM when available, and avoid spreadsheet resave before parsing.

## Amounts have the wrong sign

Cause: debit/credit headers were renamed or a spreadsheet removed minus signs. Keep headers such as `חובה`, `זכות`, `debit`, and `credit`. Compare total debit and credit against the bank export.

## Dates fail to parse

Supported formats: `DD-MM-YYYY`, `DD/MM/YYYY`, `YYYY-MM-DD`, `YYYY/MM/DD`, and `DD.MM.YYYY`. Normalize mixed files before import.

## Too many uncategorized rows

Cause: local suppliers, terminal identifiers, or aggregate card lines. Sort by `normalized_description`, add custom rules for recurring descriptions, and import card detail.

## BIT or PayBox is unclear

Wallet descriptions lack context. Add rules only for known recurring clients. Leave unknown wallet lines flagged for review.

## VAT relevance looks too broad

`vat_relevant` means the item may need invoice/receipt review. It does not mean input VAT is recoverable.

## Credit-card settlements look duplicated

Keep the bank aggregate line as a settlement. Categorize detailed card transactions separately and reconcile sums.

## Duplicate flags are noisy

Same-day recurring items can look identical. Review flags manually and use references when available.

## Custom rule does not match

Check JSON syntax, escaped quotes, `patterns` list, direction, and priority. Match text that appears in the normalized description.

## Production incident checklist

1. Stop using affected output.
2. Preserve source statement and rules file.
3. Record command and version.
4. Identify parsing, matching, duplicate, or override issue.
5. Add a test scenario.
6. Fix and rerun all tests.
7. Regenerate output and document the correction.
