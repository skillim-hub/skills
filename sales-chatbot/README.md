# Sales Chatbot

Hebrew sales chatbot helper for Israeli small businesses, freelancers, and consumer-facing teams. Use local price presentation in ₪, DD/MM/YYYY dates, installment wording, upsell and cross-sell logic, consent-aware marketing, service handoff, and pytest coverage.

## Install for local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a local recommendation, extract the returned quote identifier, and reuse it in the next step.

```bash
CREATE_RESPONSE=$(sales-chatbot create "כמה עולה CRM לעסק קטן ואפשר בתשלומים?" --env sandbox --json)
echo "$CREATE_RESPONSE"
QUOTE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["quote_id"])' <<< "$CREATE_RESPONSE")
sales-chatbot quote-status "$QUOTE_ID" --env sandbox
```

Run the same flow without installing console scripts:

```bash
python scripts/sales_chatbot_cli.py create "כמה עולה CRM לעסק קטן ואפשר בתשלומים?" --env sandbox --json
pytest scripts/test_sales_chatbot_client.py
python -m compileall scripts/ -q
```

## Python usage

```python
from sales_chatbot_client import SalesChatbotClient, sample_catalog

bot = SalesChatbotClient(sample_catalog())
response = bot.recommend(
    "כמה עולה CRM לעסק קטן?",
    {"name": "דנה", "has_marketing_consent": True, "preferred_installments": 3},
)
print(response.reply_he)
print(response.quote_id)
```

The package also exposes the same API from `sales_chatbot`:

```python
from sales_chatbot import SalesChatbotClient, sample_catalog
```

## Validated operational constants

The package was revalidated on 03/06/2026. The standard VAT rate remains configured as 18%, the current Tax Authority invoice-allocation threshold is treated as above ₪5,000 before VAT as of 01/06/2026, and the Bank of Israel exchange-rate example uses the official SDMX API host. Keep these values configurable and review `references/verification-log.md` before production deployment.

## Environment variables

| Variable | Purpose |
|---|---|
| `SALES_CHATBOT_ENV` | Default environment for examples: `sandbox` or `production` |
| `SALES_CHATBOT_API_KEY` | Optional placeholder for external gateway or CRM secrets; never printed |
| `SALES_CHATBOT_CATALOG` | Optional path to catalog JSON |
| `SALES_CHATBOT_CONTEXT` | Optional path to customer context JSON |
| `SALES_CHATBOT_CHANNEL` | Channel label, such as `whatsapp`, `web`, or `phone` |

## Catalog shape

```json
{
  "products": [
    {
      "sku": "BASIC-CRM",
      "name_he": "חבילת CRM בסיסית",
      "category": "תוכנה לעסקים קטנים",
      "price_ils": "249",
      "tags": ["crm", "לקוחות", "עסק", "ניהול", "לידים"],
      "cross_sell": ["SETUP-1H"],
      "upsell_to": "PRO-CRM",
      "stock": 999,
      "max_installments": 3,
      "warranty_months": 12
    }
  ]
}
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Israeli integration and regulatory reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Diagnostics and fixes |
| `references/test-scenarios.md` | Concrete test scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Neutrality and attribution audit report |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `references/verification-log.md` | Web validation log for regulatory and API references |
| `scripts/sales_chatbot_client.py` | Typed sync and async client |
| `scripts/sales_chatbot_cli.py` | Typer CLI |
| `scripts/sales-chatbot-cli.py` | Compatibility launcher |
| `scripts/test_sales_chatbot_client.py` | pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Installable package configuration |
| `requirements-dev.txt` | Development dependencies |

## Safety notes

- Do not collect card numbers in chat.
- Do not send promotional outreach without consent.
- Show total price whenever installments are shown.
- Route complaints, legal disputes, chargebacks, payment failures, and cancellation uncertainty to a human.
- Confirm current legal, tax, VAT, accounting, and provider rules before production deployment.

## Web validation

Review `references/verification-log.md` before production use. The 03/06/2026 pass double-confirmed VAT, total-price display, consent handling, privacy, accessibility, Tax Authority endpoints, Bank of Israel exchange-rate API patterns, and WhatsApp Cloud API terminology. The invoice-allocation threshold was corrected to the current `₪5,000` before VAT threshold effective `01/06/2026`; fetch `MinimumAmount` before issuing invoices.

