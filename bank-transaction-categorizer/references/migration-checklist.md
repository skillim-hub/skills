# Migration Checklist

## Package migration

- Remove branding, organization names, badges, logos, and distribution callouts.
- Confirm `metadata.json` has no `author` field.
- Confirm `LICENSE` uses `Copyright (c) The Authors`.
- Replace minimal docs with `SKILL.md` and `SKILL_HE.md`.
- Add reference, workflow, troubleshooting, test-scenario, and migration documents.
- Add typed client, full CLI, examples, pytest suite, changelog, and project files.

## Data migration

- Keep original statement exports unchanged.
- Create a new folder for categorized outputs.
- Do not overwrite historical manual spreadsheets.
- Test one sample from every bank/account format.
- Compare totals against existing spreadsheets.
- Add custom rules for stable repeated merchants.
- Preserve manual overrides separately.

## Rule migration

- Convert spreadsheet formulas to JSON rules.
- Use one rule per merchant or concept.
- Add `direction` to reduce false positives.
- Use higher priority for specific rules.
- Avoid private customer names in shared rules.
- Add tests for high-value rules.

## Workflow migration

- Replace manual copy/paste with CLI command templates.
- Use file names such as `YYYY-MM-bank-source.csv` and `YYYY-MM-categorized.csv`.
- Add review status: draft, reviewed, sent, approved.
- Reconcile credit-card settlements monthly.
- Store source hash and rules version.

## Production readiness

- Confirm privacy controls for raw statements.
- Confirm backup and retention rules.
- Confirm accountant or bookkeeper review.
- Confirm no banking credentials are stored.
- Confirm all tests pass.
