# Mortgage & Loan Eligibility Checker

Neutral local toolkit for preliminary Israeli mortgage eligibility screening. It calculates LTV, estimated monthly repayment, DSR, maximum loan by LTV, maximum loan by repayment capacity, and practical remediation steps.

## Install

```bash
pip install -e .
pip install -r requirements-dev.txt
```

The calculator uses the Python standard library. The CLI uses Typer.

## Quick start

Create a reusable scenario, extract the scenario id from the create response, then evaluate the same scenario in the next step.

```bash
mortgage-loan-eligibility create   --output scenarios.json   --property-value 2400000   --loan-amount 1680000   --status single_home   --net-income 28000   --existing-debt 1500   --annual-rate 5.25   --term-years 25   --cash-equity 720000   --json > create-response.json

SCENARIO_ID=$(python -c "import json; print(json.load(open('create-response.json', encoding='utf-8'))['scenario_id'])")

mortgage-loan-eligibility evaluate   --input scenarios.json   --scenario-id "$SCENARIO_ID"   --env sandbox   --json
```

Direct one-off calculation:

```bash
mortgage-loan-eligibility calculate   --property-value 2400000   --loan-amount 1680000   --status single_home   --net-income 28000   --existing-debt 1500   --annual-rate 5.25   --term-years 25   --cash-equity 720000   --json
```

File workflow:

```bash
mortgage-loan-eligibility sample --path request.json
mortgage-loan-eligibility from-file request.json --env sandbox
```

## Python usage

```python
from mortgage_loan_eligibility_client import MortgageEligibilityClient

result = MortgageEligibilityClient().calculate({
    "property_value": 2400000,
    "requested_loan_amount": 1500000,
    "property_status": "single_home",
    "net_monthly_income": 30000,
    "existing_monthly_debt": 1000,
    "annual_rate": 5.0,
    "term_years": 25,
    "cash_equity": 900000
})
print(result.to_json())
```

## Environment defaults

Set environment-specific defaults for scripts and CLI commands.

```bash
export MLE_SANDBOX_DEFAULT_ANNUAL_RATE=5.25
export MLE_SANDBOX_DEFAULT_TERM_YEARS=25
export MLE_SANDBOX_DSR_LIMIT=50
export MLE_PRODUCTION_DEFAULT_ANNUAL_RATE=5.75
export MLE_PRODUCTION_DEFAULT_TERM_YEARS=25
export MLE_PRODUCTION_DSR_LIMIT=45
```

## File index

```text
SKILL.md                                      English guide
SKILL_HE.md                                   Hebrew guide
README.md                                     Install and quick start
CHANGELOG.md                                  Keep-a-Changelog history
LICENSE                                       MIT license
metadata.json                                 Skill metadata
pyproject.toml                                Project configuration
requirements-dev.txt                          Development dependencies
references/api-reference.md                   Regulation and interface reference
references/workflow-guide.md                  End-to-end workflows
references/troubleshooting.md                 Troubleshooting guide
references/test-scenarios.md                  20+ scenarios
references/migration-checklist.md             Migration guide
references/branding-audit.md                  Branding and attribution audit
references/hebrew-qa-log.md                   Hebrew quality-assurance log
references/verification-log.md                Two-pass web validation log
scripts/mortgage_loan_eligibility_client.py   Typed sync and async calculator
scripts/mortgage_loan_eligibility_cli.py      Importable Typer CLI module
scripts/mortgage-loan-eligibility-cli.py      Direct CLI wrapper
scripts/test_mortgage_loan_eligibility_client.py  Pytest suite
scripts/examples/                             Runnable examples
```

## Development

```bash
python -m pytest scripts
python -m compileall scripts/ -q
python scripts/examples/01_first_home.py --env sandbox
```

## Interpretation notes

- Treat results as preliminary screening, not lender approval.
- Validate current Bank of Israel and lender policy before production use.
- Store policy thresholds with every production result.
- Protect borrower data and avoid logging sensitive identifiers.
