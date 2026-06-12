# Migration Checklist

## Neutral package

- Remove promotional language.
- Remove visual identity assets and image references.
- Remove named-credit metadata.
- Use imperative, professional voice.
- Set MIT license with the required copyright line.

## Metadata

Required: slug, name, version, description, license, language, tags, entrypoints, minimum Python. Do not include a named-credit field.

## Layout

Expected files: SKILL.md, SKILL_HE.md, README.md, CHANGELOG.md, LICENSE, metadata.json, pyproject.toml, requirements-dev.txt, references, scripts, examples, tests.

## References

Move Israeli official-source notes to api-reference. Include Central Bureau of Statistics, Israel Tax Authority, Planning Administration, municipalities, Fire and Rescue, accessibility, standards, environmental hazards, and health/business rules.

## Workflows

Add apartment, quote normalization, clinic, retail, landlord make-ready, water damage, shell-to-finish, change-order, payment milestone, and report workflows.

## Troubleshooting

Cover low estimates, high estimates, VAT ambiguity, old buildings, occupied work, licensing, structural work, food businesses, clinics, and inflation updates.

## Tests

Maintain at least 20 pytest cases covering residential, commercial, invalid inputs, VAT, async, Hebrew output, line items, quote review, and risk flags.

## Quality gate

Run tests, inspect metadata, verify no image references, confirm license text, confirm zip name, and confirm all required files exist.
