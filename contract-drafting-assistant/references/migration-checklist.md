# Migration checklist

Use this checklist when upgrading from a narrow employment-contract package or a generic contract template into this enhanced Israeli contract drafting skill.

## Scope migration

- Rename the skill directory to `contract-drafting-assistant`.
- Replace employment-only positioning with general Israeli contract drafting.
- Keep employment-classification warnings but do not present the skill as an employment-contract generator.
- Add service, freelance, consumer, sale, supply, NDA, website terms, IP, and privacy workflows.
- Add Hebrew and English parity.
- Add references for contracts, remedies, standard terms, consumer law, VAT, privacy, copyright, sale, arbitration, and electronic signatures.

## Metadata migration

- Set `name` to `contract-drafting-assistant`.
- Bump version to a new major version when scope changes.
- Remove any metadata field identifying a person, organization, publisher, or distribution source.
- Expand tags in Hebrew and English.
- Remove compatibility or promotional language that names external products.
- Keep license value as MIT.

## File migration

Required files:

- `SKILL.md`
- `SKILL_HE.md`
- `metadata.json`
- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `pyproject.toml`
- `requirements-dev.txt`
- `references/api-reference.md`
- `references/workflow-guide.md`
- `references/troubleshooting.md`
- `references/test-scenarios.md`
- `references/migration-checklist.md`
- `scripts/contract_drafting_assistant_client.py`
- `scripts/contract_drafting_assistant_cli.py`
- `scripts/test_contract_drafting_assistant_client.py`
- `scripts/examples/*.py`

Optional convenience files may be added if they do not introduce branding or visual identity asset references.

## Content migration

- Replace "employment agreement" examples with mixed contract examples.
- Remove visual identity assets, decorative markers, decorative headers, images, and promotional references.
- Use imperative voice.
- Add decision trees using Mermaid syntax.
- Add concrete examples and edge cases.
- Add anti-patterns and replacement language.
- Add production checklist.
- Add risk taxonomy.
- Add Hebrew localization and accounting language.
- Add a non-legal-advice and professional-review limitation.

## Script migration

- Replace one-off generator scripts with a typed helper module.
- Add synchronous and asynchronous APIs.
- Add dataclasses or typed models for parties, terms, results, and risk findings.
- Add validation for Israeli IDs.
- Add VAT calculation helper.
- Add risk scanner.
- Add renderer for Hebrew and English agreements.
- Add CLI commands for generation, risk checks, VAT calculation, scenarios, and ID validation.
- Add runnable examples for at least five scenarios.
- Add pytest tests covering at least 20 behaviors.

## Quality gate

```bash
python -m pytest scripts -q
python scripts/contract_drafting_assistant_cli.py --help
python scripts/contract_drafting_assistant_cli.py scenario freelance-design --language he
python scripts/contract_drafting_assistant_cli.py vat 1000 --rate 0.18
```

Search the package for forbidden items:

```bash
grep -R "legacy-branding-token\|visual identity asset\|decorative marker\|decorative header" .
```

Expected result: no forbidden branding or metadata identifiers.

## Backward-compatibility notes

- Existing employment-only prompts should route to worker-classification warnings or dedicated employment review.
- Existing `generate_contract.py` command should be replaced by the CLI `scenario` and `new` commands.
- Existing tests that expect employment benefits should be removed or moved to an employment-specific package.
- Contract outputs should use bracketed placeholders instead of inventing missing facts.
- Hebrew examples should use DD/MM/YYYY and ₪.


## v3 live-source migration

- Replace any permanent VAT-number clause with "מע״מ כדין" or "VAT at the lawful rate" unless the document is a calculation exhibit.
- Add a 2026 interpretation check for Israeli business contracts.
- Keep the Bank of Israel API endpoint behind a fallback clause because exchange rates are representative indicators, not automatically mandatory.
- Keep companies-lookup resource identifiers configurable rather than hardcoded.
- Store the verification date in risk notes or review metadata.
