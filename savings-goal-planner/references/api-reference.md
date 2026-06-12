# API and Regulation Reference

## Scope

This package does not call live financial APIs. Treat the client as a deterministic calculation helper. Use the references below to validate assumptions before production use. When a workflow imports rates, indices, contribution limits, or fund data from another system, record the source URL, retrieval date, source quote, and transformation rules.

Access date for the validated entries below: 02/06/2026.

## Official and reference sources

| Topic | Authority or source | URL | Use in planning | Validated note |
|---|---|---|---|---|
| Standard VAT rate | Israel Tax Authority | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf | VAT reserve assumptions | Use 18% for standard Israeli VAT scenarios from 01/01/2025; recheck before filing |
| VAT reporting and payment | Israel Tax Authority | https://www.gov.il/he/service/reporting-or-payment-of-vat-reports | VAT cash-flow timing | Online filing service for registered dealers; deadline rules vary by report type |
| VAT terminology and current 2026 confirmation | Kol Zchut | https://www.kolzchut.org.il/he/הגשת_דו%22חות_תקופתיים_ותשלום_מס_ערך_מוסף | Plain-language cross-check | Confirms 18% from 01/01/2025 and 2026 reporting examples |
| Bank of Israel policy rate | Bank of Israel | https://www.boi.org.il/publications/pressreleases/25-5-26/ | Market context for cash and deposit assumptions | Policy rate is 3.75% after the 25/05/2026 decision; do not treat as a product yield |
| Inflation target | Bank of Israel | https://www.boi.org.il/en/bank-of-israel/about-the-bank-of-israel/objectives-and-functions/ | Inflation assumption sanity check | Official price-stability range is 1-3% |
| Consumer price index API | Central Bureau of Statistics | https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx | CPI history and index-linkage workflows | Use CBS API host `https://api.cbs.gov.il` and published endpoint paths |
| Capital-gains tax reporting | Israel Tax Authority | https://www.gov.il/BlobFolder/service/reporting-and-payment-2025-annual-tax-report-for-individuals/he/Service_Pages_Income_tax_annual-report-2026_1322-2025.pdf | Tax drag on taxable securities | Forms show 25% real capital-gains tax for common securities scenarios; exceptions apply |
| Deposit and savings interest taxation | Israel Tax Authority | https://www.gov.il/he/pages/guide-to-taxes-on-income-from-deposits-and-savings-and-tax-relief-programs?chapterIndex=2 | Bank deposit and interest assumptions | Tax may be 15%, 20%, or 25% depending on product and linkage |
| National Insurance for self-employed | National Insurance Institute | https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx | Freelancer reserve scenarios | For 2026, ordinary self-employed brackets use ₪7,703 and ₪51,910 thresholds and 7.7% / 18% totals |
| Self-employed National Insurance cross-check | Kol Zchut | https://www.kolzchut.org.il/he/דמי_ביטוח_לאומי_לעצמאי | Plain-language cross-check | Confirms the same 2026 brackets and rates |
| Retirement age | National Insurance Institute | https://www.btl.gov.il/benefits/old_age/Conditions_of_eligibility/gilMezake/Pages/gilPrisha.aspx | Retirement scenarios | Men: 67; women: 60-65 by birth date; do not hard-code a single age for every user |
| Old-age allowance terminology | National Insurance Institute | https://www.btl.gov.il/benefits/old_age/Pages/schum.aspx | Income-gap naming | Use expected pension or allowance income, not a generic fixed state-pension value |
| Training fund rules | Civil Service Commission pension-insurance guide | https://www.gov.il/BlobFolder/reports/pension-insurance-2026-csc/he/pension-insurance-csc-2026.pdf | Vehicle suitability warnings | The guide describes six-year liquidity and typical employee/employer deposit percentages |
| Investment provident fund cap | Kol Zchut | https://www.kolzchut.org.il/he/קופת_גמל_להשקעה | 2026 contribution-cap checks | For 2026, cap is ₪83,641 per person per calendar year; 2025 cap of ₪81,711 is stale for 2026 |
| Provident and pension comparisons | GemelNet / Capital Market Authority | https://gemelnet.cma.gov.il | Product comparison workflow | Use official comparison tools for actual returns, fees, and track data |

## CBS price-index API

The package does not call CBS directly, but production systems can import CPI data with the official paths below.

### API host

```text
https://api.cbs.gov.il
```

### Catalog tree

```http
GET /index/catalog/tree?format=json&download=false&lang=he
Host: api.cbs.gov.il
Accept: application/json
```

Example response shape:

```json
{
  "id": 120010,
  "name": "מדד המחירים לצרכן",
  "children": []
}
```

### Price data

```http
GET /index/data/price?id=120010&format=json&download=false&lang=he
Host: api.cbs.gov.il
Accept: application/json
```

Example response shape:

```json
{
  "id": 120010,
  "period": "2026-04",
  "base": "2024=100",
  "value": 104.2
}
```

### Calculator endpoint

```http
GET /index/data/calculator/120010?startPeriod=2025-01&endPeriod=2026-01&format=json&lang=he
Host: api.cbs.gov.il
Accept: application/json
```

Example response shape:

```json
{
  "startPeriod": "2025-01",
  "endPeriod": "2026-01",
  "changePercent": 2.4
}
```

### Selected price endpoint

```http
GET /index/data/price_selected_b?id=120010&format=json&download=false&lang=he
Host: api.cbs.gov.il
Accept: application/json
```

## Non-API official references

No government webhook is used by this package. Webhook event names are not applicable.

When integrating a workflow with external systems, store the following fields with each imported source:

```json
{
  "source_name": "Bank of Israel interest-rate announcement",
  "source_url": "https://www.boi.org.il/publications/pressreleases/25-5-26/",
  "accessed_at": "02/06/2026",
  "source_quote": "להוריד את הריבית ב-0.25% לרמה של 3.75%",
  "assumption_name": "policy_rate_context",
  "assumption_value": 0.0375,
  "review_frequency": "after every Bank of Israel rate decision"
}
```

## Internal module interface

### Calculate a purchase or reserve goal

Request:

```python
from savings_goal_planner import GoalRequest, SavingsGoalPlannerClient

request = GoalRequest(
    goal_name="Used delivery vehicle",
    target_amount=180000,
    months=36,
    current_savings=40000,
    current_monthly_savings=1500,
    inflation_rate=0.025,
    vehicle_key="bank_deposit_fixed",
    monthly_income=22000,
)

result = SavingsGoalPlannerClient().calculate_goal(request)
```

Response shape:

```json
{
  "goal_name": "Used delivery vehicle",
  "target_amount_input": 180000.0,
  "target_future_value": 193838.68,
  "months": 36,
  "years": 3.0,
  "monthly_required": 2727.4,
  "current_monthly_savings": 1500.0,
  "total_new_contributions": 98186.4,
  "projected_current_savings_value": 42150.0,
  "projected_existing_monthly_value": 55321.0,
  "projected_total_value": 193838.68,
  "shortfall_at_current_rate": 96367.68,
  "effective_annual_return": 0.02125,
  "monthly_return": 0.001752,
  "inflation_rate": 0.025,
  "vehicle": {
    "key": "bank_deposit_fixed",
    "english_name": "Fixed bank deposit",
    "hebrew_name": "פיקדון בנקאי קצוב"
  },
  "warnings": []
}
```

Numerical values above are illustrative. Run the package to produce exact values.

### Calculate retirement gap

Request:

```python
from savings_goal_planner import RetirementRequest, SavingsGoalPlannerClient

request = RetirementRequest(
    current_age=42,
    retirement_age=67,
    life_expectancy=95,
    desired_monthly_spending_today=14000,
    expected_monthly_pension_today=7000,
    current_retirement_savings=180000,
)

result = SavingsGoalPlannerClient().calculate_retirement(request)
```

Response shape:

```json
{
  "accumulation_months": 300,
  "retirement_months": 336,
  "monthly_income_gap_today": 7000.0,
  "required_nest_egg_today": 1690000.0,
  "monthly_required_today": 2500.0,
  "projected_current_savings_today": 480000.0,
  "effective_annual_return_accumulation": 0.04,
  "annual_real_return_retirement": 0.025,
  "warnings": []
}
```

### Store and retrieve a goal

Request:

```python
from savings_goal_planner import GoalRequest, SavingsGoalPlannerClient

client = SavingsGoalPlannerClient()
stored = client.create_goal(
    GoalRequest(goal_name="Equipment", target_amount=42000, months=18),
    store_path="goals.json",
    environment="sandbox",
)

same_goal = client.get_goal(stored.id, store_path="goals.json", environment="sandbox")
```

Stored response shape:

```json
{
  "id": "2f9f9d6f8e314a5a8e6b9f0c91d2f6ac",
  "environment": "sandbox",
  "created_at": "2026-06-02T12:00:00+00:00",
  "request": {
    "goal_name": "Equipment",
    "target_amount": 42000.0,
    "months": 18
  },
  "result": {
    "goal_name": "Equipment",
    "monthly_required": 2333.33
  }
}
```

## Command-line request examples

### Direct goal calculation

```bash
savings-goal-planner goal \
  --target 180000 \
  --months 36 \
  --current-savings 40000 \
  --vehicle bank_deposit_fixed \
  --format json
```

### Chained stored workflow

```bash
CREATE_RESPONSE="$(savings-goal-planner create-goal \
  --target 180000 \
  --months 36 \
  --env sandbox \
  --format json)"

GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
savings-goal-planner show-goal --id "$GOAL_ID" --env sandbox --format json
```

## Vehicle preset reference

| Key | Default annual return | Fee | Tax drag | Intended use |
|---|---:|---:|---:|---|
| `cash_bank` | 0.5% | 0.0% | 15% | Emergency and immediate reserves |
| `bank_deposit_fixed` | 2.5% | 0.0% | 15% | Fixed-date low-volatility goals |
| `money_market_fund` | 3.5% | 0.15% | 25% | Short reserve with daily pricing |
| `government_bond_fund` | 4.0% | 0.50% | 25% | Medium low-credit-risk exposure |
| `taxable_brokerage_balanced` | 5.5% | 0.80% | 25% | Medium and long flexible goals |
| `equity_index_fund` | 7.0% | 0.40% | 25% | Long horizon, high volatility tolerance |
| `keren_hishtalmut` | 6.0% | 0.60% | 0% | Eligible long horizon wrapper |
| `kupat_gemel_investment` | 5.5% | 0.70% | 25% | Long flexible wrapper; 2026 contribution cap is ₪83,641 per person |
| `pension_fund` | 5.5% | 0.50% | 0% | Retirement only |

Do not treat preset assumptions as current market quotes. Replace them with product-specific data before advising a user. Use Bank of Israel rates as context, not as a deposit quote. Use GemelNet, PensionNet, provider disclosures, or bank disclosures for actual products.

## Error table

| Error message | Trigger | Corrective action |
|---|---|---|
| `target_amount must be non-negative` | Negative target | Enter zero or a positive target |
| `months must be greater than zero` | Horizon of zero or less | Enter at least one month |
| `unknown vehicle_key` | Vehicle key not in preset table | Run `savings-goal-planner vehicles` |
| `annual_return must be greater than -0.999 and at most 1.0` | Return outside accepted range | Correct the rate |
| `annual_fee must be non-negative` | Negative fee | Enter zero or positive fee |
| `tax_rate_on_gain must be between 0 and 1` | Tax rate outside 0 to 100 percent | Enter a decimal such as `0.25` |
| `environment must be sandbox or production` | Invalid repository environment | Use `--env sandbox` or `--env production` |
| `goal not found` | Identifier absent from selected store | Pass the correct id, store path, and environment |
| `store file is not valid JSON` | Corrupt store file | Restore from backup or remove the invalid file |
| `store file must contain a JSON array` | Store root is not an array | Replace with `[]` or recreate through the CLI |

## Production source checklist

For every production run, record:

- Source name.
- Source URL.
- Retrieval date in DD/MM/YYYY.
- Relevant table, page, or disclosure name.
- Assumption copied into the calculation.
- Transformation applied to turn the source value into an annual decimal rate.
- Reviewer role, without putting personal attribution in package metadata.
- Next review date.

## Data freshness rules

- Refresh CPI and interest-rate assumptions after official publication updates.
- Refresh tax and contribution caps at the start of each tax year and after legislative changes.
- Refresh product fees and yields before client-facing use.
- Treat copied source dates as more important than file modification dates.
- Reject stale assumptions when the output drives a binding quote, budget approval, or client-facing recommendation.
