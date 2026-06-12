# Workflow Guide

## Workflow 1: Freelancer monthly bookkeeping prep

1. Export the business bank statement as CSV.
2. Save the original as `statements/2026-01-bank.csv`.
3. Run:
   ```bash
   python scripts/bank-transaction-categorizer-cli.py categorize statements/2026-01-bank.csv --output work/2026-01-categorized.csv
   ```
4. Sort by `confidence`.
5. Review all wallet transfers, personal-risk expenses, uncategorized rows, and aggregate card debits.
6. Add recurring client and supplier rules to `rules/freelancer-rules.json`.
7. Rerun with:
   ```bash
   python scripts/bank-transaction-categorizer-cli.py categorize statements/2026-01-bank.csv --rules rules/freelancer-rules.json --output final/2026-01-categorized.csv
   ```
8. Send source file, categorized output, and documentation to the accountant.

Acceptance criteria: no invalid rows, all low-confidence items reviewed, card settlements reconciled, VAT-relevant lines backed by documents.

## Workflow 2: Small-business cash-flow review

1. Export current-account activity for the period.
2. Categorize the file to JSON.
3. Compare income credits against invoices.
4. Compare tax, rent, payroll, and loan debits against expected obligations.
5. Flag unexpected fees, duplicate charges, cash withdrawals, and missing recurring charges.
6. Save output with review date.

## Workflow 3: Household budget

1. Export household account transactions.
2. Categorize the file.
3. Treat tax fields as metadata only.
4. Review supermarket, pharmacy, cash, and wallet lines.
5. Track recurring subscriptions and municipal charges.
6. Create a household-specific rules file for stable patterns.

## Workflow 4: Credit-card reconciliation

1. Categorize bank statement.
2. Filter `Credit Card Settlement`.
3. Export detailed card activity for the same card/month.
4. Categorize card detail separately.
5. Compare detailed sum against aggregate debit.
6. Explain differences: refunds, installments, foreign currency, fees, or cutoff dates.
7. Avoid counting both aggregate and detailed rows as expenses.

## Workflow 5: Year-end cleanup

1. Combine monthly outputs.
2. Confirm full-year coverage.
3. Remove duplicate imports.
4. Review `Uncategorized`, `Personal/Review`, and low-confidence rows.
5. Confirm owner transfers and capital injections.
6. Reconcile payroll, pension, National Insurance, VAT, and income-tax advances.
7. Export final category totals.
8. Archive source files, rules, manual overrides, and approval notes.

## Workflow 6: Custom-rule hardening

1. Sort by normalized description.
2. Identify repeated merchants.
3. Add rules only for stable descriptions.
4. Use `direction` to prevent false positives.
5. Set higher `priority` for specific suppliers and clients.
6. Add a test for every high-value rule.
