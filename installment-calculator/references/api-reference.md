# API and Regulation Reference

This skill is a local calculator and does not call an external service. Treat the Python package as the API. Supply any VAT rate, acquirer fee, or legal-text updates from controlled internal sources before production use.

## Web-validated Israeli regulation and official-source reference

Access date for this section: 2026-06-02. The package does not call these sources. Use them to validate operating policy before production.

| Area | Verified baseline | Source handling |
|---|---|---|
| VAT rate | 18% from 01/01/2025; treated as current in the 2026 validation pass | Keep `CURRENT_ISRAEL_VAT_RATE_PERCENT` configurable in consuming systems. |
| Consumer price display | Consumer-facing price should be total and include mandatory payments such as VAT | Keep `vat_included=True` for consumer flows unless the legal context clearly permits otherwise. |
| Cancellation fee cap | For qualifying statutory cancellation cases, use the lower of 5% of the transaction or ₪100 | Use `statutory_cancellation_fee_cap` only after confirming eligibility and exceptions. |
| Loan or credit disclosure | Credit offers may require disclosure of credit cost, actual/effective cost, maximum cost, arrears interest, fees, and other borrower costs | Treat calculator disclosure output as a checklist, not legal wording. |
| Israel Invoice allocation threshold | From 01/06/2026, allocation is required above ₪5,000 before VAT for relevant input-tax deduction workflows | This is an accounting workflow checkpoint, not an installment schedule input. |
| External endpoints and webhooks | None implemented | No API host, endpoint path, webhook event, credential, or callback is used by this package. |

### VAT helper examples

Request:

```python
from installment_calculator import gross_from_net, vat_components_from_gross

gross = gross_from_net("100")
components = vat_components_from_gross("118")
```

Response:

```json
{
  "gross": "118.00",
  "components": {
    "net_price": "100.00",
    "vat_amount": "18.00",
    "gross_price": "118.00",
    "vat_rate_percent": "18"
  }
}
```

### Cancellation fee cap helper

Request:

```python
from installment_calculator import statutory_cancellation_fee_cap

cap = statutory_cancellation_fee_cap("3000")
```

Response:

```json
{
  "cancellation_fee_cap": "100.00"
}
```

## Public Python API

Import from the installable package:

```python
from installment_calculator import InstallmentRequest, calculate_plan, estimate_refund
```

### Create a plan

Request:

```python
request = InstallmentRequest(
    cash_price="3600",
    installments=12,
    annual_interest_rate="7.5",
    upfront_fee="49",
    per_installment_fee="1.90",
    first_due_date="05/07/2026",
)
plan = calculate_plan(request)
```

Response shape:

```json
{
  "cash_price": "3600.00",
  "down_payment": "0.00",
  "financed_amount": "3600.00",
  "installments": 12,
  "annual_interest_rate": "7.5",
  "upfront_fee": "49.00",
  "per_installment_fee": "1.90",
  "regular_payment": "...",
  "total_interest": "...",
  "total_fees": "...",
  "total_payments": "...",
  "finance_charge": "...",
  "cost_above_cash_price": "...",
  "effective_annual_cost_percent": "...",
  "schedule": [
    {
      "number": 1,
      "due_date": "05/07/2026",
      "principal": "...",
      "interest": "...",
      "fee": "1.90",
      "payment": "...",
      "balance": "..."
    }
  ],
  "warnings": ["..."],
  "disclosure_checks": [
    {"code": "CASH_PRICE", "status": "ok", "message": "..."}
  ]
}
```

### Compare plans

Request:

```python
from installment_calculator import compare_plans

plans = compare_plans([
    InstallmentRequest(cash_price="2400", installments=3, annual_interest_rate="0"),
    InstallmentRequest(cash_price="2400", installments=12, annual_interest_rate="8.9", per_installment_fee="1.50"),
])
```

Response: list of `InstallmentPlan` objects sorted by total paid, then finance charge, then installment count.

### Estimate refund

Request:

```python
refund = estimate_refund(plan, installments_paid=4, cancellation_fee="0")
```

Response:

```json
{
  "installments_paid": 4,
  "paid_total": "...",
  "remaining_principal": "...",
  "remaining_scheduled_payments": "...",
  "cancellation_fee": "0.00",
  "estimated_settlement_before_legal_adjustments": "...",
  "note": "Use contract terms, current cancellation rules, card-acquirer policy, and bookkeeping guidance before issuing a refund or charge reversal."
}
```

## CLI API

### Calculate

```bash
installment-calculator --env sandbox calculate --price 3600 --installments 12 --annual-rate 7.5 --upfront-fee 49 --per-installment-fee 1.90 --first-due-date 05/07/2026 --output json
```

### Compare

```bash
installment-calculator compare --price 2400 --installments 3 --installments 12 --annual-rate 0 --annual-rate 8.9 --per-installment-fee 1.50
```

### Refund

```bash
installment-calculator refund --price 2400 --installments 12 --paid 4 --annual-rate 8.9 --per-installment-fee 1.50
```

## Error table

| Code | Trigger | Corrective action |
|---|---|---|
| `INVALID_DECIMAL` | Input cannot be parsed as a number | Pass a numeric string such as `1200.00` |
| `ROUNDING_MUST_BE_POSITIVE` | Rounding quantum is zero or negative | Use `0.01` unless a different accounting policy is approved |
| `PRICE_MUST_BE_POSITIVE` | Cash price is zero or negative | Use the immediate-payment price |
| `INSTALLMENTS_MUST_BE_POSITIVE` | Installment count is not a positive integer | Use 1 or more |
| `DOWN_PAYMENT_OUT_OF_RANGE` | Down payment is negative or equals the full price | Use a value lower than the cash price |
| `RATE_MUST_NOT_BE_NEGATIVE` | Annual interest rate is negative | Use zero or a positive rate |
| `FEE_MUST_NOT_BE_NEGATIVE` | Any fee is negative | Model refunds separately, not as negative fees |
| `PAYMENT_DAY_OUT_OF_RANGE` | Payment day is outside 1-31 | Use a valid calendar day |
| `INVALID_DATE` | Date format is unsupported | Use `DD/MM/YYYY`, `DD-MM-YYYY`, or `YYYY-MM-DD` |
| `PAYMENT_DOES_NOT_AMORTIZE` | Payment cannot reduce balance | Check rate, term, and rounding |
| `INSTALLMENTS_PAID_OUT_OF_RANGE` | Refund request exceeds schedule length | Pass a number from 0 through the installment count |
| `INVALID_ENVIRONMENT` | Client environment is not supported | Use `sandbox` or `production` |

## Israeli regulatory domains to verify

The calculator does not replace legal analysis. Use the following domains as a verification checklist:

| Domain | Relevance to installment plans | Implementation note |
|---|---|---|
| Consumer Protection Law, 5741-1981 | Consumer-facing price display, misleading terms, cancellation and disclosure duties | Verify current wording for each product and channel |
| Consumer Protection Regulations for price display | Cash price and consumer price presentation | Keep cash price visible before credit terms |
| Credit-related consumer disclosure rules | Cost of credit, fees, and payment schedule | Review when interest or fees apply |
| Payment Services Law, 5779-2019 | Payment execution, customer authorization, and payment-service obligations | Confirm with payment provider and counsel |
| Value Added Tax Law, 5736-1975 | VAT-inclusive consumer price, VAT-exclusive business quote, invoice and credit invoice handling | Coordinate with bookkeeping |
| Standard card-acquirer rules | Number of installments, chargebacks, refunds, settlement and fees | Obtain current acquirer terms before launch |
| Bookkeeping instructions | Receipt, invoice, refund, and reconciliation records | Store calculation inputs and customer acceptance record |

## Data-retention fields

Store at least:

- Cash price, VAT status, down payment, financed amount.
- Number of installments, interest rate, every fee, rounding policy.
- First due date or date-setting rule.
- Full schedule as accepted by the customer.
- Timestamp, channel, salesperson or system actor, and customer approval evidence.
- Contract version, cancellation policy, and disclosure text version.
