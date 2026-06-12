# RTL UI Design Advisor

A practical package for implementing and auditing right-to-left interfaces for Hebrew and Arabic users in Israel. Use it for websites, booking forms, checkout flows, invoices, receipts, client dashboards, service portals, and consumer-facing pages.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create an audit, extract the audit id from the JSON response, then use the id in the next command.

```bash
AUDIT_ID="$(
  rtl-ui-design-advisor create-audit \
    --kind tailwind \
    --text "flex ml-4 text-left left-0 space-x-2" \
    --format json \
  | python -c "import json,sys; print(json.load(sys.stdin)['id'])"
)"

rtl-ui-design-advisor show-audit "$AUDIT_ID" --format markdown
```

Run direct checks when a stored audit is not needed.

```bash
rtl-ui-design-advisor audit-html --file path/to/page.html --format json
rtl-ui-design-advisor audit-css --file path/to/styles.css --format markdown
rtl-ui-design-advisor audit-tailwind --text "p-4 ps-4 border-s-4 text-start"
```

Use the module from Python after installation.

```python
from rtl_ui_design_advisor import RtlAuditClient

client = RtlAuditClient()
record = client.create_audit("tailwind", "flex ml-4 text-left", env="sandbox")
print(record.id)
print(client.get_audit(record.id).result.to_markdown())
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English implementation guide with examples, decision trees, edge cases, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli professional terminology, ₪ formatting, and DD/MM/YYYY examples |
| `references/api-reference.md` | Browser, framework, localization, and Israeli regulatory reference |
| `references/workflow-guide.md` | End-to-end implementation and rollout workflows |
| `references/troubleshooting.md` | Symptom-based debugging guide |
| `references/test-scenarios.md` | Concrete QA scenarios for Hebrew and Arabic UI |
| `references/migration-checklist.md` | Checklist for converting LTR products to RTL |
| `references/branding-audit.md` | Neutrality, attribution, logo, and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log |
| `references/verification-log.md` | Two-pass web validation log with official-source snippets and correction status |
| `src/rtl_ui_design_advisor/` | Installable Python module |
| `scripts/rtl_ui_design_advisor_client.py` | Underscored standalone helper implementation |
| `scripts/rtl_ui_design_advisor_cli.py` | CLI entry script |
| `scripts/examples/` | Runnable scenario scripts |
| `scripts/test_rtl-ui-design-advisor_client.py` | Pytest suite |

## Development checks

```bash
python -m pytest
python -m compileall scripts/ -q
```

## Scope

Use this package for interface implementation, automated static checks, and QA preparation. Treat accessibility, privacy, consumer protection, tax, and accounting items as engineering checkpoints. Confirm binding legal, tax, accessibility, and regulatory obligations with current official publications and qualified professionals before release sign-off.
