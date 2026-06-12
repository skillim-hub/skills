# Workflow Guide

## Workflow 1: First household budget

### Goal

Create a practical monthly view for an Israeli household.

### Inputs

- Month in `MM-YYYY`
- Net salary and other income
- Rent or mortgage
- Arnona, electricity, water, gas, internet, mobile
- Groceries, delivery, restaurants
- Transport, insurance, healthcare, education, childcare
- Savings goal and current savings

### Steps

1. Create budget file.
2. Add income.
3. Add fixed expenses.
4. Add variable expenses.
5. Normalize non-monthly bills.
6. Add savings goals.
7. Calculate summary.
8. Review categories above plan.
9. Choose 3 actions for next month.

### Example command

```bash
python scripts/household-budget-planner-cli.py sample --output sample-budget.json
python scripts/household-budget-planner-cli.py summary sample-budget.json --month 05-2026
```

## Workflow 2: Freelancer cash-flow split

### Goal

Separate business cash from household money.

### Inputs

- Gross collections
- VAT status and VAT rate when relevant
- Business expenses
- Accountant-provided reserve percentage if available
- Desired household transfer
- Upcoming VAT, income-tax, and Bituach Leumi dates

### Steps

1. Record gross collections.
2. Mark VAT-inclusive receipts.
3. Extract VAT component.
4. Add tax and Bituach Leumi reserve placeholders.
5. Tag business expenses separately.
6. Set owner draw.
7. Transfer only owner draw to household budget.
8. Keep business buffer.

### Rule

If VAT is collected, do not count it as household income.

## Workflow 3: Credit-card audit

### Goal

Find leaks, duplicate subscriptions, and installment pressure.

### Steps

1. Import credit-card CSV.
2. Deduplicate overlapping exports.
3. Remove internal transfers.
4. Split groceries, delivery, and restaurants.
5. Mark installments.
6. Group by vendor.
7. Detect recurring charges.
8. Report top 10 vendors.
9. Set next month category caps.

### Red flags

- “Other” above 5%.
- Duplicate subscriptions.
- Installments above discretionary budget.
- Large cash withdrawals without receipts.
- Refunds counted as income.

## Workflow 4: Emergency fund

### Goal

Calculate required monthly contribution.

### Steps

1. Confirm target amount.
2. Confirm current balance.
3. Confirm due date.
4. Calculate gap.
5. Calculate months remaining.
6. Compare contribution to surplus.
7. Automate transfer when feasible.

### Example

```text
Target: ₪30,000
Current: ₪18,000
Gap: ₪12,000
Due date: 31-12-2026
Required monthly contribution: about ₪1,500
Status: feasible if monthly surplus stays above ₪1,500
```

## Workflow 5: Annual sinking funds

### Goal

Prevent annual payments from breaking monthly cash flow.

### Steps

1. List annual or irregular expenses.
2. Record amount and due month.
3. Divide by months until due.
4. Add monthly sinking-fund line.
5. Track actual payment month separately.

### Example

```text
Car insurance: ₪4,800 due 01-09-2026
Start: 05-2026
Months remaining: 4
Monthly sinking fund: ₪1,200
```

## Workflow 6: Shared household

### Goal

Budget fairly for partners, roommates, or family members.

### Steps

1. Tag joint and personal expenses.
2. Add payer.
3. Add split percentage.
4. Record reimbursements as transfers, not income.
5. Reconcile monthly.
6. Keep personal discretionary budgets separate.

## Workflow 7: Monthly review

### Agenda

1. Review actual income.
2. Review category variances.
3. Review credit-card liabilities.
4. Review savings goals.
5. Approve one structural change.
6. Approve two small changes.
7. Set next month caps.
