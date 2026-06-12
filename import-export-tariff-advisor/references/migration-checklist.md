# Migration Checklist

Use this checklist when replacing an older tariff-estimation prompt, spreadsheet, or script with this enhanced skill.

## Content migration

- Remove branding, visual marks, decorative marks, personal credit names, distribution notes, and promotional text.
- Replace first-person plural wording with imperative instructions.
- Add bilingual support: English `SKILL.md` and Hebrew `SKILL_HE.md`.
- Convert generic import-tax language into Israel-specific terminology.
- Add warnings for Israeli tariff-code validation, purchase tax, VAT base, and import approvals.
- Add separate references for API/regulation checks, workflows, troubleshooting, and scenarios.

## Data migration

- Normalize tariff codes by removing punctuation.
- Store Israeli tariff suffix separately from international HS 6-digit headings.
- Store duty, purchase tax, and VAT rates as decimals.
- Store estimate date in `DD-MM-YYYY` for Hebrew-facing reports and ISO format internally.
- Store exchange rate and source date.
- Store line items rather than one free-text description for mixed shipments.
- Store assumptions and warnings with every estimate.

## Code migration

- Replace spreadsheet-only formulas with typed calculation models.
- Keep VAT configurable.
- Validate rates between 0 and 1.
- Validate non-negative monetary values.
- Expose both sync and async client methods.
- Add a CLI command for quick estimates.
- Add pytest coverage for validation, calculation, JSON output, and warning behavior.
- Add example scripts for common scenarios.

## Operational migration

- Train users to distinguish government taxes from courier/broker fees.
- Require product descriptions good enough for classification.
- Route regulated or high-value shipments to broker review.
- Keep source references and retrieval dates.
- Avoid claiming that an estimate is official.
- Review defaults whenever Israeli tax rates, tariff lines, or import rules change.

## Acceptance checklist

- `pytest` passes.
- CLI returns valid JSON with `--json`.
- Hebrew guidance uses natural Israeli terminology.
- No author field exists in `metadata.json`.
- License names "The Credits".
- No visual marks, decorative marks, decorative headers, or image references remain.
- Documentation covers at least 20 scenarios.
- Examples are runnable from the repository root.
