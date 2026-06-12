# Migration Checklist

Use this checklist when replacing spreadsheets, ad-hoc calculators, or an older loan-planning package.

## 1. Inventory current models

- List all spreadsheets, templates, and scripts currently used for loan planning.
- Identify who owns each model.
- Note which models include CPI, prime, grace, balloon, and early-repayment logic.
- Mark models that contain hard-coded rates or outdated assumptions.

## 2. Map input fields

| Existing field | New field | Action |
|---|---|---|
| Loan amount | `principal` | Remove ₪ symbols and commas if needed |
| Term | `term_months` | Convert years to months |
| Start date | `start_date` | Use `DD/MM/YYYY` or `YYYY-MM-DD` |
| Interest rate | `annual_interest_rate` | Convert percent to decimal |
| Prime base | `prime_rate` | Enter explicit assumption |
| Prime spread | `prime_margin` | Use positive or negative decimal |
| CPI forecast | `annual_cpi_rate` | Use decimal |
| Setup fee | `origination_fee` | Enter as ₪ amount |
| Prepayment fee | `early_payment_fee` | Enter as ₪ amount |

## 3. Rebuild benchmark scenarios

Create at least five benchmark scenarios from previously approved decisions:

1. Fixed-rate loan.
2. Prime-linked loan.
3. CPI-linked loan.
4. Grace-period loan.
5. Balloon loan.

Run the new helper and compare outputs with prior workpapers.

## 4. Investigate differences

For each difference above the chosen tolerance, check:

- Daily versus monthly interest.
- CPI convention.
- Rounding.
- Embedded fees.
- Due-date rule.
- Actual versus assumed prime rate.
- Whether old models used percent values incorrectly.
- Whether old models ignored early repayments.

## 5. Update operating procedure

- Store scenario JSON beside each decision memo.
- Export CSV for approved scenarios.
- Require a source note for prime and CPI assumptions.
- Require stress cases for variable-rate or CPI-linked loans.
- Require review before client-facing use.

## 6. Train users

Cover:

- Decimal rate entry.
- Israeli date entry.
- Difference between interest and CPI adjustment.
- Interpretation of effective cash cost.
- When to escalate to accounting, tax, legal, or lender review.

## 7. Archive old models

- Mark old spreadsheets as superseded.
- Keep them read-only for audit history.
- Remove links from current templates.
- Document the cutover date.

## 8. Production readiness

- Pytest suite passes.
- CLI works on a clean machine.
- README quick start works as written.
- Hebrew and English guides are available.
- Neutral packaging and metadata have been verified.
- License uses the required neutral copyright line.
