# Savings Goal Planner

Neutral package for calculating monthly savings needed for major purchases, business reserves, equipment upgrades, and retirement gaps in Israel.

## What it includes

- English and Hebrew skill guides.
- Israeli vehicle presets for bank cash, fixed deposits, money-market funds, government bond funds, taxable portfolios, equity funds, training funds, investment provident funds, and pension funds.
- Deterministic Python client with synchronous and asynchronous methods.
- JSON-backed goal repository for chained command-line workflows.
- Click command-line interface.
- Runnable example scripts.
- Pytest suite and development configuration.

## Install for local use

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained stored goal

Create a stored goal, extract the returned identifier, and use the identifier in the next command.

```bash
CREATE_RESPONSE="$(savings-goal-planner create-goal \
  --name "Used delivery vehicle" \
  --target 180000 \
  --months 36 \
  --current-savings 40000 \
  --inflation-rate 0.025 \
  --vehicle bank_deposit_fixed \
  --env sandbox \
  --format json)"

GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"

savings-goal-planner show-goal \
  --id "$GOAL_ID" \
  --env sandbox \
  --format json
```

Use an explicit store path when testing repeatable examples:

```bash
STORE_PATH="$(pwd)/tmp-goals.json"

CREATE_RESPONSE="$(savings-goal-planner create-goal \
  --target 42000 \
  --months 18 \
  --vehicle money_market_fund \
  --store "$STORE_PATH" \
  --env sandbox \
  --format json)"

GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"

savings-goal-planner show-goal --id "$GOAL_ID" --store "$STORE_PATH" --env sandbox
```

## Validated Israeli references

Public calculations use configurable assumptions. As of 02/06/2026, the packaged reference notes validate the Israeli VAT rate, Bank of Israel policy-rate context, inflation-target terminology, CBS price-index API paths, National Insurance self-employed thresholds, retirement-age terminology, and common Israeli savings vehicles. Always recheck official sources before filing tax reports, issuing invoices, or making product recommendations.

## Direct calculations

```bash
savings-goal-planner goal \
  --name "Renovation" \
  --target 90000 \
  --months 30 \
  --current-savings 25000 \
  --inflation-rate 0.025 \
  --vehicle money_market_fund \
  --format json
```

```bash
savings-goal-planner retirement \
  --current-age 42 \
  --retirement-age 67 \
  --life-expectancy 95 \
  --monthly-spending 14000 \
  --expected-pension 7000 \
  --current-savings 180000 \
  --format json
```

```bash
savings-goal-planner recommend-vehicles \
  --months 72 \
  --risk medium \
  --liquidity few_days \
  --tax-advantaged \
  --format json
```

## Python use

```python
from savings_goal_planner import GoalRequest, SavingsGoalPlannerClient

client = SavingsGoalPlannerClient()

result = client.calculate_goal(
    GoalRequest(
        goal_name="Equipment upgrade",
        target_amount=42000,
        months=18,
        current_savings=8000,
        current_monthly_savings=900,
        vehicle_key="money_market_fund",
    )
)

print(result.to_dict())
```

Asynchronous use:

```python
import asyncio

from savings_goal_planner import GoalRequest, SavingsGoalPlannerClient

async def main():
    client = SavingsGoalPlannerClient()
    result = await client.calculate_goal_async(
        GoalRequest(goal_name="Emergency reserve", target_amount=60000, months=24)
    )
    print(result.monthly_required)

asyncio.run(main())
```

## Run examples

Each example reads environment variables, accepts `--env sandbox|production`, and prints JSON with `ensure_ascii=False` and indentation.

```bash
python scripts/examples/01_major_purchase_car.py --env sandbox
python scripts/examples/02_freelancer_equipment.py --env sandbox
python scripts/examples/03_retirement_gap.py --env sandbox
python scripts/examples/04_wedding_goal_with_inflation.py --env sandbox
python scripts/examples/05_compare_vehicle_candidates.py --env sandbox
python scripts/examples/06_business_tax_reserve.py --env sandbox
```

Example environment variables:

```bash
export SGP_TARGET=180000
export SGP_MONTHS=36
export SGP_CURRENT_SAVINGS=40000
export SGP_STORE_PATH="$(pwd)/example-goals.json"
```

## Run tests

```bash
pip install -e .
pip install -r requirements-dev.txt
pytest
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `README.md` | Installation and quick start |
| `CHANGELOG.md` | Keep a Changelog history |
| `LICENSE` | MIT license |
| `metadata.json` | Package metadata without creator attribution |
| `pyproject.toml` | Installable Python package configuration |
| `requirements-dev.txt` | Development and test dependencies |
| `savings_goal_planner/client.py` | Core calculations and typed client |
| `savings_goal_planner/cli.py` | Command-line implementation |
| `scripts/savings_goal_planner_client.py` | Script entry for client imports |
| `scripts/savings-goal-planner-cli.py` | Script wrapper for the CLI |
| `scripts/test_savings_goal_planner_client.py` | Pytest coverage |
| `scripts/examples/` | Runnable scenario scripts |
| `references/api-reference.md` | Official source and regulation reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Operational troubleshooting |
| `references/test-scenarios.md` | Scenario catalog |
| `references/migration-checklist.md` | Migration steps |
| `references/branding-audit.md` | Branding and attribution audit |
| `references/hebrew-qa-log.md` | Hebrew quality log |

## Safety and compliance notes

Treat results as scenario calculations. Do not present output as personal investment advice, pension advice, tax advice, or legal advice. Verify contribution caps, tax rates, eligibility rules, and product disclosures against official sources before using the output for client-facing or production decisions.
