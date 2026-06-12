# Freelancer Tax Calculator

Neutral Israeli tax-estimation package for `osek-patur` and `osek-murshe` scenarios. Calculate VAT, income-tax advances, National Insurance and health-insurance contribution estimates, osek patur ceiling risk, and cash reserve summaries.

The package is local and deterministic. It does not connect to the Tax Authority, National Insurance Institute, or a bookkeeping system. Version 2.2.0 uses web-validated 2026 defaults for VAT, osek patur ceiling, and basic National Insurance reserve planning. Treat defaults as planning values and update the configuration for the relevant tax year before relying on a report. The National Insurance model is a reserve estimate and does not replace official BTL base adjustments or notices.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with a saved scenario

Create a reusable scenario, extract the returned ID, and run the next step with that ID:

```bash
CREATE_RESPONSE=$(freelancer-tax-calculator create \
  --business-type osek-murshe \
  --revenue 300000 \
  --expenses 80000 \
  --input-vat 7200 \
  --advance-rate 0.10 \
  --advance-base revenue \
  --env sandbox \
  --json)

SCENARIO_ID=$(python -c 'import json, os; print(json.loads(os.environ["CREATE_RESPONSE"])["scenario_id"])')
freelancer-tax-calculator run "$SCENARIO_ID" --env sandbox --json
```

Direct calculation remains available:

```bash
freelancer-tax-calculator calculate \
  --business-type osek-patur \
  --revenue 116000 \
  --expenses 22000 \
  --advance-rate 0.06 \
  --advance-base revenue \
  --json
```

VAT-only estimate:

```bash
freelancer-tax-calculator vat \
  --business-type osek-murshe \
  --revenue 50000 \
  --input-vat 2400 \
  --json
```

## Environment variables

Set optional values before running examples or the CLI:

```bash
export FTC_ENV=sandbox
export FTC_REVENUE_ILS=300000
export FTC_EXPENSES_ILS=80000
export FTC_INPUT_VAT_ILS=7200
export FTC_ADVANCE_RATE=0.10
export FTC_ADVANCE_BASE=revenue
export FTC_STORE_DIR=.freelancer-tax-calculator/scenarios
```

Configuration overrides use `FTC_VAT_RATE`, `FTC_OSEK_PATUR_THRESHOLD_ANNUAL`, `FTC_NI_REDUCED_RATE`, `FTC_NI_REGULAR_RATE`, `FTC_NI_REDUCED_THRESHOLD_ANNUAL`, `FTC_NI_ANNUAL_CEILING`, and `FTC_MICRO_BUSINESS_EXPENSE_RATE`.

## Python usage

```python
from freelancer_tax_calculator import FreelancerTaxCalculator, FreelancerTaxInput

calculator = FreelancerTaxCalculator(environment="sandbox")
report = calculator.calculate(FreelancerTaxInput(
    business_type="osek-murshe",
    annual_revenue_ils="300000",
    deductible_expenses_ils="80000",
    input_vat_ils="7200",
    income_tax_advance_rate="0.10",
    income_tax_advance_base="revenue",
))
print(report.to_json())
```

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, anti-patterns, troubleshooting, and production checklist. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli accounting terminology and local formatting. |
| `references/api-reference.md` | Regulatory source map, local schema, examples, and error table. |
| `references/workflow-guide.md` | End-to-end workflows for osek patur, osek murshe, VAT period review, and accountant handoff. |
| `references/troubleshooting.md` | Diagnosis and recovery guidance. |
| `references/test-scenarios.md` | Manual and automated scenario catalogue with more than 20 concrete cases. |
| `references/migration-checklist.md` | Migration checklist from spreadsheets, old scripts, or ad hoc calculators. |
| `references/branding-audit.md` | Neutrality audit summary. |
| `references/hebrew-qa-log.md` | Hebrew review log. |
| `references/verification-log.md` | Web validation log with pass 1 and pass 2 sources. |
| `freelancer_tax_calculator_client.py` | Typed sync and async client implementation. |
| `freelancer_tax_calculator/` | Installable package interface and CLI module. |
| `scripts/freelancer_tax_calculator_client.py` | Underscored script copy for direct inspection and compatibility. |
| `scripts/freelancer-tax-calculator-cli.py` | Executable CLI wrapper. |
| `scripts/examples/` | Runnable examples that read environment variables and accept `--env sandbox|production`. |
| `scripts/test_freelancer_tax_calculator_client.py` | Pytest suite. |
| `metadata.json` | Package metadata without attribution fields. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Installable project metadata. |
| `requirements-dev.txt` | Development dependencies. |
