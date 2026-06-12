# Loan Amortization Planner

Offline loan-amortization planning package for Israeli fixed-rate, prime-linked, and CPI-linked loans. It supports repayment schedules, stress cases, and offer comparisons in ₪ for small businesses, freelancers, and consumers.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Quick start with a reusable scenario id

Create a local scenario record and extract its id from the JSON response:

```bash
SCENARIO_ID=$(
  python -m loan_amortization_planner.cli create-scenario \
    --name "equipment fixed loan" \
    --principal 250000 \
    --term-months 72 \
    --start-date 01/07/2026 \
    --rate-type fixed \
    --annual-interest-rate 0.065 \
    --origination-fee 1200 \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])'
)
```

Use that id in the next step:

```bash
python -m loan_amortization_planner.cli schedule "$SCENARIO_ID" \
  --json-out schedule.json \
  --csv-out schedule.csv
```

Compare several offers:

```bash
python -m loan_amortization_planner.cli compare examples/offers.json
```

Run tests:

```bash
pytest -q
python -m compileall scripts/ -q
```

## Python quick start

```python
from loan_amortization_planner import LoanScenario, build_schedule

scenario = LoanScenario.from_mapping({
    "name": "equipment fixed loan",
    "principal": "250000",
    "term_months": 72,
    "start_date": "01/07/2026",
    "rate_type": "fixed",
    "annual_interest_rate": "0.065",
    "origination_fee": "1200"
})
schedule = build_schedule(scenario)
print(schedule.summary.as_dict())
```

## File index

| File | Description |
|---|---|
| `SKILL.md` | English guide with examples, decision trees, edge cases, anti-patterns, troubleshooting, and production checklist |
| `SKILL_HE.md` | Hebrew guide using Israeli professional terminology and local date/currency conventions |
| `loan_amortization_planner/` | Installable Python package |
| `references/api-reference.md` | Offline API contract, regulatory/data-source reference, request/response examples, and errors |
| `references/workflow-guide.md` | End-to-end workflows for offer comparison, freelancer cash flow, CPI stress testing, balloon loans, and reconciliation |
| `references/troubleshooting.md` | Operational fixes for validation errors and lender-reconciliation differences |
| `references/test-scenarios.md` | Manual and automated scenario ideas |
| `references/migration-checklist.md` | Migration checklist for replacing spreadsheets or prior versions |
| `references/branding-audit.md` | Packaging neutrality audit |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance change log |
| `references/verification-log.md` | Two-pass web validation log for official Israeli sources |
| `scripts/loan_amortization_planner_client.py` | Underscored compatibility entry point for the client |
| `scripts/loan_amortization_planner_cli.py` | Underscored compatibility entry point for the CLI |
| `scripts/test_loan_amortization_planner_client.py` | pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |

## Development

```bash
pytest -q
python -m compileall scripts/ -q
python scripts/examples/compare_three_offers.py --env sandbox
python scripts/loan_amortization_planner_cli.py validate examples/fixed-equipment.json
```

## Important limitations

- The package does not retrieve live Bank of Israel, CPI, lender, or tax data.
- The package does not calculate VAT, income tax, National Insurance, depreciation, or lender APR disclosures.
- Lender statements may differ because of daily interest, CPI publication conventions, business-day shifts, fees, and internal rounding.
- Treat output as planning support and reconcile against lender documents before making a binding decision.


## Current verified baseline

As of 2026-06-02, official-source validation found a Bank of Israel rate of 3.75%, an implied prime base of 5.25%, and a standard VAT rate of 18%. Refresh these values before production use.
