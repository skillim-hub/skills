# Migration Checklist

Use this checklist when replacing a stub or earlier version of this skill.

## Content migration

- Remove all branding, visual identitys, visual markers, large headers, attribution names, and distribution callouts.
- Keep neutral imperative wording.
- Replace generic descriptions with concrete Israeli Mas Shevach workflows.
- Add English and Hebrew guides with equivalent depth.
- Localize Hebrew examples with ₪ and `DD-MM-YYYY`.
- Add decision trees, examples, anti-patterns, troubleshooting, and production checklist.

## Metadata migration

- Bump `version`.
- Remove `author`.
- Keep license as `MIT`.
- Expand tags.
- Confirm descriptions are neutral and practical.
- Confirm supported agents match actual usage.

## Code migration

- Add typed calculation helper through an underscored installable module.
- Add synchronous and asynchronous calculation entry points.
- Add CLI.
- Add JSON output for automation and case-based CLI chaining.
- Add pretty output for humans.
- Add examples.
- Add pytest coverage with at least 20 tests.
- Validate all inputs.
- Ensure tests run without network access.

## Legal/tax migration

- Do not hard-code unverified future tax rates as legal facts.
- Make tax rate configurable.
- Mark CPI and regulation data as requiring official verification.
- Never silently apply exemptions.
- Keep audit trail fields: warnings, assumptions, inputs, formulas.
- Escalate complex cases.

## Packaging migration

- Add `README.md`.
- Add `CHANGELOG.md` in Keep a Changelog format.
- Add an MIT license file with the required neutral notice.
- Add `pyproject.toml`.
- Add `requirements-dev.txt`.
- Ensure zip archive contains the skill root folder.
- Run tests before publishing.

## Acceptance checks

- `grep -R "legacy-brand-token\|visual identity\|visual marker\|author" .` returns no prohibited branding/attribution fields except this checklist line if testing raw terms.
- `pytest scripts/test_real-estate-capital-gains-tax_client.py` passes.
- CLI estimate command returns JSON.
- Hebrew file reads naturally and uses Israeli professional terms.
- License text is present.
- Zip archive opens and includes all required files.
