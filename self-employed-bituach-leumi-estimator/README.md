# self-employed-bituach-leumi-estimator-enhanced v3

A small, dependency-light Python package and ChatGPT skill reference for estimating 2026 Israeli self-employed National Insurance and health-insurance contributions.

## Quick start

```bash
python -m scripts.cli --monthly-income 12000 --months 3 --year 2026
```

Expected total for the official NII example is about ₪3,864 for the quarter.

## Validate locally

```bash
python -m pytest -q
python -m compileall -q scripts tests
```

## Caveats

This package estimates. Binding amounts are set by Israeli law, National Insurance records, final tax assessments, and applicable coordination rules.
