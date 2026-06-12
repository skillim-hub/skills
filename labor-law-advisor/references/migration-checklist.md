# Migration Checklist

Use this checklist to migrate from the uploaded prior package to this enhanced `labor-law-advisor` package.

## Scope changes

- [ ] Rename the skill directory to `labor-law-advisor`.
- [ ] Remove all organization names, attribution claims, channel-specific callouts, and visual asset references.
- [ ] Replace prior metadata with neutral `metadata.json`.
- [ ] Keep English and Hebrew guides at equivalent depth.
- [ ] Treat this as a legal-information assistant, not a legal-decision engine.
- [ ] Add structured helper scripts and tests.

## File migration

| Old item | New item | Action |
|---|---|---|
| `SKILL.md` | `SKILL.md` | Replace with expanded English guide |
| `SKILL_HE.md` | `SKILL_HE.md` | Replace with localized Hebrew guide |
| `references/labor-laws-summary.md` | `references/api-reference.md` | Convert into official-source reference and local interface |
| `references/entitlements-calculator.md` | `references/workflow-guide.md` | Move calculations into workflows and client |
| `scripts/severance-calculator.py` | `scripts/labor_law_advisor_client.py` | Replace one-purpose calculator with typed helper |
| none | `scripts/labor-law-advisor-cli.py` | Add Typer CLI |
| none | `scripts/test_labor-law-advisor_client.py` | Add pytest suite |
| none | `scripts/examples/` | Add runnable scenarios |
| none | `references/troubleshooting.md` | Add issue-resolution guide |
| none | `references/test-scenarios.md` | Add 20+ concrete scenarios |
| none | `references/migration-checklist.md` | Add migration steps |
| none | `CHANGELOG.md` | Add Keep-a-Changelog record |
| none | `README.md` | Add install and file index |
| none | `LICENSE` | Add MIT license |
| none | `pyproject.toml` and `requirements-dev.txt` | Add packaging/test metadata |

## Metadata migration

- [ ] Remove attribution metadata fields.
- [ ] Use version `2.0.0` or later.
- [ ] Add Hebrew and English tags.
- [ ] Include jurisdiction `IL`.
- [ ] Include date reviewed.
- [ ] Do not mention unsupported agents, channels, or organizations.
- [ ] Avoid visual assets and decorative artwork.

## Content migration

- [ ] Add minimum wage with effective date and verification warning.
- [ ] Add overtime daily/weekly decision tree.
- [ ] Add severance, Section 14, release documents, and edge cases.
- [ ] Add parental rights and protected-status workflow.
- [ ] Add Histadrut, collective agreement, and extension-order workflow.
- [ ] Add freelancer/employee classification risk.
- [ ] Add household worker and consumer-facing guidance.
- [ ] Add anti-patterns and safety boundaries.
- [ ] Add production checklist.
- [ ] Add examples using ₪ and DD-MM-YYYY.
- [ ] Localize Hebrew naturally.

## Code migration

- [ ] Keep calculations deterministic and documented.
- [ ] Return typed dataclasses with `.to_dict()`.
- [ ] Provide sync and async methods.
- [ ] Add CLI commands for common calculations.
- [ ] Include examples for minimum wage, overtime, severance, sick pay, parental rights, and collective coverage.
- [ ] Add at least 20 tests.
- [ ] Run `python -m pytest scripts -q`.
- [ ] Confirm all tests pass.

## Validation checklist

- [ ] Search package for organization names, attribution claims, channels, and visual asset references.
- [ ] Confirm `metadata.json` contains only neutral metadata fields.
- [ ] Confirm LICENSE uses the required MIT copyright line.
- [ ] Confirm Hebrew dates use DD-MM-YYYY.
- [ ] Confirm all scripts run without network access.
- [ ] Confirm ZIP root contains `labor-law-advisor/`.
