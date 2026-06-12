# Reference: Israeli Shovi Rechev Data, Regulations, and Local Interfaces

This is a non-API skill. The reference below documents the official sources to verify, the local JSON table contract, command request/response examples, and error behavior.

## Official sources to verify before production use

Use current official Israeli sources before payroll filing or client-facing advice:

| Source | Purpose | What to verify |
|---|---|---|
| Israel Tax Authority — שווי שימוש ברכב צמוד | Annual Shovi Rechev guidance and tables | Linear rate, green-vehicle monthly reductions, special categories. |
| Israel Tax Authority — מאגר דגמי רכב / מחיר מקורי | Vehicle model original coordinated price | Official price used for calculation. |
| Income Tax Ordinance and Income Tax Regulations | Legal basis for employee benefit taxation | Applicability of benefit valuation rules. |
| National Insurance Institute guidance | Payroll impact context | Whether payroll systems apply additional liabilities. |
| VAT Law and bookkeeping instructions | Expense/VAT comparison for business owners | Deductibility limits and VAT input restrictions for passenger cars. |

Suggested official URLs to check manually:

```text
https://www.gov.il/he/departments/israel_tax_authority
https://www.gov.il/he/departments/topics/vehicle_tax
https://www.gov.il/he/service/car_value_use
https://www.gov.il/he/departments/publications/reports
```

URL paths can change. Search the official government portal for: `שווי שימוש ברכב`, `רכב צמוד`, `מחיר מקורי מתואם`, `רכב היברידי`, `רכב חשמלי`.

## Local table schema

File: `data/tax_authority_tables.json`

### Top-level fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | string | Yes | Data contract version. |
| `currency` | string | Yes | `ILS`. |
| `locale` | string | Yes | `he-IL`. |
| `last_reviewed` | string | Yes | Review date in `DD/MM/YYYY`. |
| `source_note` | string | Yes | Human warning about official verification. |
| `calculation_method` | string | Yes | Currently `linear_percent_with_monthly_reduction`. |
| `default_private_vehicle_rate` | number | Yes | Fallback linear rate. |
| `annual_rules` | object | Yes | Year-specific rules. |
| `validation` | object | Yes | Input bounds and warnings. |

### Annual rule fields

```json
{
  "2026": {
    "effective_from": "01/01/2026",
    "effective_to": "31/12/2026",
    "base_linear_rate": 0.0248,
    "categories": {
      "private_combustion": {
        "he": "רכב פרטי בנזין/דיזל",
        "monthly_reduction_ils": 0,
        "allowed": true,
        "notes": "שווי חודשי רגיל לפי שיעור לינארי ממחיר מקורי מתואם."
      }
    }
  }
}
```

### Category keys

| Key | Hebrew label | Linear formula status |
|---|---|---|
| `private_combustion` | רכב פרטי בנזין/דיזל | Supported |
| `hybrid` | רכב היברידי | Supported with reduction |
| `plugin_hybrid` | רכב היברידי נטען | Supported with reduction |
| `electric` | רכב חשמלי | Supported with reduction |
| `motorcycle_l3` | אופנוע L3 | Rejected by calculator; requires dedicated rule |

## Command interface

### Calculate one vehicle

Request:

```bash
python scripts/car_leasing_tax_benefit_client.py calculate \
  --price 180000 \
  --category private_combustion \
  --year 2026 \
  --tax-rate 0.35 \
  --months 12 \
  --json
```

Response:

```json
{
  "category": "private_combustion",
  "category_he": "רכב פרטי בנזין/דיזל",
  "tax_year": 2026,
  "original_price_ils": "180000.00",
  "monthly_imputed_value_ils": "4464.00",
  "annual_imputed_value_ils": "53568.00",
  "estimated_monthly_tax_cost_ils": "1562.40",
  "estimated_annual_tax_cost_ils": "18748.80",
  "employee_marginal_tax_rate": "0.35",
  "license_plate": null,
  "employee_name": null,
  "trace": {
    "formula": "max(original_price_ils * base_linear_rate - category_reduction_ils, 0) * private_use_ratio",
    "base_linear_rate": "0.0248",
    "gross_monthly_value_ils": "4464.00",
    "category_reduction_ils": "0",
    "private_use_ratio": "1",
    "months_available": 12,
    "rule_effective_from": "01/01/2026",
    "rule_effective_to": "31/12/2026",
    "warnings": []
  }
}
```

### Calculate an electric vehicle

Request:

```bash
python scripts/car_leasing_tax_benefit_client.py calculate \
  --price 220000 \
  --category electric \
  --tax-rate 0.47 \
  --json
```

Response:

```json
{
  "category": "electric",
  "category_he": "רכב חשמלי",
  "monthly_imputed_value_ils": "4076.00",
  "estimated_monthly_tax_cost_ils": "1915.72"
}
```

### Batch request

Input file:

```json
[
  {
    "employee_name": "Leah",
    "license_plate": "111-22-333",
    "original_price_ils": "145000",
    "category": "private_combustion",
    "tax_year": 2026,
    "employee_marginal_tax_rate": "0.31"
  },
  {
    "employee_name": "Omer",
    "license_plate": "444-55-666",
    "original_price_ils": "230000",
    "category": "electric",
    "tax_year": 2026,
    "employee_marginal_tax_rate": "0.47"
  }
]
```

Command:

```bash
python scripts/car_leasing_tax_benefit_client.py batch input.json --output-csv shovi.csv
```

CSV columns:

```text
employee_name,license_plate,tax_year,category,category_he,original_price_ils,monthly_imputed_value_ils,annual_imputed_value_ils,estimated_monthly_tax_cost_ils,estimated_annual_tax_cost_ils,employee_marginal_tax_rate
```

## Python sync client

```python
from decimal import Decimal
from pathlib import Path
import importlib.util
import sys

path = Path("scripts/car_leasing_tax_benefit_client.py")
spec = importlib.util.spec_from_file_location("client", path)
client_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = client_module
spec.loader.exec_module(client_module)

client = client_module.CarLeasingTaxBenefitClient()
vehicle = client_module.VehicleInput(
    original_price_ils=Decimal("180000"),
    category="private_combustion",
    employee_marginal_tax_rate=Decimal("0.35"),
)
result = client.calculate(vehicle)
print(result.to_dict())
```

## Python async client

```python
import asyncio

async def run():
    client = client_module.CarLeasingTaxBenefitClient()
    result = await client.calculate_async({"original_price_ils": "220000", "category": "electric"})
    return result.to_dict()

print(asyncio.run(run()))
```

## Error reference

| Error class | Trigger | Example message | Corrective action |
|---|---|---|---|
| `RuleTableError` | Missing JSON table | `Rule table not found` | Check path or restore `data/tax_authority_tables.json`. |
| `RuleTableError` | Unsupported year | `No rules for tax_year=2035` | Add official year rules. |
| `InputValidationError` | Negative or zero price | `original_price_ils must be positive` | Use official positive price. |
| `InputValidationError` | Tax rate outside 0–1 | `employee_marginal_tax_rate must be between 0 and 1` | Use decimal rate such as `0.35`. |
| `InputValidationError` | Months outside 1–12 | `months_available must be between 1 and 12` | Split periods or fix input. |
| `UnsupportedCategoryError` | Unknown category key | `Unknown category '...'` | Run `categories`. |
| `UnsupportedCategoryError` | Dedicated-rule category | `requires a dedicated rule` | Use a specialized calculation method. |
| `json.JSONDecodeError` via CLI | Invalid batch file | JSON parse failure | Validate input JSON. |

## Data-quality controls

- Store the official publication date in `last_reviewed`.
- Keep a copy of the official table used for each payroll year.
- Add a changelog entry whenever rates change.
- Run the test suite after changing any rate, category, or formula.
- For client workpapers, export JSON with trace rather than only final numbers.


## Create-then-calculate local request workflow

Create request:

```bash
python scripts/car_leasing_tax_benefit_client.py --env sandbox create \
  --price 180000 \
  --category private_combustion \
  --tax-rate 0.35
```

Response:

```json
{
  "id": "clr_example1234",
  "environment": "sandbox",
  "vehicle": {
    "original_price_ils": "180000",
    "category": "private_combustion",
    "tax_year": 2026,
    "employee_marginal_tax_rate": "0.35",
    "months_available": 12,
    "private_use_ratio": "1",
    "employee_name": null,
    "license_plate": null
  }
}
```

Use the id in the next step:

```bash
python scripts/car_leasing_tax_benefit_client.py --env sandbox calculate \
  --request-id clr_example1234 \
  --json
```

## Installable import

```python
from car_leasing_tax_benefit import CarLeasingTaxBenefitClient

client = CarLeasingTaxBenefitClient()
result = client.calculate({"original_price_ils": "180000", "category": "private_combustion"})
print(result.to_dict())
```


## Web-validated current values as of 01/06/2026

The calculator is local/offline. It does not call the Tax Authority simulator. Use these values only after verifying current official publications again.

| Tax year | Linear rate | Price ceiling | Hybrid reduction | Plug-in hybrid reduction | Electric reduction |
|---:|---:|---:|---:|---:|---:|
| 2026 | 2.48% | ₪596,860 | ₪580 | ₪1,150 | ₪1,380 |
| 2025 | 2.48% | ₪583,100 | ₪560 | ₪1,130 | ₪1,350 |
| 2024 | 2.48% | ₪563,790 | ₪540 | ₪1,090 | ₪1,310 |

Formula used by v3:

```text
monthly_imputed_value =
  max(min(original_price_ils, price_ceiling_ils) × base_linear_rate − monthly_category_reduction, 0)
  × private_use_ratio
```

No webhook event names apply because this is a local calculation helper, not a hosted API integration.
