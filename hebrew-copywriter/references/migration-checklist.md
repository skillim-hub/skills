# Migration checklist

Use this checklist when upgrading an older Hebrew content package to this enhanced neutral package.

## Identity

- [ ] Set slug to `hebrew-copywriter`.
- [ ] Remove organization/distributor references.
- [ ] Remove visual identity references and image links.
- [ ] Remove personal attribution fields from `metadata.json`.
- [ ] Keep neutral imperative voice.

## Required files

- [ ] `SKILL.md`
- [ ] `SKILL_HE.md`
- [ ] `metadata.json`
- [ ] `README.md`
- [ ] `CHANGELOG.md`
- [ ] `LICENSE`
- [ ] `pyproject.toml`
- [ ] `requirements-dev.txt`
- [ ] `references/api-reference.md`
- [ ] `references/workflow-guide.md`
- [ ] `references/troubleshooting.md`
- [ ] `references/test-scenarios.md`
- [ ] `references/migration-checklist.md`
- [ ] `scripts/hebrew-copywriter-client.py`
- [ ] `scripts/hebrew-copywriter-cli.py`
- [ ] `scripts/test_hebrew_copywriter_client.py`
- [ ] `scripts/examples/` with 5+ runnable examples.

## Documentation

- [ ] Expand from grammar into marketing workflows.
- [ ] Add full Hebrew guide with Israeli professional terminology.
- [ ] Include ₪, `כולל מע"מ`, `לא כולל מע"מ`, 24-hour time, and DD/MM/YYYY.
- [ ] Add channel playbooks for landing pages, WhatsApp, SMS, ads, מסחר מקוון, email, and social.
- [ ] Add Mermaid decision trees.
- [ ] Add anti-patterns, edge cases, troubleshooting, and production checklist.
- [ ] Add Israeli references for consumer protection, spam, privacy, accessibility, VAT, and public-data APIs.

## Code

- [ ] Add typed dataclasses.
- [ ] Support sync and async helper clients.
- [ ] Provide CLI commands for template, generation, prompt, and compliance checks.
- [ ] Add pytest suite with at least 20 tests.
- [ ] Add 5+ runnable examples.
- [ ] Avoid network calls in tests.

## Hebrew quality

- [ ] Replace literal translation advice with Hebrew-first principles.
- [ ] Add gender strategies: masculine, feminine, mixed, neutral.
- [ ] Add terms: `עוסק פטור`, `עוסק מורשה`, `חשבונית מס`, `קבלה`, `הוצאה מוכרת`, `דוח שנתי`, `מקדמות`.
- [ ] Add unsubscribe patterns for direct marketing.
- [ ] Add privacy microcopy for lead forms.
- [ ] Add safer language for health, finance, legal, real estate, education.

## Validation

```bash
python -m pytest scripts -q
python scripts/hebrew-copywriter-cli.py brief-template
python scripts/hebrew-copywriter-cli.py quick --business-name "דוגמה" --business-type "שירות" --offer "ייעוץ קצר" --audience "עצמאים" --channel whatsapp --include-unsubscribe
```
