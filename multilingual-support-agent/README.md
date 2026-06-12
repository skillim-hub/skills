# Multilingual Support Agent

A neutral support skill for Israeli small businesses, freelancers, and consumer-facing teams that handle high-coverage customer messages in Hebrew, English, Russian, and Arabic.

The package contains guidance, workflows, a typed Python client, a Typer command-line interface, runnable examples, and a pytest suite.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a local support case and extract the generated case identifier:

```bash
CREATE_RESPONSE=$(multilingual-support-agent create "המשלוח שלי מאחר" --env sandbox --order-id IL-1001)
CASE_ID=$(printf "%s" "$CREATE_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])')
multilingual-support-agent add-message "$CASE_ID" "תודה, מספר הטלפון שלי 050-0000000" --env sandbox --order-id IL-1001
```

Use the Python client:

```python
from multilingual_support_agent import SupportAgentClient, SupportContext

client = SupportAgentClient(environment="sandbox")
created = client.create_case(
    "I was charged twice for order IL-1001",
    SupportContext(order_id="IL-1001", last4="1234"),
)
case_id = created["case_id"]
follow_up = client.add_message(case_id, "Please update me by email")
print(follow_up["analysis"]["reply"])
```

Use the helper script:

```bash
python scripts/multilingual_support_agent_client.py "Я не получил чек" --env sandbox --order-id IL-1001 --email customer@example.com
```

Run examples:

```bash
python scripts/examples/example_01_late_delivery.py --env sandbox
python scripts/examples/example_04_refund_arabic.py --env production --order-id IL-2002
```

## Environment variables

| Variable | Purpose |
|---|---|
| `MSA_ENV` | Default environment: `sandbox` or `production`. |
| `MSA_BUSINESS_NAME` | Optional business name used in context. |
| `MSA_ORDER_ID` | Optional order identifier for examples and helper script. |
| `MSA_EMAIL` | Optional customer email. |
| `MSA_PHONE` | Optional customer phone. |
| `MSA_LAST4` | Optional last four digits of the payment method. |
| `MSA_API_KEY` | Accepted by examples for integration parity; never printed. |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology, ₪ formatting, and DD/MM/YYYY dates. |
| `references/api-reference.md` | Israeli regulation and API reference, data contracts, examples, and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for delivery, refunds, invoices, privacy, and complaints. |
| `references/troubleshooting.md` | Operational debugging guide. |
| `references/test-scenarios.md` | More than 20 concrete scenarios. |
| `references/migration-checklist.md` | Migration steps from templates or ad-hoc support. |
| `references/branding-audit.md` | Audit record for neutral packaging checks. |
| `references/hebrew-qa-log.md` | Hebrew localization review log. |
| `references/verification-log.md` | Web validation log with two-pass source checks. |
| `multilingual_support_agent/client.py` | Typed sync and async Python client. |
| `multilingual_support_agent/cli.py` | Typer CLI implementation. |
| `scripts/multilingual_support_agent_client.py` | Structured helper for local scenario execution. |
| `scripts/multilingual_support_agent_cli.py` | CLI entry wrapper. |
| `scripts/test_multilingual_support_agent_client.py` | Pytest suite. |
| `scripts/examples/` | Five runnable scenario scripts. |

## Test

```bash
python -m pytest
python -m compileall scripts/ -q
```

## Production notes

Use the verification log as a dated reference snapshot, then verify current Israeli legal, tax, privacy, accessibility, and consumer-protection requirements before production use. Treat the skill as operational triage, not legal, tax, accounting, medical, safety, or financial advice.
