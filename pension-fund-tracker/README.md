# Pension Fund Performance Tracker

Information-only tooling and guidance for tracking Israeli pension fund returns and fees using public Pensia Net and official Israeli public data.

The package supports reproducible normalization, validation, comparison, ranking, and fee-impact estimation. It does not provide pension advice, investment advice, insurance advice, tax advice, or personal recommendations.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
pension-fund-tracker --help
```

## Quick start

Create a normalized response, extract a fund id from that response, and pass it into the next command.

```bash
cat > sample.csv <<'CSV'
מספר קופה,שם קופה,שם גוף מנהל,תאריך דיווח,תשואה 36 חודשים אחרונים,דמי ניהול מצבירה,דמי ניהול מהפקדה
12345,קרן א,גוף א,31/12/2025,18.2,0.20,1.50
67890,קרן ב,גוף ב,31/12/2025,17.9,0.24,1.20
CSV

pension-fund-tracker normalize sample.csv --output normalized.json
FUND_ID=$(python - <<'PY'
import json
rows = json.load(open("normalized.json", encoding="utf-8"))
print(rows[0]["fund_id"])
PY
)
pension-fund-tracker compare normalized.json "$FUND_ID"
pension-fund-tracker rank normalized.json --metric trailing_36m_return_pct --top 10
```

Use the package directly after installation.

```python
from pension_fund_tracker import PensionFundTrackerClient

client = PensionFundTrackerClient()
records = client.load_csv("sample.csv")
print(client.validate_records(records))
```

## CLI commands

```bash
pension-fund-tracker normalize sample.csv --output normalized.json
pension-fund-tracker validate normalized.json
pension-fund-tracker rank normalized.json --metric trailing_36m_return_pct --top 10
pension-fund-tracker compare normalized.json 12345 67890
pension-fund-tracker fee-impact --monthly-contribution 2000 --years 20 --annual-return 5 --deposit-fee 1.5 --asset-fee 0.2
pension-fund-tracker fetch-ckan RESOURCE_ID --output normalized.json --max-records 1000
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Public data/API and regulation reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | Manual and automated test scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Neutrality and visual-asset audit |
| `references/hebrew-qa-log.md` | Hebrew terminology QA log |
| `references/verification-log.md` | Web-validated source and regulation log |
| `src/pension_fund_tracker/` | Installable Python package |
| `scripts/pension_fund_tracker_client.py` | Underscored client implementation entry point |
| `scripts/pension-fund-tracker-cli.py` | CLI wrapper |
| `scripts/test_pension_fund_tracker_client.py` | Pytest suite |
| `scripts/examples/` | Runnable examples |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project metadata |
| `requirements-dev.txt` | Development dependencies |

## Required report notice

Use outputs for information only. Confirm public data against the official source before operational decisions. Ask a licensed professional for personal pension, investment, insurance, tax, or legal advice.
