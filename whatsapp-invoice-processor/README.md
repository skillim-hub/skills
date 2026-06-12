# WhatsApp Invoice Processor

Process invoice photos received through WhatsApp by applying OCR upstream, parsing the resulting text, extracting Israeli invoice fields, and returning a concise receipt confirmation in chat.

## Install

```bash
cd whatsapp-invoice-processor
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create `sample.txt`:

```bash
cat > sample.txt <<'EOF'
א.ב. שירותים בע"מ
ח.פ. 516123456
חשבונית מס/קבלה מס' 8841
תאריך 14/02/2026
סה"כ לפני מע"מ 99.00 ₪
מע"מ 18% 18.00 ₪
סה"כ לתשלום 117.00 ₪
מספר הקצאה 987654321
EOF
```

Create a parse response:

```bash
whatsapp-invoice-processor parse sample.txt --env sandbox --json > create-response.json
```

Extract the document identifier from the create response, then use the same OCR text in the next step:

```bash
DOCUMENT_ID=$(python - <<'PY'
import json
with open('create-response.json', encoding='utf-8') as f:
    print(json.load(f)['dedupe_key'])
PY
)
WHATSAPP_INVOICE_OCR_TEXT="$(cat sample.txt)" whatsapp-invoice-processor parse-env --env sandbox --known-duplicate-key "$DOCUMENT_ID" > follow-up-response.json
python - <<'PY'
import json
with open('create-response.json', encoding='utf-8') as f:
    first = json.load(f)
with open('follow-up-response.json', encoding='utf-8') as f:
    second = json.load(f)
print(first['dedupe_key'])
print(second['status'])
PY
```

Use the client from Python:

```python
from whatsapp_invoice_processor import InvoiceProcessor, ProcessingConfig

processor = InvoiceProcessor(ProcessingConfig.from_env(env="sandbox"))
result = processor.parse_file("sample.txt")
print(result.chat_reply_he)
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with examples, edge cases, mermaid decision tree, anti-patterns, troubleshooting, and production checklist. |
| `SKILL_HE.md` | Hebrew guide with natural Israeli terminology, ₪ formatting, and DD/MM/YYYY localization. |
| `references/api-reference.md` | WhatsApp, Israeli VAT, allocation-number, privacy, request and response examples, and error tables. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Operational failures, fixes, logging, and recovery. |
| `references/test-scenarios.md` | 30 concrete scenarios. |
| `references/migration-checklist.md` | Migration from manual or prior automation. |
| `references/branding-audit.md` | Branding and attribution audit report. |
| `references/hebrew-qa-log.md` | Hebrew quality review log. |
| `references/verification-log.md` | Two-pass web validation of official sources, snippets, and corrections. |
| `whatsapp_invoice_processor/client.py` | Typed sync and async helper. |
| `whatsapp_invoice_processor/cli.py` | Installable command-line interface. |
| `scripts/whatsapp_invoice_processor_client.py` | Underscored compatibility import. |
| `scripts/whatsapp-invoice-processor-cli.py` | Source checkout command wrapper. |
| `scripts/test_whatsapp_invoice_processor_client.py` | Pytest suite with more than 20 tests. |
| `scripts/examples/` | Runnable scenario scripts. |
| `metadata.json` | Skill metadata. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Project and test configuration. |
| `requirements-dev.txt` | Development dependencies. |

## Test

```bash
pytest
python -m compileall scripts/ -q
```

## Production notes

Connect OCR before the helper or replace the extraction layer with a service that returns the same structured contract. Verify current official Israeli tax, privacy, and WhatsApp requirements before production deployment. As of 03/06/2026, the Invoice Israel allocation threshold is ₪5,000 before VAT for qualifying tax invoices; keep this policy configurable.
