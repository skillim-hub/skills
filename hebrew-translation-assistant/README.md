# Hebrew Translation Assistant

Neutral package for Hebrew-English translation assistance and adaptation in Israeli business, freelance, and consumer contexts.

Use the package to prepare and review customer support replies, invoices, receipts, payment reminders, e-commerce copy, privacy notices, warranty text, casual WhatsApp wording, and Israeli idioms while preserving register, terminology, numbers, URLs, email addresses, `₪`, and `DD/MM/YYYY` dates.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with a stored request id

Create a translation request, extract the id, then use the id in the next command.

```bash
export HEBREW_TRANSLATION_ASSISTANT_HOME="$(pwd)/.hta-data"

CREATE_RESPONSE="$(hebrew-translation-assistant create "Please issue a tax invoice/receipt for ₪1,250 by 2026-03-05." --register accounting --env sandbox)"
REQUEST_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
hebrew-translation-assistant show "$REQUEST_ID"
```

Run a direct translation without storage:

```bash
hebrew-translation-assistant translate "Refund within 7 business days" --direction en-to-he --register support --json
```

Print source-sensitive Israeli reference facts verified for this release:

```bash
hebrew-translation-assistant facts
```

Use the importable Python module:

```python
from hebrew_translation_assistant import HebrewTranslationAssistant

client = HebrewTranslationAssistant()
result = client.translate_text(
    "Please send the receipt and bank transfer confirmation.",
    direction="en-to-he",
    register="business",
)
print(result.to_json())
```

## Run tests

```bash
pytest
python -m compileall scripts/ -q
```

## Run examples

Each example reads `HEBREW_TRANSLATION_ASSISTANT_ENV` and `HEBREW_TRANSLATION_ASSISTANT_HOME`. Each example also accepts `--env sandbox|production` and prints JSON with `json.dumps(..., ensure_ascii=False, indent=2)`.

```bash
python scripts/examples/translate_invoice_email.py --env sandbox
python scripts/examples/translate_support_reply.py --env production
python scripts/examples/localize_checkout_copy.py --env sandbox
python scripts/examples/review_contract_clause.py --env sandbox
python scripts/examples/bulk_review_terms.py --env sandbox
python scripts/examples/export_glossary.py --env sandbox
python scripts/examples/show_reference_facts.py --env sandbox
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, edge cases, anti-patterns, production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, `₪`, and `DD/MM/YYYY` localization |
| `references/api-reference.md` | Validated official-source map, helper API reference, request and response examples, error tables |
| `references/verification-log.md` | Web validation log with two-pass source checks |
| `references/workflow-guide.md` | End-to-end translation workflows |
| `references/troubleshooting.md` | Detailed diagnosis and fixes |
| `references/test-scenarios.md` | More than 20 scenario prompts and expected handling |
| `references/migration-checklist.md` | Migration checklist from generic translation or older localization material |
| `references/branding-audit.md` | Branding, ownership, visual mark, badge, and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log |
| `hebrew_translation_assistant/` | Installable Python module |
| `scripts/hebrew_translation_assistant_client.py` | Compatibility import entry |
| `scripts/hebrew_translation_assistant_cli.py` | Compatibility CLI entry |
| `scripts/test_hebrew_translation_assistant_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |

## Scope

The helper scripts provide terminology, register, idiom, storage, source-sensitive reference facts, and formatting assistance. They do not replace a professional translation engine, lawyer, tax adviser, accountant, bookkeeper, privacy specialist, accessibility specialist, consumer-protection specialist, certified translator, or official regulatory source. For legal, tax, accounting, privacy, accessibility, certified, or public-facing publication, verify the final text against current official sources.
