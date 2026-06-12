# Hebrew Email Formatter

Professional Hebrew email composition and formatting for Israeli small businesses, freelancers, and consumers.

The package creates reviewable drafts with natural Israeli Hebrew, formality levels, gender-aware wording, neutral fallback phrasing, `₪` amounts, `DD/MM/YYYY` dates, and business signature blocks.

## Install

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start: importable package

```python
from hebrew_email_formatter import HebrewEmailFormatterClient

draft = HebrewEmailFormatterClient().compose({
    "purpose": "payment_reminder",
    "recipient": {"name": "דנה", "gender": "female"},
    "sender": {"name": "יואב לוי", "gender": "male"},
    "facts": {
        "invoice_number": "2026-041",
        "invoice_date": "01/05/2026",
        "due_date": "31/05/2026",
        "amount": "3500",
        "payment_terms": "שוטף + 30"
    }
})

print(draft.render())
```

## Quick start: create and reuse a draft identifier

```bash
CREATE_RESPONSE=$(hebrew-email-formatter create \
  --purpose payment_reminder \
  --recipient "דנה" \
  --recipient-gender female \
  --sender "יואב לוי" \
  --sender-gender male \
  --invoice-number 2026-041 \
  --invoice-date 01/05/2026 \
  --due-date 31/05/2026 \
  --amount 3500 \
  --payment-terms "שוטף + 30" \
  --env sandbox \
  --json)

DRAFT_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

hebrew-email-formatter show "$DRAFT_ID"
```

## CLI examples

```bash
hebrew-email-formatter amount 1234.5 --agorot
hebrew-email-formatter date 2026-06-03
python scripts/hebrew_email_formatter_client.py create --purpose follow_up --recipient "דנה" --sender "יואב" --topic "הצעת המחיר" --env sandbox
```

## Run tests

```bash
python -m pytest scripts/test_hebrew_email_formatter_client.py -q
python -m compileall scripts/ -q
```

## Example scripts

Each example reads environment variables, accepts `--env sandbox|production`, and prints JSON with `ensure_ascii=False`.

```bash
HEF_SENDER_NAME="יואב לוי" python scripts/examples/payment_reminder_example.py --env sandbox
HEF_SENDER_NAME="נועה ברק" python scripts/examples/quote_example.py --env production
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with examples, decision tree, edge cases, anti-patterns, and checklist |
| `SKILL_HE.md` | Hebrew skill guide with Israeli professional terminology |
| `hebrew_email_formatter/` | Installable Python package |
| `scripts/hebrew_email_formatter_client.py` | Structured helper script |
| `scripts/hebrew-email-formatter-cli.py` | Command wrapper |
| `scripts/test_hebrew_email_formatter_client.py` | Pytest suite |
| `scripts/examples/` | Runnable examples |
| `references/api-reference.md` | Schemas, validation codes, and Israeli context references |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | Validation scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Neutral packaging audit |
| `references/hebrew-qa-log.md` | Hebrew quality log |
| `references/verification-log.md` | Web validation log with two-pass source checks |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Change history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Packaging configuration |
| `requirements-dev.txt` | Development dependencies |

## Review boundary

Generated drafts are reviewable text. Verify legal, tax, accounting, privacy, and consumer-rights claims before sending. Minimize personal data in email content.
