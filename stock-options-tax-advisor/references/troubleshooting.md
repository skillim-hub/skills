# Troubleshooting

## Capital-track grant is treated as ordinary income

Check whether the sale date is before the earliest preferred sale date. Check whether the holding-period anchor is correct. If trustee confirmation is missing, keep the warning and avoid giving a definitive capital-track conclusion.

## Income-track scenario fails

Add `fmv_at_exercise`. The model needs fair market value at exercise or release to split employment income from later appreciation.

## ESPP scenario fails

Add `fmv_at_purchase`. The purchase discount equals purchase-date fair market value less purchase price.

## Surtax looks unexpected

Check `other_annual_income`. Surtax is incremental and can be triggered by capital gain even when employment income is below the threshold.

## National Insurance is zero

Other annual income may already exceed the annual contribution cap. Confirm whether the income is employment income, self-employment income, capital income, or another category.

## Foreign-currency result is wrong

Check that all prices use the same original currency and that `fx_rate_to_ils` is positive. Use separate scenarios when exercise, purchase, vest, and sale dates require different exchange rates.

## Public-company split is missing

Set `public_at_grant=true` and provide `fmv_at_grant`. Without the FMV, the model flags the issue but cannot split the components.

## Documents conflict

Prefer trustee confirmation for plan track and release date, payroll records for employment income withholding, broker records for sale price and fees, and board or valuation records for private-company FMV.

## Web-validated rate refresh checklist

- Confirm the VAT rate only for business-context notes; do not add VAT to equity tax calculations.
- Refresh 2026 employee National Insurance and health contribution rates from National Insurance before production use.
- Confirm whether a new tax year has changed the surtax threshold, income brackets, reduced National Insurance bracket, or maximum National Insurance base.
- Treat Section 102 capital-track status as unconfirmed until the trustee, plan filing, grant agreement, and release date are documented.
