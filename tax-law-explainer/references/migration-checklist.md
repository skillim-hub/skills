# Migration Checklist

Use this checklist when replacing an older or partial tax-law explainer package.

## Content neutrality

- [ ] Remove organization names, distribution callouts, and visual identity marks.
- [ ] Remove creator metadata.
- [ ] Use the required MIT authors notice in the license.
- [ ] Use neutral imperative language.
- [ ] Remove first-person claims and promotional wording.
- [ ] Keep educational and operational scope clear.

## Legal scope

- [ ] Cover Income Tax Ordinance, VAT Law, and Real Estate Taxation Law.
- [ ] Include National Insurance as an adjacent consideration for self-employed onboarding.
- [ ] Distinguish VAT status from income-tax liability.
- [ ] Distinguish state real-estate taxes from municipal betterment levy.
- [ ] Add current-data warnings for thresholds, brackets, forms, and deadlines.

## Hebrew localization

- [ ] Use natural Israeli terminology.
- [ ] Use ₪ formatting for examples.
- [ ] Use DD/MM/YYYY dates.
- [ ] Prefer Hebrew professional terms over transliteration.
- [ ] Check gendered verbs and avoid awkward literal translations.
- [ ] Use מע״מ, מס שבח, מס רכישה, ניכוי מס במקור, מקדמות, הצהרת הון.

## File structure

- [ ] `SKILL.md`
- [ ] `SKILL_HE.md`
- [ ] `references/api-reference.md`
- [ ] `references/workflow-guide.md`
- [ ] `references/troubleshooting.md`
- [ ] `references/test-scenarios.md`
- [ ] `references/migration-checklist.md`
- [ ] `scripts/tax_law_explainer_client.py`
- [ ] `scripts/tax-law-explainer-cli.py`
- [ ] `scripts/test_tax_law_explainer_client.py`
- [ ] `scripts/examples/` with at least five runnable scripts
- [ ] `metadata.json`
- [ ] `CHANGELOG.md`
- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `pyproject.toml`
- [ ] `requirements-dev.txt`

## Functional validation

- [ ] Run the pytest suite.
- [ ] Confirm at least 20 tests pass.
- [ ] Run at least one CLI command.
- [ ] Run all example scripts.
- [ ] Confirm metadata has no creator field.
- [ ] Search for forbidden organizational identity strings.
- [ ] Confirm the zip contains only the enhanced package files.

## Release checklist

- [ ] Bump semantic version.
- [ ] Update changelog.
- [ ] Rebuild zip from a clean directory.
- [ ] Print file tree and count.
- [ ] Preserve executable scripts where supported.
