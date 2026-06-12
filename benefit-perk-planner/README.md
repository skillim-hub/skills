# Benefit & Perk Planner

Plan Israeli benefit and perk packages for small businesses, freelancers, consumers, and employees. The package includes English and Hebrew skill guides, implementation references, troubleshooting, test scenarios, migration support, a typed Python planner client, a Typer CLI, example scripts, and pytest coverage.

## Install for development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a plan and save the response:

```bash
python scripts/benefit-perk-planner-cli.py create \
  --env sandbox \
  --entity employer \
  --employees 12 \
  --budget 15000 \
  --store-dir .benefit-perk-planner > create-response.json
```

Extract the identifier from the create response:

```bash
PLAN_ID="$(python -c 'import json; print(json.load(open("create-response.json"))["plan_id"])')"
```

Use the extracted identifier in the next step:

```bash
python scripts/benefit-perk-planner-cli.py show \
  --env sandbox \
  --plan-id "$PLAN_ID" \
  --store-dir .benefit-perk-planner
```

Create JSON output without storing:

```bash
python scripts/benefit-perk-planner-cli.py plan \
  --env sandbox \
  --entity freelancer \
  --income 28000 \
  --cash-buffer-months 2 \
  --format json
```

Use a request file:

```json
{
  "entity_type": "employer",
  "employee_count": 12,
  "monthly_budget_ils": 15000,
  "goals": ["retention", "equity"],
  "work_model": "hybrid",
  "existing_benefits": ["mandatory pension"],
  "location": "Tel Aviv"
}
```

```bash
python scripts/benefit-perk-planner-cli.py from-file request.json --env sandbox --output plan.md
```

## Python usage

```python
from benefit_perk_planner_client import BenefitPlannerClient, BenefitRequest

client = BenefitPlannerClient(environment="sandbox")
request = BenefitRequest(
    entity_type="employer",
    employee_count=12,
    monthly_budget_ils=15000,
    goals=["retention", "equity"],
    existing_benefits=["mandatory pension"],
)

plan = client.plan(request)
print(plan.to_markdown())
```

Async usage:

```python
from benefit_perk_planner_client import AsyncBenefitPlannerClient, BenefitRequest

plan = await AsyncBenefitPlannerClient().plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600))
```

## Example scripts

Each example accepts `--env sandbox|production`, reads environment variables, and prints JSON with `ensure_ascii=False`.

```bash
BENEFIT_PLANNER_BUDGET_ILS=15000 \
BENEFIT_PLANNER_EMPLOYEE_COUNT=12 \
python scripts/examples/employer_hybrid_retention.py --env sandbox
```

Useful environment variables:

| Variable | Meaning |
|---|---|
| `BENEFIT_PLANNER_BUDGET_ILS` | Monthly budget in ₪ |
| `BENEFIT_PLANNER_EMPLOYEE_COUNT` | Number of employees |
| `BENEFIT_PLANNER_MONTHLY_INCOME_ILS` | Freelancer monthly income |
| `BENEFIT_PLANNER_CASH_BUFFER_MONTHS` | Freelancer reserve in months |
| `BENEFIT_PLANNER_GOALS` | Comma-separated goals |
| `BENEFIT_PLANNER_WORK_MODEL` | Work model |
| `BENEFIT_PLANNER_LOCATION` | Location |
| `BENEFIT_PLANNER_EXISTING_BENEFITS` | Comma-separated existing benefits |
| `BENEFIT_PLANNER_STORE` | Directory for stored plan JSON files |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English comprehensive operating guide |
| `SKILL_HE.md` | Hebrew comprehensive operating guide |
| `references/api-reference.md` | Israeli official-source and integration reference |
| `references/workflow-guide.md` | End-to-end implementation workflows |
| `references/troubleshooting.md` | Diagnosis and recovery guide |
| `references/test-scenarios.md` | Concrete validation scenarios |
| `references/migration-checklist.md` | Migration from informal perks to policy |
| `references/branding-audit.md` | Branding, author, logo, and Markdown emoji audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log |
| `references/verification-log.md` | Web validation and second-pass verification log |
| `scripts/benefit_perk_planner_client.py` | Typed sync and async planner client |
| `scripts/benefit_perk_planner_cli.py` | Typer CLI implementation |
| `scripts/benefit-perk-planner-cli.py` | CLI launcher |
| `scripts/test_benefit_perk_planner_client.py` | pytest suite |
| `scripts/examples/` | Runnable examples |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep a Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Package and tooling config |
| `requirements-dev.txt` | Development dependencies |

## Test

```bash
python -m compileall scripts/ -q
pytest -q
```

## Scope and limitations

The planner provides structured decision support and implementation checklists. It does not provide legal, tax, accounting, pension, insurance, or investment advice. Verify current statutory rates, annual ceilings, payroll treatment, provider terms, and documentation rules before launch.
