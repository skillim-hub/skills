# Customer-Service Chat Agent

Hebrew-first customer-service chat agent skill for Israeli small businesses, freelancers, and consumer-facing teams. The package provides operational guidance, Israeli localization, handoff rules, troubleshooting, test scenarios, an importable Python package, a Typer CLI, runnable examples, and a pytest suite.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Classify and reply:

```bash
python scripts/customer_service_chat_agent_cli.py classify "איפה ההזמנה שלי?"
python scripts/customer_service_chat_agent_cli.py reply "קיבלתי מוצר פגום, רוצה החזר"
```

Create a handoff ticket, extract the identifier, then use it in the next step:

```bash
CREATE_RESPONSE=$(python scripts/customer_service_chat_agent_cli.py create-handoff "חייבתם אותי פעמיים" --name "דנה לוי" --contact "+972501234567" --env sandbox)
TICKET_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["ticket_id"])' <<< "$CREATE_RESPONSE")
python scripts/customer_service_chat_agent_cli.py ticket-status "$TICKET_ID" --env sandbox
```

Import from Python:

```python
from customer_service_chat_agent import CustomerServiceChatAgent

agent = CustomerServiceChatAgent()
response = agent.reply("כמה עולה ייעוץ?")
print(response.message)
```

## Run tests

```bash
python -m compileall scripts/ -q
pytest
```

## Run examples

Each example reads environment variables and accepts `--env sandbox|production`.

```bash
CUSTOMER_NAME="דנה לוי" CUSTOMER_CONTACT="+972501234567" python scripts/examples/01_faq_hours.py --env sandbox
ORDER_NUMBER="10493" python scripts/examples/02_order_status.py --env sandbox
ORDER_NUMBER="10493" python scripts/examples/03_refund_handoff.py --env sandbox
python scripts/examples/04_invoice_request.py --env sandbox
CUSTOMER_CONTACT="dana@example.co.il" python scripts/examples/05_privacy_request.py --env sandbox
python scripts/examples/06_accessibility_issue.py --env sandbox
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Israeli API and regulatory reference |
| `references/workflow-guide.md` | End-to-end implementation workflows |
| `references/troubleshooting.md` | Diagnostics and remediation guide |
| `references/test-scenarios.md` | Manual and automated QA scenarios |
| `references/migration-checklist.md` | Migration checklist for existing support flows |
| `references/branding-audit.md` | Branding, logo, author, and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew QA correction log |
| `references/verification-log.md` | Two-pass web validation log |
| `customer_service_chat_agent/` | Installable Python package |
| `scripts/customer_service_chat_agent_client.py` | Compatibility import script |
| `scripts/customer_service_chat_agent_cli.py` | CLI script |
| `scripts/test_customer_service_chat_agent_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario examples |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Python packaging and test config |
| `requirements-dev.txt` | Development dependencies |

## Design goals

- Answer Hebrew FAQs from approved knowledge.
- Handle Israeli customer-service concepts such as חשבונית מס/קבלה, מע״מ, ח.פ., עוסק מורשה, משלוח, איסוף עצמי, זיכוי, and החזר כספי.
- Use ₪ and DD/MM/YYYY.
- Ask one clarifying question at a time.
- Escalate edge cases to human representatives.
- Avoid legal, tax, medical, or binding financial decisions.
- Collect only necessary customer data.

## Production notes

Verify current Israeli legal, tax, privacy, accessibility, and payment requirements with official sources and professional advisers before production. Keep the business knowledge base versioned and reviewed.
