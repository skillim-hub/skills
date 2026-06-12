# Migration checklist

Use this checklist when moving from the earlier car-insurance-centered package to the enhanced health, home, and life insurance analyzer.

## Identity

- Rename root directory to `insurance-coverage-analyzer`.
- Set metadata `name` to `insurance-coverage-analyzer`.
- Remove all author fields.
- Remove organization branding and distribution callouts.
- Remove badges, banners, logos, and image references.
- Use neutral imperative wording.
- Keep the MIT license with the required neutral Authors notice.

## Scope

- Remove car-insurance-first positioning.
- Add health analysis: surgery, drugs outside basket, transplants, ambulatory, specialist consultations, serious illness, exclusions, waiting periods, supplementary overlap.
- Add home analysis: structure, contents, mortgage, water, earthquake, third-party liability, employer liability, valuables, business equipment.
- Add life analysis: death benefit, mortgage assignment, beneficiaries, premium path, riders, exclusions, business-continuity needs.

## Documentation

- Expand `SKILL.md`.
- Expand `SKILL_HE.md`.
- Add `references/api-reference.md`.
- Add `references/workflow-guide.md`.
- Add `references/troubleshooting.md`.
- Add `references/test-scenarios.md`.
- Add this checklist.
- Add `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, and `requirements-dev.txt`.

## Scripts

- Add typed sync and async client.
- Add Typer CLI.
- Add pytest suite with at least 20 tests.
- Add at least 5 runnable examples.
- Keep processing local and deterministic.

## Data mapping

| Old concept | New field |
|---|---|
| Product category | `policy_type` |
| Company | `insurer` |
| Annual price | `premium_annual_nis` |
| Monthly price | `premium_monthly_nis` |
| Coverage row | `coverages.<coverage_key>` |
| Deductible | `coverages.<coverage_key>.deductible_nis` |
| Exclusion | `exclusions[]` |
| Source | `source.document_name` or `source.url` |

## Quality gates

- Run `pytest`.
- Confirm test count is at least 20.
- Confirm `metadata.json` has no `author`.
- Confirm no branding strings remain.
- Confirm no Markdown image syntax exists.
- Confirm Hebrew uses professional Israeli terminology.
- Confirm `₪` and `DD/MM/YYYY` examples exist.
- Confirm replacement warnings exist.
