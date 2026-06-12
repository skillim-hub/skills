# Migration Checklist

Use this checklist when moving from the previous package layout to version 2.1.0.

## Python imports

- Replace dynamic loading of `scripts/stock-options-tax-advisor-client.py` with package imports.
- Use `from stock_options_tax_advisor import StockOptionsTaxAdvisorClient, EquityScenario`.
- Keep `scripts/stock_options_tax_advisor_client.py` only as a compatibility import path for local scripts.

## CLI

- Prefer the installed command `stock-options-tax-advisor` after `pip install -e .`.
- The direct wrapper remains at `scripts/stock-options-tax-advisor-cli.py`.
- Pass `--env sandbox` for examples and `--env production` for reviewed production assumptions.

## Tests

- Install development dependencies with `pip install -r requirements-dev.txt`.
- Run `python -m compileall scripts/ -q` before pytest.
- Run `pytest` from the package root.

## Documentation

- Use `SKILL.md` for English workflows.
- Use `SKILL_HE.md` for Hebrew client-facing terminology.
- Use `references/hebrew-qa-log.md` and `references/branding-audit.md` to confirm the correction pass.
