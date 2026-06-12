# API, Regulation, and Data Reference

This skill is a non-API calculation package. It does not fetch official rates or regulatory data automatically. Use this reference to decide which external Israeli sources to consult manually before entering assumptions.


## Web-validated official source map

These checks were performed on 2026-06-02. Refresh them before a production decision because rates and thresholds change.

| Topic | Verified item | Package use |
|---|---|---|
| Standard VAT | 18% from 01/01/2025; still corroborated by 2026 tax references | Not calculated; documented for cash-flow context |
| Bank of Israel rate | 3.75% after 25/05/2026 decision | Manual input for prime-linked scenarios |
| Prime interest | Bank of Israel interest + 1.5% | Current implied base prime: 5.25%; lender margin remains separate |
| CPI publication | Main price indices published on the 15th at 18:30, with weekend/holiday adjustment | CPI forecast input and reconciliation note |
| CPI linkage API | `https://api.cbs.gov.il/index/catalog/tree`, `.../catalog/catalog`, `.../catalog/chapter`, `.../catalog/subject`, `.../data/price`, `.../data/calculator/{id}` | Optional external data source; not called automatically |
| Loan fees | Bank of Israel guide discusses credit and collateral handling fees, early repayment fees, and effective cost disclosure | Use `origination_fee` and `early_payment_fee` fields |
| Loan tracks | Official Bank of Israel material distinguishes fixed, variable, prime, and CPI-indexed tracks | Supports the scenario taxonomy |

### Optional CBS CPI API examples

The planner remains offline-first. Use these endpoints only in a separate data-ingestion step if current or historical CPI values are required.

```text
GET https://api.cbs.gov.il/index/catalog/tree?format=json&download=false&period=M
GET https://api.cbs.gov.il/index/data/price?id=120010&format=json&download=false&last=2&coef=true
GET https://api.cbs.gov.il/index/data/calculator/120010?value=1000&date=2025-01-01&toDate=2026-01-01&format=json
```

Treat API responses as external inputs. Store the request URL, access date, and raw response with the workpaper.

## External sources to cite in a workpaper

| Source | Use | Manual input affected | Notes |
|---|---|---|---|
| Bank of Israel | Prime-rate environment, interest-rate context, banking-supervision publications | `prime_rate`, scenario stress rates | Prime is a commercial benchmark, not a field pulled by this package |
| Central Bureau of Statistics | Consumer Price Index publication and inflation history | `annual_cpi_rate`, CPI stress cases | Contract may refer to known index or published index |
| Israel tax administration | VAT timing, deductible financing expenses, bookkeeping constraints | cash-flow assumptions outside the schedule | This skill does not calculate VAT or income tax |
| Banking Supervision consumer disclosures | Loan disclosure format, fee concepts, early-repayment context | `origination_fee`, `early_payment_fee` | Check the actual lender disclosure |
| Lender loan agreement | Binding rate, linkage, grace, balloon, fees, due dates | all inputs | Contract controls over model assumptions |

## Equivalent local API contract

Because the package is offline-first, the practical "API" is the JSON scenario schema consumed by the Python helper and CLI.

### Request: single scenario

```json
{
  "name": "working capital prime scenario",
  "principal": "120000",
  "term_months": 36,
  "start_date": "15/06/2026",
  "rate_type": "prime",
  "prime_rate": "0.0525",
  "prime_margin": "0.018",
  "payment_frequency": "monthly",
  "grace_months": 0,
  "balloon_percent": "0",
  "origination_fee": "750",
  "early_payment_fee": "0",
  "rate_changes": {
    "13": "0.085"
  },
  "extra_payments": {
    "7": "15000"
  }
}
```

### Response: schedule summary and rows

```json
{
  "scenario": {
    "name": "working capital prime scenario",
    "principal": "120000.00",
    "term_months": 36,
    "start_date": "2026-06-15",
    "rate_type": "prime",
    "payment_frequency": "monthly"
  },
  "summary": {
    "principal": "120000.00",
    "total_interest": "10342.18",
    "total_cpi_adjustment": "0.00",
    "total_paid": "130342.18",
    "fees": "750.00",
    "effective_cash_cost": "11092.18",
    "final_balance": "0.00",
    "max_payment": "4612.49",
    "periods": 32
  },
  "rows": [
    {
      "period": 1,
      "due_date": "2026-07-15",
      "opening_balance": "120000.00",
      "cpi_adjustment": "0.00",
      "indexed_balance": "120000.00",
      "interest_rate_annual": "7.8000",
      "interest": "780.00",
      "principal": "2984.21",
      "extra_payment": "0.00",
      "total_payment": "3764.21",
      "closing_balance": "117015.79"
    }
  ]
}
```

Values above are illustrative. Generate actual results with the packaged scripts.

## CLI commands

### Build one schedule

```bash
python -m loan_amortization_planner.cli schedule scenario.json --json-out schedule.json --csv-out schedule.csv --rows 12
```

### Compare scenarios

```bash
python -m loan_amortization_planner.cli compare scenarios.json
```

### Validate input

```bash
python -m loan_amortization_planner.cli validate scenario.json
```

## Python API

### Synchronous

```python
from loan_amortization_planner import LoanScenario, build_schedule

scenario = LoanScenario.from_mapping({
    "principal": "250000",
    "term_months": 72,
    "start_date": "01/07/2026",
    "annual_interest_rate": "0.065"
})
schedule = build_schedule(scenario)
print(schedule.summary.as_dict())
```

### Asynchronous

```python
result = await loan_client.async_build_schedule(scenario)
```

## Error table

| Error text | Cause | Fix |
|---|---|---|
| `principal must be positive` | Principal is zero or negative | Enter a positive ₪ amount |
| `term_months must be positive` | Term is missing or non-positive | Enter a positive number of months |
| `prime_rate is required for prime loans` | `rate_type=prime` without `prime_rate` | Enter the assumed prime rate as decimal |
| `grace_months must be shorter than term_months` | Grace consumes the full term | Leave at least one amortizing period |
| `balloon_percent must be between 0 and less than 1` | Balloon is negative or at least 100% | Use `0` to `0.9999` |
| `quarterly repayment requires term_months divisible by 3` | Quarterly schedule cannot align with term | Choose a term divisible by 3 |
| `date must be YYYY-MM-DD or DD/MM/YYYY` | Unsupported date format | Use `31/01/2026` or `2026-01-31` |

## Regulatory-use cautions

- Do not state that the generated schedule is an official lender amortization table.
- Do not state that the package retrieves official Bank of Israel or CPI data.
- Do not use the output to represent a binding APR or total-credit-cost disclosure unless the lender's required methodology is implemented separately.
- Do not combine VAT, income tax, depreciation, and financing cost in the same output without a separate tax model.
- Do not rely on CPI assumptions without identifying whether the loan uses known index, base index, published index, or another contractual mechanism.

## Data retention and privacy

The package writes only to paths selected by the operator. It does not transmit scenario data. When handling consumer or sole-proprietor data, store input files and generated CSVs according to the organization's privacy and document-retention policy.
