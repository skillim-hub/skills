# Household Budget Planner

A neutral skill package for tracking Israeli household budgets, consumer spending, freelancer cash flow, small-business reserves, VAT-aware expenses, and savings goals in ₪.

## What it does

- Track monthly income, expenses, transfers, and savings goals.
- Use Israeli-friendly categories such as arnona, Kupat Cholim, transport, childcare, VAT reserve, and business expenses.
- Format public Hebrew guidance with ₪ and `DD/MM/YYYY`; accept `DD-MM-YYYY`, `DD/MM/YYYY`, and ISO dates in code.
- Include English and Hebrew guides, source references, workflows, troubleshooting, migration checklist, tests, examples, and a CLI.
- Keep tax, legal, insurance, pension, investment, and mortgage decisions outside the planner and direct verification to official sources.

## Install for local use

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained budget identifier

Create a budget, extract the returned identifier, and use it in the next command.

```bash
CREATE_RESPONSE=$(household-budget-planner create --month 05-2026 --output budget.json --env sandbox --json)
BUDGET_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["budget_id"])' <<< "$CREATE_RESPONSE")

household-budget-planner add budget.json \
  --budget-id "$BUDGET_ID" \
  --date 12-05-2026 \
  --amount 245.90 \
  --kind expense \
  --category food \
  --description "Supermarket"

household-budget-planner goal budget.json \
  --budget-id "$BUDGET_ID" \
  --name "Emergency fund" \
  --target 30000 \
  --current 18000 \
  --due 31-12-2026

household-budget-planner summary budget.json --budget-id "$BUDGET_ID" --month 05-2026
```

## Python quick start

```python
from household_budget_planner import HouseholdBudgetPlannerClient

client = HouseholdBudgetPlannerClient.for_month("05-2026")
client.add_transaction(date="01-05-2026", amount=15000, kind="income", category="salary")
client.add_transaction(date="02-05-2026", amount=6200, kind="expense", category="housing")
print(client.render_text_summary())
```

## Examples

Each example accepts an environment flag and reads environment variables where useful.

```bash
python scripts/examples/01_monthly_household.py --env sandbox
python scripts/examples/02_freelancer_vat_split.py --env production
```

Useful environment variables:

| Variable | Purpose |
|---|---|
| `HBP_MONTH` | Budget month, such as `05-2026` |
| `HBP_VAT_RATE` | VAT rate used for VAT-inclusive calculations |
| `HBP_OUTPUT` | Optional output path for generated JSON |
| `HBP_TARGET_AMOUNT` | Savings target for goal examples |
| `HBP_CURRENT_AMOUNT` | Current savings balance for goal examples |

## Web-validated source notes

The 2.1.0 package includes `references/verification-log.md`, which records two-pass validation of the Israeli official sources used by the planner. The pass verified the current 18% VAT example rate, the 2026 osek patur threshold of ₪122,833, and official API patterns for Bank of Israel and CBS data.

## Run checks

```bash
pytest scripts/test_household_budget_planner_client.py
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Israeli source, API, regulation, and data normalization guide |
| `references/workflow-guide.md` | End-to-end household, freelancer, card audit, and savings workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | Concrete validation scenarios |
| `references/migration-checklist.md` | Migration checklist from spreadsheets or old structures |
| `references/branding-audit.md` | Branding and visual-reference audit report |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance change log |
| `household_budget_planner/` | Installable Python package |
| `scripts/household_budget_planner_client.py` | Underscored client compatibility entry point |
| `scripts/household_budget_planner_cli.py` | Script wrapper for the CLI |
| `scripts/test_household_budget_planner_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Package metadata |
| `CHANGELOG.md` | Keep-a-Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Python project metadata |
| `requirements-dev.txt` | Development dependencies |

## Data format

A budget JSON file contains:

```json
{
  "budget_id": "budget_example123",
  "month": "05-2026",
  "currency": "ILS",
  "environment": "sandbox",
  "vat_rate": 0.18,
  "transactions": [
    {
      "date": "01-05-2026",
      "amount": 15000,
      "kind": "income",
      "category": "salary",
      "description": "Net salary"
    }
  ],
  "savings_goals": [
    {
      "name": "Emergency fund",
      "target_amount": 30000,
      "current_amount": 18000,
      "due_date": "31-12-2026"
    }
  ],
  "category_limits": {},
  "notes": []
}
```

## Professional boundaries

Verify current rates and legal requirements through official sources before production use. Use a qualified professional for tax filings, deductible expenses, payroll, VAT reporting, insurance, pension, investment, mortgage, and insolvency decisions.
