# Migration Checklist

## From earlier package versions

Use this checklist when moving from a script-only package to version 2.2.0.

### Python imports

Replace dynamic file imports with package imports.

Before:

```python
import importlib.util
from pathlib import Path

path = Path("scripts/savings-goal-planner-client.py")
```

After:

```python
from savings_goal_planner import GoalRequest, SavingsGoalPlannerClient
```

### Client file naming

- Remove references to `scripts/savings-goal-planner-client.py`.
- Use `savings_goal_planner` for package imports.
- Use `scripts/savings_goal_planner_client.py` only as a script-compatible client entry point.

### Installation

Run:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Command-line workflows

Replace direct-only examples with stored workflow examples when repeat review is needed.

Before:

```bash
python scripts/savings-goal-planner-cli.py goal --target 10000 --months 10
```

After:

```bash
CREATE_RESPONSE="$(savings-goal-planner create-goal --target 10000 --months 10 --env sandbox --format json)"
GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
savings-goal-planner show-goal --id "$GOAL_ID" --env sandbox --format json
```

### Test migration

1. Install the package with `pip install -e .`.
2. Run `pytest`.
3. Run `python -m compileall scripts/ -q`.
4. Update any tests that import from a hyphenated filename.
5. Update asynchronous tests to use `pytest-asyncio`.

### Metadata migration

- Keep `metadata.json` without creator attribution.
- Bump version when any public file changes.
- Add a changelog entry for every release.
- Keep license text as MIT with the required neutral holder wording.

### Documentation migration

- Remove status markers, image references, and visual marks.
- Remove public Markdown emoji.
- Use neutral imperative voice.
- Update Hebrew text to use professional Israeli terminology.
- Use ₪ and DD/MM/YYYY in Hebrew-facing documentation.
- Keep source validation guidance in `references/api-reference.md`.

### Operational migration

| Area | Required action |
|---|---|
| Stored goals | Choose sandbox or production store path |
| Examples | Pass `--env sandbox` or `--env production` |
| Environment variables | Prefix custom values with `SGP_` |
| Source validation | Record official source date before production use |
| Vehicle assumptions | Replace presets with product-specific data |
| Retirement analysis | Keep real-return model separate from nominal purchase goals |


## From version 2.1.0 to 2.2.0

- Replace `--state-pension` examples with `--expected-pension`. The old option remains accepted as a compatibility alias.
- Revalidate stored scenario assumptions against `references/verification-log.md` before using 2026 tax, National Insurance, or provident-fund caps.
- Replace any 2025 investment provident fund cap of ₪81,711 with the 2026 cap of ₪83,641 when modeling a 2026 contribution limit.
- Keep product return, fee, and tax assumptions in explicit input fields instead of treating defaults as official rates.
