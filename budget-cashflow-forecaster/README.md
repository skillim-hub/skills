# Budget & Cash-Flow Forecaster

A neutral, local-first skill package for forecasting cash flow for Israeli small businesses, freelancers, consumers, and micro-organizations.

## Install

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Quick start

```bash
budget-cashflow-forecaster validate scripts/examples/baseline_scenario.json
budget-cashflow-forecaster create scripts/examples/baseline_scenario.json --env sandbox > create-response.json
FORECAST_ID=$(python -c "import json; print(json.load(open('create-response.json', encoding='utf-8'))['id'])")
budget-cashflow-forecaster show "$FORECAST_ID"
budget-cashflow-forecaster forecast scripts/examples/baseline_scenario.json --env sandbox --json-output
```

## Python usage

```python
from budget_cashflow_forecaster import CashFlowForecaster

result = CashFlowForecaster().forecast_from_json(
    "scripts/examples/baseline_scenario.json",
    environment="sandbox",
)
print(result.as_dict()["summary"])
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide |
| `SKILL_HE.md` | Hebrew guide |
| `metadata.json` | Skill metadata without creator fields |
| `references/api-reference.md` | Israeli regulation and data reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | 25 concrete testing scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding and visual-reference audit |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance log |
| `references/verification-log.md` | Two-pass web validation log |
| `budget_cashflow_forecaster/` | Installable Python module |
| `scripts/budget_cashflow_forecaster_client.py` | Compatibility import wrapper |
| `scripts/budget-cashflow-forecaster-cli.py` | Executable CLI wrapper |
| `scripts/test_budget_cashflow_forecaster_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenarios |
| `CHANGELOG.md` | Keep-a-Changelog format |
| `LICENSE` | MIT license |
| `pyproject.toml` | Build and tool configuration |
| `requirements-dev.txt` | Development dependencies |

## Environment mode

Use `--env sandbox` for examples, tests, and planning drafts. Use `--env production` only after confirming tax assumptions, payment timing, and reporting obligations with official sources or a licensed Israeli accountant.
