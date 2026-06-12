# Multi-Line Item Aggregator

Neutral local tooling for checking multi-line Israeli invoice calculations. It calculates line discounts, invoice-level discounts, VAT per line, rounded totals, and fractional agorot residuals.

## Install

From the extracted package directory:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Run checks:

```bash
python -m pytest
python -m compileall scripts/ -q
```

## Quick start

Create a sample invoice and capture the response:

```bash
CREATE_RESPONSE=$(python -m multi_line_item_aggregator.cli create-sample --env sandbox sample-invoice.json)
```

Extract the draft identifier from the create response:

```bash
INVOICE_ID=$(python -c 'import json, sys; print(json.loads(sys.argv[1])["id"])' "$CREATE_RESPONSE")
```

Use the extracted identifier in the next step:

```bash
python -m multi_line_item_aggregator.cli aggregate sample-invoice.json \
  --env sandbox \
  --id "$INVOICE_ID" \
  --invoice-date 15/06/2026 \
  --vat-number 515555555
```

Print JSON output:

```bash
python -m multi_line_item_aggregator.cli aggregate sample-invoice.json --env sandbox --id "$INVOICE_ID" --json-output
```

## Python usage

```python
from multi_line_item_aggregator import aggregate_invoice

result = aggregate_invoice([
    {"sku": "A", "description": "Service", "quantity": "1", "unit_price": "100", "vat_rate": "18%"}
])
print(result.totals.grand_total)
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with examples, edge cases, decision tree, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew guide localized for Israeli professional terminology. |
| `multi_line_item_aggregator/` | Installable Python package. |
| `references/api-reference.md` | Israeli regulatory/API reference and non-API mapping. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Diagnosis tables and correction steps. |
| `references/test-scenarios.md` | Concrete regression scenarios. |
| `references/migration-checklist.md` | Migration plan from spreadsheets and legacy flows. |
| `references/branding-audit.md` | Branding, attribution, logo, badge, and emoji audit report. |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance change log. |
| `scripts/multi_line_item_aggregator_client.py` | Compatibility CLI script using package imports. |
| `scripts/multi-line-item-aggregator-cli.py` | Thin wrapper for the package CLI. |
| `scripts/test_multi_line_item_aggregator_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable scenario scripts. |
| `metadata.json` | Package metadata. |
| `CHANGELOG.md` | Keep a Changelog history. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Installable Python project configuration. |
| `requirements-dev.txt` | Development and test dependencies. |

## Assumptions

- Amounts are before VAT unless converted before input.
- Currency is ILS by default.
- VAT rate is supplied per line.
- Money values use Decimal-safe strings.
- JSON output uses strings for money to preserve precision.

## Production note

Use approved accounting software for official issuance, legal retention, and required tax reporting. Keep current VAT rates and reporting requirements under operational review.


## Web validation

The package includes `references/verification-log.md`, created on 2026-06-02. It double-checks current Israeli VAT rate, Israel Invoice thresholds, official endpoint references, terminology, and confirms that official webhook event names were not found.
