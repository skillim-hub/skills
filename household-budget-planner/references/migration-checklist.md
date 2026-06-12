# Migration Checklist

## Scope

Migrate useful budgeting data only. Do not migrate branding, visual identity assets, organization names, distribution notes, or creator metadata.

## Files

- [ ] Root folder is `household-budget-planner`.
- [ ] English guide is `SKILL.md`.
- [ ] Hebrew guide is `SKILL_HE.md`.
- [ ] Reference material is under `references/`.
- [ ] Executable helpers are under `scripts/`.
- [ ] Examples are under `scripts/examples/`.
- [ ] Tests are under `scripts/test_household-budget-planner_client.py`.
- [ ] README, CHANGELOG, LICENSE, pyproject, and requirements-dev exist.

## Metadata

- [ ] Slug is `household-budget-planner`.
- [ ] Version is `2.0.0` or later.
- [ ] Author field is absent.
- [ ] Tags cover household, Israel, shekel, savings, VAT, freelancer, small business, cash flow, and consumer spending.
- [ ] License is MIT.

## Data mapping

| Old field | New field |
|---|---|
| Date | date |
| Amount | amount |
| Type | kind |
| Category | category |
| Notes | description |
| Merchant | vendor |
| Account | payment_method |
| Business | is_business |
| VAT | vat_included |
| Split percent | business_use_percent |
| Goal | savings_goal.name |

## Category cleanup

- [ ] Merge spelling variants.
- [ ] Split groceries, delivery, and restaurants when needed.
- [ ] Add arnona as its own category.
- [ ] Add VAT reserve and tax reserve for freelancers.
- [ ] Keep “other” below 5%.
- [ ] Add sinking funds for annual expenses.

## Validation

- [ ] Income total matches old file.
- [ ] Expense total matches after removing transfers.
- [ ] Refunds do not inflate income.
- [ ] Dates use `DD-MM-YYYY`.
- [ ] Amounts are in ₪.
- [ ] Savings goals include target, current, and due date.
- [ ] Business expenses are separated.
- [ ] VAT rate is configurable.

## Cutover

1. Keep a read-only copy of the old file.
2. Export migrated data to JSON.
3. Run tests.
4. Compare two months of summaries.
5. Correct mappings.
6. Start using the new structure from the next month.
