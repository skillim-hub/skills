# Migration Checklist

Use this checklist when replacing an older package.

## Neutralization

- Remove organization names, distributor mentions, sponsorship language, and promotional visual callouts.
- Remove visual brand assets and references to them.
- Remove creator/publisher attribution fields from metadata.
- Use the required neutral MIT holder text in `LICENSE`.
- Replace first-person promotional copy with imperative, neutral guidance.
- Remove unexplained external references that imply endorsement.

## Metadata

- Keep `slug` as `advertising-campaign-planner`.
- Bump `version`.
- Add tags for Israel, Hebrew, Arabic, Russian, ROI, compliance, privacy, accessibility, small business, ecommerce, and lead generation.
- Ensure `entrypoint` points to `SKILL.md`.

## Content

- Add English and Hebrew guides of comparable depth.
- Localize Hebrew examples with ₪ and DD/MM/YYYY.
- Add Israeli consumer, privacy, accessibility, direct-marketing, VAT, and regulated-claim checks.
- Add decision trees, edge cases, anti-patterns, and production checklist.
- Add ROI formulas and conservative interpretation.

## Scripts and tests

- Add typed request, plan, ROI, and validation models.
- Add sync and async planning APIs.
- Add CLI commands for plan, estimate-roi, validate, and template.
- Add examples that run without network access.
- Add at least 20 pytest tests and keep them passing.

## Final verification

- Run pytest.
- Run CLI smoke tests.
- Search for old package identifiers and remove them.
- Confirm no network access is required for normal use.
- Confirm no visual brand files or references remain.
- Confirm Hebrew terminology, dates, and ₪ formatting are correct.
