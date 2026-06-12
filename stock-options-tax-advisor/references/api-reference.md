# Regulation and Helper Interface Reference

This package is a local planning helper. It does not call a government API. Treat the following as a structured reference for the Israeli regulations and public authorities that the workflow cites, plus request and response shapes for the local client and CLI.

## Israeli regulation and authority map

| Area | Citation or authority | Use in this package |
| --- | --- | --- |
| Employee equity | Income Tax Ordinance, Section 102 | Determines trustee route, capital gains track, income track, non-trustee treatment, holding-period checks, and plan documentation needs. |
| Non-employee equity and certain option benefits | Income Tax Ordinance, Section 3(i) | Conservative ordinary-income modeling when Section 102 does not apply. |
| Capital gains | Income Tax Ordinance capital-gain provisions | Applies the ordinary 25 percent capital gains rate in the planning constants. |
| Controlling shareholder | Israeli tax rules for material shareholders | Applies 30 percent capital gains rate when 10 percent or more holder status is indicated. |
| Surtax | Income Tax Ordinance surtax provisions | Adds surtax above the configured annual threshold. |
| National Insurance | National Insurance Law and National Insurance Institute rules | Applies capped National Insurance and health contribution estimates to employment income components. |
| Health contribution | National Health Insurance Law | Included with National Insurance for employment-income components. |
| Withholding | Israel Tax Authority withholding and trustee reporting practice | Prompts for trustee confirmations and withholding letters. |

## Web-validated official source map

Access date for the source map: 01/06/2026. This package has no live government API integration, API host, endpoint path, or webhook event. Use the source map to refresh local constants and guidance.

| Check | Current package position | Official source to refresh |
| --- | --- | --- |
| VAT context | 18% from 01/01/2025; not used in equity calculations. | Israel Tax Authority VAT rates/history pages and Knesset VAT order release. |
| Section 102 plan route | Treat capital-track status as unavailable unless trustee and plan facts are documented. | Income Tax Circular 01/2024 on submitting trustee share-allocation plans under Section 102. |
| Section 102 capital track | Model documented capital-track gain at 25% before surtax. | Tax Authority Form 1399 explanatory pages and Section 102 publications. |
| Holding period | Default conservative helper can anchor the preferred sale date to grant-year end, grant date, trustee deposit date, or a manual date. | Income Tax Ordinance Section 102 and court/Tax Authority publications referring to the required trustee period. |
| Public-company split | Require grant-date FMV for listed-company grants and split embedded employment income from later appreciation. | Section 102(b)(3) discussions and Tax Authority Section 102 plan questionnaire. |
| Section 3(i) and non-employee cases | Model conservatively as ordinary income unless an ESPP purchase-FMV split is supplied and reviewed. | Income Tax Ordinance Section 3(i) and professional commentary cross-checked against Tax Authority materials. |
| Capital gains rate | 25%; 30% when material shareholder status applies; both before surtax. | Tax Authority capital-gain forms 1399, 1322, and the official glossary. |
| Surtax | 3% above ₪721,560 plus 2% extra on capital-source income above that threshold. | Tax Authority Instruction 05/2025 and 2026 deduction-booklet materials. |
| Income tax brackets | 2026 annual earned-income brackets: ₪84,120, ₪120,720, ₪228,000, ₪301,200, ₪560,280, then 47% above. | Tax Authority 2026 deduction booklet and 2026 tax-coordination updates. |
| National Insurance and health | Employee-side estimate: 4.27% below ₪7,703/month and 12.17% above, capped at ₪51,910/month. | National Insurance employee-rate table and health-contribution page. |

## Local calculate request

```json
{
  "grant_type": "options",
  "track": "102_capital",
  "quantity": 50000,
  "exercise_price": 1,
  "sale_price": 10,
  "grant_date": "15/03/2024",
  "sale_date": "02/01/2027",
  "other_annual_income": 360000,
  "trustee_approved": true,
  "holding_period_anchor": "grant_year_end",
  "currency": "ILS",
  "fx_rate_to_ils": 1
}
```

## Local calculate response

```json
{
  "gross_proceeds": 500000,
  "cost_basis": 50000,
  "total_gain": 450000,
  "employment_income": 0,
  "capital_gain": 450000,
  "ordinary_income_tax": 0,
  "capital_gains_tax": 112500,
  "national_insurance_health": 0,
  "surtax": 2653.2,
  "total_tax": 115153.2,
  "net_proceeds": 334846.8,
  "effective_tax_rate_on_gain": 0.255896,
  "holding_period_satisfied": true,
  "earliest_preferred_sale_date": "2026-12-31",
  "warnings": [],
  "assumptions": ["Section 102 capital-gains track modeled with documented or assumed trustee compliance."]
}
```

## CLI reference

| Command | Purpose |
| --- | --- |
| `stock-options-tax-advisor calculate` | Calculate one scenario. |
| `stock-options-tax-advisor compare` | Compare Section 102 capital, Section 102 income, and Section 3(i). |
| `stock-options-tax-advisor eligibility` | Compute earliest preferred sale date and holding-period status. |

## Field validation errors

| Error | Meaning | Fix |
| --- | --- | --- |
| `quantity must be positive` | Quantity is zero or negative. | Enter the number of shares, options, or units sold. |
| `sale_price must be non-negative` | Sale price cannot be below zero. | Use zero only for forfeiture or worthless outcome modeling. |
| `exercise_price must be non-negative` | Exercise or purchase price cannot be below zero. | Check broker statement and grant agreement. |
| `fx_rate_to_ils is required for non-ILS currency` | Foreign-currency values were supplied without a valid exchange rate. | Add date-specific ILS exchange rate. |
| `fmv_at_exercise is required for 102_income` | Income-track split cannot be computed without exercise or release FMV. | Obtain fair market value from trustee or valuation support. |
| `fmv_at_purchase is required for ESPP non-102 discount split` | ESPP discount cannot be split without purchase FMV. | Obtain plan purchase statement. |
| `environment must be sandbox or production` | Unsupported environment option. | Use `sandbox` for examples or `production` for reviewed assumptions. |

## Python interface

```python
from stock_options_tax_advisor import EquityScenario, StockOptionsTaxAdvisorClient

client = StockOptionsTaxAdvisorClient(environment="sandbox")
scenario = EquityScenario.from_dict({...})
breakdown = client.calculate(scenario)
```
