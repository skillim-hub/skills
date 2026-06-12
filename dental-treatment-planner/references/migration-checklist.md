# Migration Checklist

Use this checklist when migrating from the stub package to the enhanced package.

## Package structure

- [ ] Replace stub `SKILL.md`.
- [ ] Replace stub `SKILL_HE.md`.
- [ ] Add `README.md`.
- [ ] Add `CHANGELOG.md`.
- [ ] Add `LICENSE`.
- [ ] Add `pyproject.toml`.
- [ ] Add `requirements-dev.txt`.
- [ ] Add all reference files.
- [ ] Add the typed client.
- [ ] Add the Typer CLI.
- [ ] Add pytest coverage.
- [ ] Add runnable examples.

## Metadata

- [ ] Bump version to `1.0.0` or later.
- [ ] Remove creator-person fields.
- [ ] Remove organization fields.
- [ ] Remove visual promotional assets and media references.
- [ ] Expand tags for Israeli context, cost estimation, Hebrew, CLI, and offline-first use.
- [ ] Keep license as MIT.

## Content migration

- [ ] Replace generic stub language with imperative operating guidance.
- [ ] Add Israeli provider routes.
- [ ] Add ₪ cost examples.
- [ ] Add DD/MM/YYYY examples in Hebrew material.
- [ ] Add emergency red-flag handling.
- [ ] Add insurance/supplementary-plan handling.
- [ ] Add business cash-flow guidance.
- [ ] Add privacy and tax boundaries.
- [ ] Add anti-patterns.
- [ ] Add production checklist.

## Data migration

- [ ] Map existing treatment labels to built-in codes.
- [ ] Identify unsupported local clinic items.
- [ ] Add `override_price_ils` only for written quote prices.
- [ ] Attach `source_date` to any imported tariff.
- [ ] Mark old tariff rows inactive rather than deleting them.
- [ ] Keep a changelog entry for price-table changes.

## Testing

- [ ] Run `python -m pytest -q`.
- [ ] Run CLI sample generation.
- [ ] Run CLI estimate in JSON mode.
- [ ] Run CLI estimate in Markdown mode.
- [ ] Run CLI compare.
- [ ] Run strict validation scenario.
- [ ] Run at least one Hebrew-facing manual review.
- [ ] Confirm neutral metadata and no promotional visual assets remain.

## Production readiness

- [ ] Replace example provider factors with source-backed pricing where available.
- [ ] Add manual review for complex implant, orthodontic, surgical, and emergency cases.
- [ ] Add privacy controls for stored dental plans.
- [ ] Add patient consent wording before upload or storage.
- [ ] Add data-retention policy.
- [ ] Add accountant-review handoff for business expense questions.
- [ ] Add provider-tariff refresh schedule.
