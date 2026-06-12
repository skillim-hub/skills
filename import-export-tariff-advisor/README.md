# Import/Export Tariff Advisor

Bilingual guidance and local tooling for estimating Israeli import taxes: customs duty, purchase tax, VAT, and landed cost. The package supports Israeli small businesses, freelancers, and consumers preparing a practical pre-import estimate based on tariff-code workflows and official-source verification.

## Install for local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create and store an estimate, then extract its identifier and use it in the next command.

```bash
CREATE_RESPONSE="$(import-export-tariff-advisor create \
  --description "Bluetooth headphones" \
  --goods-value 120 \
  --shipping 20 \
  --exchange-rate-to-ils 3.70 \
  --duty-rate 0 \
  --purchase-tax-rate 0 \
  --vat-rate 0.18 \
  --env sandbox \
  --json)"

ESTIMATE_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["estimate_id"])' <<< "$CREATE_RESPONSE")"

import-export-tariff-advisor show "$ESTIMATE_ID" --json
```

Run a direct one-off estimate without storing it:

```bash
import-export-tariff-advisor estimate \
  --description "Bluetooth headphones" \
  --goods-value 120 \
  --shipping 20 \
  --exchange-rate-to-ils 3.70 \
  --duty-rate 0 \
  --purchase-tax-rate 0 \
  --vat-rate 0.18 \
  --non-tax-fees-ils 35 \
  --env sandbox \
  --json
```

Use the installable package in Python:

```python
from import_export_tariff_advisor import TariffAdvisorClient

client = TariffAdvisorClient()
estimate = client.estimate(
    description="Laptop computer",
    goods_value=1000,
    shipping=60,
    exchange_rate_to_ils=3.70,
    duty_rate=0.0,
    purchase_tax_rate=0.0,
    vat_rate=0.18,
    environment="sandbox",
)
print(estimate.to_json(ensure_ascii=False, indent=2))
```

## Environment variables used by examples

Examples read these optional variables:

| Variable | Purpose | Default |
|---|---|---|
| `TARIFF_ADVISOR_ENV` | `sandbox` or `production` | `sandbox` |
| `TARIFF_ADVISOR_EXCHANGE_RATE_TO_ILS` | Currency conversion to ₪ | scenario default |
| `TARIFF_ADVISOR_VAT_RATE` | VAT decimal rate | `0.18` |
| `TARIFF_ADVISOR_STORE` | Local estimate store path | `.tariff-advisor-estimates.json` |

Each example also accepts `--env sandbox` or `--env production`.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Official-source and integration reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Diagnostic guide |
| `references/test-scenarios.md` | 30 concrete validation scenarios |
| `references/migration-checklist.md` | Migration and acceptance checklist |
| `references/branding-audit.md` | Neutrality and visual-asset audit |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance notes |
| `import_export_tariff_advisor/` | Installable Python package |
| `scripts/import_export_tariff_advisor_client.py` | Underscored compatibility import |
| `scripts/import-export-tariff-advisor-cli.py` | Executable CLI wrapper |
| `scripts/test_import_export_tariff_advisor_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata |
| `pyproject.toml` | Python packaging metadata |
| `requirements-dev.txt` | Development dependencies |
| `CHANGELOG.md` | Keep a Changelog history |
| `LICENSE` | MIT license |

## Web validation status

Version 2.2.0 adds a two-pass source check in `references/verification-log.md`. VAT remains configured at 18%, while personal-import thresholds are treated as live rules that must be checked on the estimate date.

## Important limits

The package estimates taxes from supplied or verified rates. It does not replace official tariff lookup, professional classification, or customs broker review. Verify live Israeli tariff rates, VAT, purchase tax, import approvals, and relief thresholds before filing or ordering high-value goods.
