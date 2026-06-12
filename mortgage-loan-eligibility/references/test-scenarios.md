# Test Scenarios

Use these concrete scenarios for acceptance testing and regression checks. Amounts are in ₪.

| # | Name | Property value | Loan | Status | Net income | Existing debt | Rate | Term | Expected |
|---:|---|---:|---:|---|---:|---:|---:|---:|---|
| 1 | Strong first-home borrower | 2,400,000 | 1,500,000 | single_home | 30,000 | 1,000 | 5.0% | 25 | Eligible |
| 2 | First home at LTV cap | 2,400,000 | 1,800,000 | single_home | 36,000 | 0 | 5.25% | 25 | Eligible or needs review |
| 3 | First home above LTV cap | 2,400,000 | 1,850,000 | single_home | 40,000 | 0 | 5.25% | 25 | Not eligible |
| 4 | Replacement home within cap | 3,000,000 | 1,950,000 | replacement_home | 42,000 | 3,500 | 5.6% | 30 | Eligible or needs review |
| 5 | Replacement home above cap | 3,000,000 | 2,200,000 | replacement_home | 55,000 | 0 | 5.2% | 30 | Not eligible |
| 6 | Investment within 50% | 2,000,000 | 1,000,000 | investment_property | 45,000 | 0 | 5.0% | 25 | Eligible |
| 7 | Investment above 50% | 2,000,000 | 1,200,000 | investment_property | 45,000 | 0 | 5.0% | 25 | Not eligible |
| 8 | DSR failure despite LTV pass | 2,400,000 | 1,500,000 | single_home | 9,000 | 0 | 5.0% | 25 | Not eligible |
| 9 | DSR review band | 2,400,000 | 1,600,000 | single_home | 20,000 | 0 | 5.0% | 25 | Needs review |
| 10 | Existing debt pressure | 2,400,000 | 1,400,000 | single_home | 25,000 | 6,500 | 5.0% | 25 | Needs review or not eligible |
| 11 | Equity shortfall | 2,400,000 | 1,500,000 | single_home | 30,000 | 0 | 5.0% | 25 | Not eligible with ₪100,000 cash equity |
| 12 | Sufficient equity | 2,400,000 | 1,500,000 | single_home | 30,000 | 0 | 5.0% | 25 | Eligible with ₪900,000 cash equity |
| 13 | Zero interest | 1,800,000 | 1,000,000 | single_home | 20,000 | 0 | 0.0% | 20 | Eligible if DSR passes |
| 14 | High-rate stress | 1,800,000 | 1,000,000 | single_home | 20,000 | 0 | 8.0% | 20 | Needs review or not eligible |
| 15 | Short-term stress | 1,800,000 | 1,000,000 | single_home | 20,000 | 0 | 5.0% | 10 | Needs review or not eligible |
| 16 | Longer-term relief | 1,800,000 | 1,000,000 | single_home | 20,000 | 0 | 5.0% | 30 | Eligible or needs review |
| 17 | Six-month freelancer | 1,800,000 | 1,100,000 | single_home | income records | 2,200 | 5.4% | 25 | Needs review when history is thin |
| 18 | No verified income | 1,800,000 | 1,100,000 | single_home | unverified only | 0 | 5.4% | 25 | Validation error |
| 19 | Mixed tracks valid | 2,500,000 | 1,500,000 | single_home | 33,000 | 1,500 | mixed | 25 | Calculate track payments |
| 20 | Mixed tracks sum mismatch | 2,500,000 | 1,500,000 | single_home | 33,000 | 1,500 | mixed | 25 | Validation error |
| 21 | Appraisal gap | 2,300,000 | 1,750,000 | single_home | 35,000 | 0 | 5.2% | 25 | Near or above cap |
| 22 | Gifted equity pending | 2,200,000 | 1,500,000 | single_home | 29,000 | 0 | 5.1% | 25 | Needs review until documented |
| 23 | Foreign income | 2,000,000 | 1,300,000 | single_home | 27,000 equivalent | 0 | 5.3% | 25 | Needs review |
| 24 | New job | 2,000,000 | 1,300,000 | single_home | 26,000 | 0 | 5.3% | 25 | Needs review |
| 25 | Replacement fallback as investment | 3,000,000 | 1,950,000 | investment_property | 42,000 | 3,500 | 5.6% | 30 | Not eligible |

## Detailed payloads

### Scenario 1

```json
{
  "property_value": 2400000,
  "requested_loan_amount": 1500000,
  "property_status": "single_home",
  "net_monthly_income": 30000,
  "existing_monthly_debt": 1000,
  "annual_rate": 5.0,
  "term_years": 25,
  "cash_equity": 900000
}
```

### Scenario 7

```json
{
  "property_value": 2000000,
  "requested_loan_amount": 1200000,
  "property_status": "investment_property",
  "net_monthly_income": 45000,
  "existing_monthly_debt": 0,
  "annual_rate": 5.0,
  "term_years": 25
}
```

### Scenario 17

```json
{
  "property_value": 1800000,
  "requested_loan_amount": 1100000,
  "property_status": "single_home",
  "income_records": [
    {"period": "2025-01", "net_income": 18500, "verified": true},
    {"period": "2025-02", "net_income": 21000, "verified": true},
    {"period": "2025-03", "net_income": 16500, "verified": true},
    {"period": "2025-04", "net_income": 23000, "verified": true},
    {"period": "2025-05", "net_income": 19000, "verified": true},
    {"period": "2025-06", "net_income": 19500, "verified": true}
  ],
  "existing_monthly_debt": 2200,
  "annual_rate": 5.4,
  "term_years": 25
}
```

### Scenario 19

```json
{
  "property_value": 2500000,
  "requested_loan_amount": 1500000,
  "property_status": "single_home",
  "net_monthly_income": 33000,
  "existing_monthly_debt": 1500,
  "tracks": [
    {"name": "fixed_unlinked", "principal": 500000, "annual_rate": 4.9, "term_years": 25},
    {"name": "prime", "principal": 500000, "annual_rate": 5.4, "term_years": 25},
    {"name": "variable_cpi", "principal": 500000, "annual_rate": 4.7, "term_years": 25}
  ]
}
```

## Acceptance checks

- Every not-eligible result contains at least one reason.
- Every review result contains at least one warning.
- LTV cap selection changes when property status changes.
- DSR decreases when income rises and all other inputs remain constant.
- DSR increases when existing debt rises and all other inputs remain constant.
- Maximum loan by DSR decreases when interest rate rises.
- Track totals must match the requested loan.
- JSON output must be valid UTF-8 and preserve the ₪ symbol.
