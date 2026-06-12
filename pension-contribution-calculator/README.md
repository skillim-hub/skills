# Pension Contribution Calculator

Neutral skill package for calculating Israeli pension, Keren Hishtalmut, and Bituach Menahalim contribution splits for employees, employers, freelancers, and consumers.

## Install

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Python 3.10 or newer is recommended.

## Quick start

Create a calculation record, extract its id, then use that id in a verification step:

```bash
python scripts/pension-contribution-calculator-cli.py employee --gross-salary 12000 --hishtalmut --json --record > /tmp/pcc-create-response.json
calc_id=$(python -c 'import json; print(json.load(open("/tmp/pcc-create-response.json", encoding="utf-8"))["id"])')
python scripts/pension-contribution-calculator-cli.py explain --from-json /tmp/pcc-create-response.json --id "$calc_id"
```

Run common calculations:

```bash
python scripts/pension-contribution-calculator-cli.py employee --gross-salary 20000 --hishtalmut --json
python scripts/pension-contribution-calculator-cli.py self-employed --annual-income 180000 --age 36 --json
python scripts/pension-contribution-calculator-cli.py compare --gross-salary 24000 --hishtalmut --json
pytest scripts/test_pension-contribution-calculator_client.py
```

Use the importable module after installation:

```python
from pension_contribution_calculator_client import PensionContributionCalculatorClient

client = PensionContributionCalculatorClient()
result = client.calculate_employee(12_000, include_hishtalmut=True)
print(result.total_monthly_deposit)
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with examples, decision trees, edge cases, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide using Israeli professional terminology and ₪ localization |
| `references/api-reference.md` | Source registry, local helper contract, CLI reference, examples, and error tables |
| `references/workflow-guide.md` | End-to-end workflows for onboarding, payroll, freelancer year-end, and product comparison |
| `references/troubleshooting.md` | Detailed fixes for input, payroll, freelancer, product, testing, and escalation issues |
| `references/test-scenarios.md` | Concrete validation scenarios |
| `references/migration-checklist.md` | Migration and annual rate-update checklist |
| `references/branding-audit.md` | Branding, attribution, visual asset, and emoji audit results |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization review log |
| `references/rate-table-2026.md` | Default shipped rate table |
| `references/verification-log.md` | Web validation log with pass 1 and pass 2 sources |
| `scripts/pension_contribution_calculator_client.py` | Typed synchronous and asynchronous calculation helper |
| `scripts/pension-contribution-calculator-cli.py` | Typer CLI |
| `scripts/test_pension-contribution-calculator_client.py` | Pytest suite with more than 20 tests |
| `scripts/examples/` | Runnable examples using environment variables and `--env sandbox|production` |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog format |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project configuration |
| `requirements-dev.txt` | Development dependencies |

## Main concepts

- Use gross monthly salary for cash and benefit calculations.
- Use pensionable salary for pension deposits when the employment agreement defines a separate base.
- Use the comprehensive pension fund monthly deposit cap to route excess deposits.
- Use Keren Hishtalmut salary ceiling to identify taxable employer excess.
- Use annual net taxable income for freelancers.
- Use explicit rate tables for annual updates.

## Development

Run tests:

```bash
pytest -q
```

Run a CLI smoke test:

```bash
python scripts/pension-contribution-calculator-cli.py employee --gross-salary 10000 --json
```

Run examples:

```bash
PCC_GROSS_SALARY=15000 python scripts/examples/employee_basic.py --env sandbox
PCC_ANNUAL_INCOME=180000 PCC_AGE=36 python scripts/examples/freelancer_mandatory.py --env production
```
