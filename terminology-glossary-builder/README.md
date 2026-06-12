# Terminology Glossary Builder

Build bilingual English-Hebrew glossaries of professional terms for Israeli small businesses, freelancers, and consumers. Each entry includes a plain-language definition, Hebrew-English pairing, usage notes, warnings, and citations to Israeli public authorities or regulators.

## Install

```bash
unzip terminology-glossary-builder-enhanced-v3.zip
cd terminology-glossary-builder
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with saved glossary id

```bash
CREATE_RESPONSE=$(tgb create "VAT" "Receipt" "Withholding tax" --industry tax --env sandbox --store ./glossaries.json)
GLOSSARY_ID=$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["id"])' <<< "$CREATE_RESPONSE")
tgb export "$GLOSSARY_ID" --store ./glossaries.json --format markdown > glossary.md
```

The first command prints a JSON response that includes `id`, `path`, `entry_count`, and `warnings`. Extract the `id` and pass it to `tgb export`.

## Python quick start

```python
from terminology_glossary_builder import GlossaryBuilder

builder = GlossaryBuilder()
result = builder.build_glossary(
    ["VAT", "חשבונית מס", "ביטול עסקה"],
    industry="retail",
    audience="small_business",
    environment="sandbox",
)
print(builder.to_markdown(result))
```

## Command-line examples

```bash
tgb build "Privacy policy" "Database registration or notice" --industry privacy --format json
tgb build "עוסק פטור" "ניכוי מס במקור" --industry freelance --hebrew --format markdown
tgb sources --json
tgb validate
```

Use `--env sandbox` for drafts, internal training, examples, and test data. Use `--env production` only after validating citations, dates, ₪ amounts, and legal/accounting review needs.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision tree, production checklist, edge cases, and anti-patterns. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli professional phrasing and local formatting rules. |
| `references/api-reference.md` | Israeli source registry, relevant public interfaces, request/response examples, and error handling. |
| `references/workflow-guide.md` | End-to-end workflows for tax, retail, privacy, import, and consumer glossaries. |
| `references/troubleshooting.md` | Diagnosis and correction guide for source, translation, formatting, and packaging issues. |
| `references/test-scenarios.md` | More than 20 concrete test scenarios. |
| `references/migration-checklist.md` | Upgrade checklist from earlier package layouts. |
| `references/branding-audit.md` | Branding and attribution audit report. |
| `references/hebrew-qa-log.md` | Hebrew quality review log. |
| `references/verification-log.md` | Web validation log with pass 1 and pass 2 sources. |
| `terminology_glossary_builder/client.py` | Importable typed client and structured offline helper. |
| `terminology_glossary_builder/cli.py` | Typer command-line interface. |
| `scripts/examples/` | Runnable scenario scripts. |
| `scripts/test_terminology_glossary_builder_client.py` | Pytest suite. |

## Source policy

Prefer Israeli official or statutory sources for operational terms. Use the Tax Authority for tax terms, the Consumer Protection and Fair Trade Authority for consumer terms, the Privacy Protection Authority for privacy terms including database registration or notice duties, the Corporations Authority for company terms, Bank of Israel for banking terms, and the Standards Institution of Israel for standards terms.

When a term is not supported by the local term library, mark it for professional review rather than inventing a translation.

## Development commands

```bash
pytest
python -m compileall scripts/ -q
python -m compileall terminology_glossary_builder/ -q
```
