# Free-Text Invoice Explanation

Generate plain-language Hebrew or English explanations for invoice line items used by Israeli small businesses, freelancers, and consumers. Use it to clarify what a client is paying for, why VAT appears or does not appear, and what supporting details should be shown next to a charge.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a JSON input file:

```bash
cat > invoice.json <<'JSON'
{
  "context": {
    "language": "he",
    "business_type": "authorized_dealer",
    "document_type": "tax_invoice",
    "document_date": "07/03/2026"
  },
  "lines": [
    {
      "description": "ייעוץ עסקי לפגישה חודשית",
      "quantity": "1",
      "unit_price": "750",
      "vat_rate": "18"
    }
  ]
}
JSON
```

Generate explanations:

```bash
invoice-explain explain --input invoice.json --env sandbox > response.json
```

Extract the first explanation identifier from the create response and reuse it in the next step. This package is local and does not create server-side records, so the stable identifier is derived from the first line title:

```bash
EXPLANATION_ID="$(python - <<'PY'
import json
data = json.load(open("response.json", encoding="utf-8"))
print(data["explanations"][0]["title"])
PY
)"
python - <<'PY'
import json, os
data = json.load(open("response.json", encoding="utf-8"))
selected = [item for item in data["explanations"] if item["title"] == os.environ["EXPLANATION_ID"]][0]
print(selected["plain_text"])
PY
```

Use the Python module:

```python
from free_text_invoice_explanation import InvoiceExplanationClient

client = InvoiceExplanationClient()
result = client.explain_invoice(
    lines=[{"description": "תחזוקת אתר חודשית", "quantity": "1", "unit_price": "400", "vat_rate": "18"}],
    context={"language": "he", "business_type": "authorized_dealer", "document_type": "tax_invoice"},
)
print(result["summary"])
```

## Environment variables

| Name | Purpose |
| --- | --- |
| `FTIE_ENV` | Default CLI environment: `sandbox` or `production`. |
| `FTIE_DEFAULT_LANGUAGE` | Default example language: `he` or `en`. |
| `FTIE_BUSINESS_NAME` | Optional business name inserted into example contexts. |

## File index

| Path | Purpose |
| --- | --- |
| `SKILL.md` | English skill guide with examples, decision trees, edge cases, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew skill guide with Israeli terminology and localized examples. |
| `references/api-reference.md` | Non-API schema reference and Israeli regulatory reference points. |
| `references/workflow-guide.md` | End-to-end workflows for common invoice explanation tasks. |
| `references/troubleshooting.md` | Operational troubleshooting reference. |
| `references/test-scenarios.md` | More than twenty concrete validation scenarios. |
| `references/migration-checklist.md` | Upgrade checklist for earlier packages and manual templates. |
| `references/branding-audit.md` | Branding, attribution, visual-asset, and public Markdown audit report. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization quality log. |
| `references/verification-log.md` | Web-validated source log with two-pass checks and correction status. |
| `free_text_invoice_explanation/` | Installable Python package. |
| `scripts/free_text_invoice_explanation_client.py` | Importable compatibility entry for client helpers. |
| `scripts/free-text-invoice-explanation-cli.py` | CLI launcher script. |
| `scripts/examples/` | Runnable scenario scripts. |
| `scripts/test_free_text_invoice_explanation_client.py` | Pytest suite. |

## Development checks

```bash
pytest -q
python -m compileall scripts/ -q
```

## Production use checklist

Confirm the current VAT rate, business classification, document type, allocation-number threshold, and legal wording with a qualified professional before sending documents to customers. Treat generated text as an explanation aid, not as tax, accounting, or legal advice.
