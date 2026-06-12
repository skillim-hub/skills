# Test Scenarios

Use these scenarios to validate calculations, conversation handling, and professional handoff.

## Scenario 1: Simple apartment, no CPI

- Purchase: 2010-01-01
- Sale: 2025-01-01
- Purchase price: ₪1,000,000
- Sale price: ₪2,000,000
- Costs: none
- Expected: positive gain, linear share applies if qualifying.

## Scenario 2: Apartment with costs

- Purchase costs: ₪70,000
- Improvements: ₪180,000
- Sale costs: ₪50,000
- Expected: taxable gain lower than Scenario 1.

## Scenario 3: Apartment with CPI

- CPI purchase: 80
- CPI sale: 100
- Expected: real gain lower than gross gain.

## Scenario 4: Commercial office with depreciation

- Purchase: ₪900,000
- Improvements: ₪100,000
- Depreciation: ₪200,000
- Sale: ₪1,500,000
- Expected: adjusted basis reduced by depreciation; warning for business-use review.

## Scenario 5: Commercial shop without depreciation data

- Property type: commercial
- Depreciation omitted
- Expected: warning asking for depreciation review.

## Scenario 6: Sale before purchase

- Purchase date: 2025-01-01
- Sale date: 2024-01-01
- Expected: validation error.

## Scenario 7: Same-day purchase and sale

- Purchase date: 2025-01-01
- Sale date: 2025-01-01
- Expected: validation error because holding period must be positive.

## Scenario 8: Negative cost

- Sale costs: -5000
- Expected: validation error.

## Scenario 9: Invalid ownership share

- Ownership share: 1.2
- Expected: validation error.

## Scenario 10: Half ownership

- Ownership share: 0.5
- Expected: seller amounts are half of property-level amounts.

## Scenario 11: Loss

- Adjusted basis: ₪2,000,000
- Net sale proceeds: ₪1,800,000
- Expected: estimated tax zero, loss warning.

## Scenario 12: CPI base mismatch suspicion

- CPI purchase: 140
- CPI sale: 70
- Expected: warning that CPI sale is lower than purchase; real gain may be overstated.

## Scenario 13: Only purchase CPI supplied

- CPI purchase: 80
- CPI sale: null
- Expected: validation error.

## Scenario 14: Pre-2014 sale

- Purchase: 2000-01-01
- Sale: 2013-12-31
- Expected: linear taxable share zero under default relief-date model; professional verification warning.

## Scenario 15: Post-2014 purchase

- Purchase: 2020-01-01
- Sale: 2025-01-01
- Expected: linear taxable share 100% under simple model.

## Scenario 16: Inherited apartment

- Ownership share: 0.5
- Exemption: inherited_apartment
- Missing deceased facts
- Expected: no automatic exemption; warning.

## Scenario 17: Gifted apartment

- Exemption: gift_continuity
- Donor basis missing
- Expected: continuity warning.

## Scenario 18: Foreign resident apartment seller

- Seller residency: foreign_resident
- Expected: foreign-resident warning.

## Scenario 19: Mixed-use apartment

- Property type: mixed_use
- Qualifying residential true
- Expected: business-use warning and no blind full exemption.

## Scenario 20: Betterment levy included

- Sale costs include ₪120,000 betterment levy
- Expected: lower net sale proceeds, document check.

## Scenario 21: Urban renewal transaction

- Property type: other
- Notes mention Tama 38
- Expected: advanced review required.

## Scenario 22: Entity seller

- Seller type: company
- Tax rate: 0.23
- Expected: company/professional review warning.

## Scenario 23: Tax rate changed by user

- Tax rate: 0.30
- Expected: estimated tax uses 30% and assumptions state it.

## Scenario 24: Full exemption scenario

- Exemption code: single_apartment
- User has strong eligibility facts
- Expected: output can show tax as scenario only; do not auto-file.

## Scenario 25: Rounding

- Fractional ownership: 0.333333
- Expected: output rounded consistently but raw JSON preserves decimals.
