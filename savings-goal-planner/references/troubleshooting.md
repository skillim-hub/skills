# Troubleshooting

## Installation issues

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: savings_goal_planner` | Package was not installed | Run `pip install -e .` from the package root |
| `click` is missing | Runtime dependency was not installed | Run `pip install -e .` |
| `pytest_asyncio` is missing | Development dependencies were not installed | Run `pip install -r requirements-dev.txt` |
| Command `savings-goal-planner` is not found | Console script is not on the active environment path | Activate the virtual environment and reinstall with `pip install -e .` |
| Script wrapper fails from another directory | Package is not installed | Use the console script after editable install |

## Calculation issues

| Symptom | Cause | Fix |
|---|---|---|
| Monthly required is unexpectedly high | Target was entered in today's ₪ and inflated, but the amount was already future nominal | Pass `--future-amount` |
| Monthly required is zero | Current savings and current deposits already cover the target | Review `projected_total_value` and `shortfall_at_current_rate` |
| Vehicle warning appears | Horizon, liquidity, or wrapper restrictions are incompatible | Select a different vehicle or change horizon |
| Retirement result is very sensitive | Long horizons amplify return assumptions | Run low-return and longevity stress cases |
| Output differs from bank quote | Product-specific fee, tax, or rate differs from preset | Override `--annual-return`, `--annual-fee`, and `--tax-rate-on-gain` |
| Business reserve is too low | VAT, income tax, and National Insurance were combined incorrectly | Model separate reserve goals |

## Stored-goal issues

| Symptom | Cause | Fix |
|---|---|---|
| `goal not found` | Wrong id, environment, or store path | Use the exact id from `create-goal` and pass the same `--env` and `--store` |
| Store file is corrupt | Manual edit created invalid JSON | Restore a backup or replace the file with `[]` |
| Production goal appears in sandbox | Store path was reused across environments | Use separate store files or rely on environment default paths |
| Duplicate goals exist | Goal was created repeatedly after assumption changes | Keep duplicates as audit history or delete obsolete records |

## Hebrew output issues

| Symptom | Cause | Fix |
|---|---|---|
| ₪ displays incorrectly | Terminal encoding is not UTF-8 | Use a UTF-8 terminal or redirect JSON to a UTF-8 file |
| Hebrew text appears reversed in a plain terminal | Bidirectional rendering limitation | Open the JSON in an editor with bidirectional text support |
| Dates are inconsistent | Mixed locale convention | Use DD/MM/YYYY in Hebrew-facing material |

## Validation failures

| Error | Meaning | Fix |
|---|---|---|
| `target_amount must be non-negative` | Target cannot be negative | Enter a non-negative amount |
| `months must be greater than zero` | Horizon must be positive | Enter at least one month |
| `unknown vehicle_key` | Preset key is invalid | Run `savings-goal-planner vehicles` |
| `tax_rate_on_gain must be between 0 and 1` | Tax rate must be a decimal fraction | Use `0.25` for 25 percent |
| `contribution_timing must be 'end' or 'beginning'` | Deposit timing is invalid | Use `--timing end` or `--timing beginning` |
| `environment must be sandbox or production` | Store environment is invalid | Use `--env sandbox` or `--env production` |

## Diagnostic commands

Run syntax checks:

```bash
python -m compileall scripts/ -q
```

Run tests:

```bash
pytest
```

Inspect vehicle presets:

```bash
savings-goal-planner vehicles --format json
```

Create and retrieve a stored goal:

```bash
CREATE_RESPONSE="$(savings-goal-planner create-goal --target 10000 --months 10 --env sandbox --format json)"
GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
savings-goal-planner show-goal --id "$GOAL_ID" --env sandbox --format json
```

## Escalation checklist

Before relying on an output:

1. Confirm inputs.
2. Confirm whether target is today's ₪ or a future nominal amount.
3. Confirm source dates for rates, inflation, and tax assumptions.
4. Run sensitivity cases.
5. Check affordability against cash flow.
6. Review vehicle restrictions.
7. Use professional advice for personal investment, pension, tax, or legal decisions.
