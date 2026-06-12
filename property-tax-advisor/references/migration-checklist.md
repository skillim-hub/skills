# Migration checklist

Use this checklist when replacing an older Arnona-only package with the enhanced `property-tax-advisor` package.

## Metadata

- Rename skill to `property-tax-advisor`.
- Remove creator metadata.
- Remove organization names, visual identity references, and distribution callouts.
- Set license to MIT.
- Use version `2.0.0` or later.
- Add bilingual tags for Arnona, Mas Rechush, purchase tax, betterment levy, municipal tax, freelancers, small businesses, and consumers.

## Content scope

- Keep Arnona calculation guidance.
- Add Mas Rechush explanation and direct-damage claim workflow.
- Add purchase-tax triage.
- Add Mas Shevach routing for sale scenarios.
- Add betterment-levy triage.
- Add small-business and freelancer mixed-use examples.
- Add consumer examples and discount workflows.
- Add edge cases and anti-patterns.

## File structure

Expected files:

```text
SKILL.md
SKILL_HE.md
README.md
CHANGELOG.md
LICENSE
metadata.json
pyproject.toml
requirements-dev.txt
references/api-reference.md
references/workflow-guide.md
references/troubleshooting.md
references/test-scenarios.md
references/migration-checklist.md
property_tax_advisor/client.py
scripts/property-tax-advisor-cli.py
scripts/test_property_tax_advisor_client.py
scripts/examples/*.py
```

## Script migration

- Replace single-purpose calculators with `property_tax_advisor_client.py`.
- Keep calculations deterministic and typed.
- Return structured dataclasses or dictionaries.
- Include warnings whenever sample data is used.
- Provide async equivalents for calculation functions.
- Add a `click` CLI with JSON output.
- Keep tests independent from internet access.

## Hebrew migration

- Use natural professional Hebrew.
- Prefer accepted Hebrew terms: ארנונה, השגה, ערר, מחזיק, צו ארנונה, מס רכישה, מס שבח, היטל השבחה, מס רכוש וקרן פיצויים.
- Use `₪` for amounts.
- Use `DD/MM/YYYY` date examples.
- Avoid unnecessary transliteration when Hebrew terminology exists.
- Avoid gendered language where a neutral professional phrasing is available.

## Neutral voice checks

- Replace possessive tool wording with “the helper” or “the script”.
- Replace collective calculation wording with “calculate”.
- Replace personal recommendation wording with “consider” or “use”.
- Remove branding phrases.
- Remove visual identity references.
- Use imperative operational guidance.

## Validation

Run:

```bash
python -m pytest scripts/test_property_tax_advisor_client.py
python scripts/property-tax-advisor-cli.py rates --municipalities
python scripts/property-tax-advisor-cli.py arnona --municipality tel-aviv --area 80 --zone A --usage residential
python scripts/property-tax-advisor-cli.py purchase-tax --price 2400000 --buyer-profile additional_home --contract-date 15/03/2026
```

## Release checklist

- Confirm all tests pass.
- Search for forbidden branding strings.
- Verify metadata has no creator key.
- Confirm LICENSE uses the required MIT copyright line.
- Confirm README file index matches actual files.
- Confirm zip contains one top-level folder named `property-tax-advisor`.
