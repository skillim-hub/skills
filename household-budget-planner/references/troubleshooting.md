# Troubleshooting

## Imported total differs from bank total

Likely causes:

- Pending card transactions missing.
- Refunds imported as income.
- Duplicate rows from overlapping export dates.
- Transfers counted as expenses.
- Foreign-currency settlement date differs from purchase date.

Fix:

1. Compare imported total with source statement.
2. Sort by date and amount.
3. Remove duplicates.
4. Tag transfers.
5. Convert refunds to refund-tagged entries.
6. Re-run summary.

## Dates fall into the wrong month

Likely causes:

- `YYYY-MM-DD` and `DD-MM-YYYY` mixed.
- Credit-card billing date differs from purchase date.
- Salary arrives after month end.

Fix:

1. Standardize output to `DD-MM-YYYY`.
2. Decide whether the budget follows calendar month or cash-flow cycle.
3. Keep purchase and billing dates when available.

## Savings rate looks too high

Likely causes:

- Tax reserves missing.
- Annual expenses missing.
- Installments missing.
- Gross business revenue treated as household income.

Fix:

1. Add reserve lines.
2. Add sinking funds.
3. Add installment payments.
4. Use owner draw instead of gross business deposits.

## Freelancer cannot pay VAT

Likely causes:

- VAT collected was spent.
- VAT-inclusive deposits counted as income.
- Business and household accounts mixed.

Fix:

1. Extract VAT from each VAT-inclusive receipt.
2. Move VAT component to reserve.
3. Use separate business account where possible.
4. Transfer stable owner draw only.

## Too many uncategorized transactions

Fix:

1. Add exact merchant rules first.
2. Add keyword rules second.
3. Review largest uncategorized transactions first.
4. Keep cash temporary until receipts exist.

## Category cap keeps failing

Fix:

1. Check last three months.
2. Split essential and discretionary subcategories.
3. Reduce by one realistic step.
4. Add holiday or event sinking fund.

## Warning signs

- Overdraft interest appears monthly.
- Debt payments exceed planned savings.
- Credit-card installments grow.
- Business reserves are missing.
- Cash withdrawals are large and unexplained.
- Paper surplus exists but balance falls.

## Recovery checklist

- [ ] Freeze new installments temporarily.
- [ ] List all debts and minimum payments.
- [ ] Cancel duplicate subscriptions.
- [ ] Add annual bills.
- [ ] Protect housing, food, healthcare, childcare, and utilities.
- [ ] Start a small automatic emergency transfer.
- [ ] Get qualified professional advice for tax, legal, pension, insurance, investment, and insolvency questions.
