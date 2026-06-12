# withholding-tax-compliance-enhanced v0.3.0

A conservative Israeli supplier withholding-tax compliance package for calculating withholding from explicit supplier certificate data and preparing auditable staging rows for Form 856 workflows.

## What changed in v0.3.0

The web-validated pass corrected the risky premise that a package can safely calculate supplier withholding solely from supplier category. The current implementation requires a supplier-specific certificate snapshot or explicit accountant-approved rate before calculation.

## What this package does

- Calculates withholding using a supplier certificate rate.
- Supports the current standard Israeli VAT rate of 18% from 2025-01-01 onward.
- Produces a CSV staging file for Form 856 preparation and reconciliation.
- Provides an operational checklist for official Form 856 submission and confirmation.
- Lists official Tax Authority service URLs for report upload, confirmation, certificate lookup, logical tests, and API information.

## What this package does not do

- It does not submit Form 856 automatically.
- It does not claim a public unauthenticated API endpoint for annual Form 856 filing.
- It does not hard-code supplier category withholding-rate tables.
- It does not replace the official Tax Authority 856 file structure or logical-tests simulator.

## Example

```bash
python scripts/generate_856.py \
  --payments examples/supplier_payments.csv \
  --certificates examples/certificates.json \
  --out /tmp/form856-staging.csv
```

## Required official flow

1. Capture supplier certificate data close to payment.
2. Calculate and reconcile withholding against bookkeeping and periodic deduction reports.
3. Generate the official file according to the current Tax Authority 856 specification.
4. Run the official 126/856 logical-tests simulator.
5. Upload through the Tax Authority 126/856 service or approved representative/SHAAM channel.
6. Complete the separate submission-confirmation step and retain the confirmation.

## Legal/tax disclaimer

This package provides technical validation and calculation helpers only. It is not tax advice, legal advice, or a certified filing system. Significant filing decisions should be reviewed by an Israeli CPA, tax advisor, or authorized representative.
