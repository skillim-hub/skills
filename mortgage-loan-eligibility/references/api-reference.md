# Reference: Israeli Mortgage Rules, Data Sources, and Local Interface

This is a non-API skill. It does not call a public eligibility endpoint, submit borrower data, retrieve credit data, or return a lender decision. Use the reference below to validate official sources and to integrate the local calculator safely.

## Israeli official sources and rules to validate

Validate the current text before production use. Lenders can apply stricter rules than baseline constraints.

| Area | Source to validate | Use in this package | Operational note |
|---|---|---|---|
| Housing-loan LTV restrictions | Bank of Israel, Banking Supervision Department housing-loan directives and macroprudential restrictions | Default caps: 75% single home, 70% replacement home, 50% additional or investment property | Confirm current caps, exceptions, and transition rules |
| Payment-to-income limits | Bank of Israel Banking Supervision Directive 329 and lender credit policy | Package label: DSR. Official terminology: payment-to-income or שיעור החזר מהכנסה. Default review threshold 40%; hard screen 50% | Lender policy may reject earlier or require exception approval |
| Mortgage track, variable-rate, and term rules | Bank of Israel Directives 329 and 451 | Review guidance for mixed tracks, variable rates, CPI linkage, stress testing, and 30-year standard term cap | Confirm current exceptions and product-specific rules |
| Property status and purchase tax | Israel Tax Authority and real-estate taxation documents | Select `property_status` and warn about replacement-home risk | Confirm single home, replacement home, or additional home legally |
| Credit data | Credit Data Law and Bank of Israel credit data procedures | Privacy and underwriting context only | This package does not access credit data |
| Source of funds | Prohibition on Money Laundering framework and bank compliance procedures | Warn about gifted equity and unexplained transfers | Treat undocumented funds as unavailable |
| Consumer disclosure | Banking consumer-protection requirements and lender disclosure forms | Frame output as preliminary screening | Do not describe output as approval in principle |

## No official public eligibility API

No universal public Israeli endpoint or webhook returns a binding mortgage eligibility decision for a private borrower. Production systems typically combine lender policy, borrower consent, credit checks, appraisals, account activity, property documents, and manual underwriting. This package therefore exposes a local deterministic interface.

## Python request example

```python
from mortgage_loan_eligibility_client import MortgageEligibilityClient

result = MortgageEligibilityClient().calculate({
    "property_value": 2400000,
    "requested_loan_amount": 1680000,
    "property_status": "single_home",
    "net_monthly_income": 28000,
    "existing_monthly_debt": 1500,
    "annual_rate": 5.25,
    "term_years": 25,
    "cash_equity": 720000
})
print(result.to_json())
```

## Async request example

```python
import asyncio

async def main():
    from mortgage_loan_eligibility_client import MortgageEligibilityClient

    client = MortgageEligibilityClient()
    result = await client.acalculate({
        "property_value": 2000000,
        "requested_loan_amount": 1000000,
        "property_status": "investment_property",
        "net_monthly_income": 42000,
        "annual_rate": 5.0,
        "term_years": 20
    })
    print(result.status.value)

asyncio.run(main())
```

## CLI request example

```bash
mortgage-loan-eligibility calculate \
  --property-value 2400000 \
  --loan-amount 1680000 \
  --status single_home \
  --net-income 28000 \
  --existing-debt 1500 \
  --annual-rate 5.25 \
  --term-years 25 \
  --cash-equity 720000 \
  --json
```

## JSON request schema

```json
{
  "property_value": 2400000,
  "requested_loan_amount": 1680000,
  "property_status": "single_home",
  "net_monthly_income": 28000,
  "existing_monthly_debt": 1500,
  "annual_rate": 5.25,
  "term_years": 25,
  "dsr_limit": 50,
  "dsr_review_threshold": 40,
  "cash_equity": 720000
}
```

| Field | Type | Required | Validation |
|---|---|---:|---|
| `property_value` | number | Yes | Greater than 0 |
| `requested_loan_amount` or `loan_amount` | number | Yes | 0 or greater; not above property value |
| `property_status` or `status` | string | Yes | `single_home`, `replacement_home`, `investment_property` |
| `net_monthly_income` | number | Conditional | Required when `income_records` is absent |
| `income_records` | array | Conditional | Required when `net_monthly_income` is absent |
| `existing_monthly_debt` | number | No | 0 or greater. Use for fixed monthly obligations and lender-policy debt adjustments; the official housing-loan PTI definition focuses on monthly housing-loan repayment, prior loans secured by the same property, and fixed expenses. |
| `cash_equity` | number | No | 0 or greater |
| `annual_rate` | number | No | Accepts `5.25` or `0.0525`; not negative |
| `term_years` | integer | No | 1-30 under the standard housing-loan repayment-period cap |
| `dsr_limit` | number | No | Accepts `50` or `0.50`; above 0 and up to 1 |
| `dsr_review_threshold` | number | No | Above 0 and no higher than `dsr_limit` |
| `tracks` | array | No | Sum of principals must equal requested loan within ₪1 |

## Income record schema

```json
{
  "period": "2025-01",
  "net_income": 21000,
  "verified": true,
  "weight": 1.0
}
```

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `period` | string | Yes | Month or period label; use `YYYY-MM` or `MM-YYYY` consistently |
| `net_income` | number | Yes | Net monthly income available for repayment |
| `verified` | boolean | No | Only verified records are used |
| `weight` | number | No | Positive weighting factor |

## Track schema

```json
{
  "name": "fixed_unlinked",
  "principal": 600000,
  "annual_rate": 4.8,
  "term_years": 25,
  "interest_only_months": 0
}
```

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `name` | string | Yes | Track label |
| `principal` | number | Yes | Track principal in ₪ |
| `annual_rate` | number | No | Annual interest |
| `term_years` | integer | No | Track term |
| `interest_only_months` | integer | No | Grace period; amortizing payment after grace is reported. Validate balloon or bullet structures separately before production use. |

## JSON response example

```json
{
  "status": "needs_review",
  "property_status": "single_home",
  "property_value": 2400000.0,
  "requested_loan_amount": 1680000.0,
  "ltv_limit": 0.75,
  "ltv": 0.7,
  "required_equity": 720000.0,
  "provided_cash_equity": 720000.0,
  "net_monthly_income_used": 28000.0,
  "estimated_monthly_payment": 10065.62,
  "existing_monthly_debt": 1500.0,
  "dsr_limit": 0.5,
  "dsr_review_threshold": 0.4,
  "dsr": 0.41305785714285713,
  "max_loan_by_ltv": 1800000.0,
  "max_monthly_payment_by_dsr": 12500.0,
  "max_loan_by_dsr": 2085654.41,
  "binding_constraint": "ltv",
  "reasons": [],
  "warnings": [
    "DSR is above the review threshold and may require stronger income evidence or lender exception handling."
  ],
  "recommendations": [
    "Prepare bank statements, tax assessments, current accountant confirmation, and explanations for variable income."
  ],
  "track_payments": [
    {
      "name": "default",
      "principal": 1680000.0,
      "annual_rate": 0.0525,
      "term_years": 25.0,
      "monthly_payment": 10065.62
    }
  ]
}
```

## Error table

| Error text | Cause | Fix |
|---|---|---|
| `property_value is required` | Missing property value | Supply purchase price or accepted valuation |
| `property_value must be greater than 0` | Zero or negative property value | Correct input |
| `requested_loan_amount must not exceed property_value` | Requested loan above asset value | Lower loan or correct property value |
| `property_status must be one of...` | Unknown status | Use `single_home`, `replacement_home`, or `investment_property` |
| `provide net_monthly_income or income_records` | No repayment-capacity input | Add net income or verified records |
| `annual_rate appears too high after normalization` | Rate likely entered as `525` | Use `5.25` for 5.25% |
| `term_years must be between 1 and 30` | Unsupported term | Use an allowed term |
| `dsr_review_threshold must be greater than 0 and up to dsr_limit` | Review threshold exceeds hard limit | Adjust thresholds |
| `sum of tracks.principal must equal requested_loan_amount within ₪1` | Track total mismatch | Align track principals |
| `at least one verified income record is required` | All records unverified | Verify supported records |

## Production configuration example

```json
{
  "ltv_limits": {
    "single_home": 0.75,
    "replacement_home": 0.70,
    "investment_property": 0.50
  },
  "dsr_review_threshold": 0.40,
  "dsr_limit": 0.50,
  "max_term_years": 30,
  "stress_rate_add_on": 0.015
}
```

Store active policy version, verification date, and timestamp with every production result.
