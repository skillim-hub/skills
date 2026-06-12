# Test Scenarios

Use these scenarios for manual QA, regression tests, and examples. Monetary amounts are in ₪.

| ID | Scenario | Inputs | Expected result |
|---:|---|---|---|
| 1 | Small consumer purchase | Target 12,000, 12 months, no savings | Monthly required near 1,000 before return effects |
| 2 | Current savings cover target | Target 10,000, 12 months, current savings 12,000 | Monthly required equals 0 |
| 3 | Inflation-adjusted car purchase | Target 180,000, 36 months, inflation 2.5% | Future target exceeds 180,000 |
| 4 | Future nominal invoice | Target 180,000, 36 months, `amount_is_today_terms=false` | Future target remains 180,000 |
| 5 | Current monthly deposits included | Target 60,000, 24 months, current monthly 1,000 | Required additional monthly is lower |
| 6 | Beginning deposits | Target 60,000, 24 months, timing beginning | Required monthly is lower than end timing |
| 7 | Zero return | Target 24,000, 24 months, zero return | Monthly required equals 1,000 when no current savings |
| 8 | Fixed deposit vehicle | Vehicle `bank_deposit_fixed`, 12 months | Vehicle appears in output |
| 9 | Money-market short reserve | Vehicle `money_market_fund`, 6 months | No long-horizon warning from that vehicle |
| 10 | Government bond too short | Vehicle `government_bond_fund`, 6 months | Warning about short horizon |
| 11 | Equity fund too short | Vehicle `equity_index_fund`, 24 months | Warning about volatility or constraint |
| 12 | Training fund early use | Vehicle `keren_hishtalmut`, 36 months | Warning about eligibility and withdrawal rules |
| 13 | Pension for purchase | Vehicle `pension_fund`, 36 months | Warning that pension savings should not fund ordinary purchases |
| 14 | High inflation | Inflation 8% | Warning requests stress test |
| 15 | Aggressive return | Annual return 15% | Warning requests downside case |
| 16 | Affordability pressure | Required monthly exceeds 30% of income | Affordability warning appears |
| 17 | Negative target | Target -1 | Validation error |
| 18 | Zero months | Months 0 | Validation error |
| 19 | Invalid vehicle key | Vehicle `missing` | Validation error |
| 20 | Retirement base case | Age 42, retire 67, life 95 | Positive required nest egg and monthly saving |
| 21 | Retirement no gap | Desired spending 7,000, expected pension 8,000 | Monthly gap equals 0 |
| 22 | Retirement invalid age | Retirement age below current age | Validation error |
| 23 | Vehicle ranking low risk | Horizon 12, risk very low | Cash and deposits rank high |
| 24 | Vehicle ranking tax wrapper | Horizon 96, tax-advantaged true | Eligible wrappers receive score benefit |
| 25 | Stored goal create and get | Create goal with sandbox store, retrieve by id | Same id and result returned |
| 26 | Stored goal missing id | Retrieve unknown id | Validation error |
| 27 | Stored goal corrupt file | Store contains invalid JSON | Validation error |
| 28 | CLI goal JSON | Run `goal --format json` | Valid JSON with `monthly_required` |
| 29 | CLI chained goal | Run `create-goal`, parse id, run `show-goal` | Same id returned |
| 30 | Example script environment | Set `SGP_TARGET` and run example | Output reflects environment value |

## Regression commands

```bash
pytest
python -m compileall scripts/ -q
```

## Manual command cases

### Scenario 3

```bash
savings-goal-planner goal \
  --name "Inflation-adjusted car" \
  --target 180000 \
  --months 36 \
  --inflation-rate 0.025 \
  --format json
```

### Scenario 13

```bash
savings-goal-planner goal \
  --name "Purchase with pension mismatch" \
  --target 100000 \
  --months 36 \
  --vehicle pension_fund \
  --format json
```

### Scenario 29

```bash
CREATE_RESPONSE="$(savings-goal-planner create-goal --target 10000 --months 10 --env sandbox --format json)"
GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
savings-goal-planner show-goal --id "$GOAL_ID" --env sandbox --format json
```

## Expected invariants

- Increasing inflation raises the future target when the target is in today's terms.
- Increasing current savings lowers required monthly saving.
- Increasing current monthly saving lowers additional required monthly saving.
- Beginning-of-month deposits require less than end-of-month deposits when return is positive.
- Retirement calculations use real returns and today's ₪.
- Stored goals preserve request data and recompute deterministic result values from stored request data.
