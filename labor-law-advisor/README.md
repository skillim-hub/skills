# Labor-Law Advisor

Neutral skill package for practical Israeli labor-law guidance. It structures answers, calculations, workflows, and escalation paths for small businesses, freelancers, employees, and consumers.

## What it covers

- Israeli minimum wage checks.
- Overtime and weekly rest triage.
- Severance pay and Section 14.
- Parental, pregnancy, fertility, adoption, surrogacy, and return-to-work rights.
- Vacation, sick leave, pension, convalescence pay, notice periods, and payslips.
- Histadrut, collective agreements, extension orders, and sectoral checks.
- Freelancer-vs-employee risk and household worker obligations.

## Important limitation

This package provides legal information and workflow support. It does not replace advice from a licensed Israeli labor-law attorney, payroll professional, accountant, union representative, or official government body. Verify date-sensitive rates against official sources before payroll action.

## Install

```bash
cd labor-law-advisor
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained case identifier

Create a local advisory case, extract the `case_id` from the JSON response, then use it in the next command.

```bash
CREATE_RESPONSE=$(labor-law-advisor create-case --category overtime --env sandbox --subject "April payroll")
CASE_ID=$(python -c 'import json, sys; print(json.load(sys.stdin)["case_id"])' <<< "$CREATE_RESPONSE")
labor-law-advisor case-summary --case-id "$CASE_ID" --env sandbox
```

Run calculation commands:

```bash
labor-law-advisor min-wage --monthly-salary 3000 --position-fraction 0.5 --env sandbox
labor-law-advisor overtime --hourly-rate 40 --daily-hours 11 --daily-threshold 8.6 --env sandbox
labor-law-advisor severance --monthly-salary 12000 --years 3 --months 4 --env sandbox
labor-law-advisor sick-pay --daily-wage 500 --sick-days 5 --env sandbox
labor-law-advisor vacation --years 6 --workweek-days 5 --env sandbox
```

The wrapper script remains available after editable installation:

```bash
python scripts/labor-law-advisor-cli.py min-wage --monthly-salary 3000 --position-fraction 0.5 --env sandbox
```

Run scenario scripts. Each script reads environment variables, accepts `--env sandbox|production`, and prints JSON with `ensure_ascii=False` and two-space indentation.

```bash
python scripts/examples/minimum_wage_part_time.py --env sandbox
python scripts/examples/overtime_day.py --env sandbox
python scripts/examples/severance_section14.py --env sandbox
python scripts/examples/parental_rights_triage.py --env sandbox
python scripts/examples/collective_agreement_check.py --env sandbox
python scripts/examples/classification_invoice_worker.py --env sandbox
```

## Python usage

```python
from labor_law_advisor_client import LaborLawAdvisor

advisor = LaborLawAdvisor()
result = advisor.minimum_wage(monthly_salary=3000, position_fraction=0.5)
print(result.to_dict())
```

Async usage:

```python
import asyncio
from labor_law_advisor_client import LaborLawAdvisor

async def main():
    advisor = LaborLawAdvisor()
    result = await advisor.aminimum_wage(hourly_wage=34, regular_hours=120)
    print(result.to_dict())

asyncio.run(main())
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli professional terminology, ₪ formatting, and DD/MM/YYYY dates |
| `references/api-reference.md` | Official-source reference, local helper interface, examples, and error table |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Diagnostic guide for common symptoms and escalation triggers |
| `references/test-scenarios.md` | Concrete test scenarios |
| `references/migration-checklist.md` | Migration steps from a prior package |
| `references/branding-audit.md` | Attribution, decorative-image, and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log |
| `references/verification-log.md` | Web validation log with two-pass source checks |
| `scripts/labor_law_advisor_client.py` | Typed sync and async calculation and triage helper |
| `scripts/labor_law_advisor_cli.py` | Import-friendly Typer CLI module |
| `scripts/labor-law-advisor-cli.py` | Executable CLI wrapper |
| `scripts/test_labor-law-advisor_client.py` | Pytest suite with more than 20 tests |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Neutral package metadata |
| `CHANGELOG.md` | Keep-a-Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project metadata, package configuration, console script, and pytest config |
| `requirements-dev.txt` | Development and test requirements |

## Development

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
labor-law-advisor --help
```

## Verification before use

- Confirm there are no attribution claims or visual assets.
- Confirm rates have effective dates.
- Review `references/verification-log.md` and confirm official sources again before payroll action.
- Confirm collective agreement coverage is not assumed without sector, role, employer type, location, and date.
- Confirm protected-status cases are escalated before dismissal, non-renewal, pay reduction, or hours reduction.
