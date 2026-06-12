# Migration Checklist

## Remove non-neutral elements

- [ ] Remove visual marks, badges, decorative images, decorative images, and distribution callouts.
- [ ] Remove attribution metadata.
- [ ] Keep the required MIT copyright notice in LICENSE.
- [ ] Use neutral imperative language.

## Update identity

- [ ] Root directory is `disaster-preparedness-guide`.
- [ ] Metadata and front matter use `disaster-preparedness-guide`.
- [ ] Version is bumped to `2.0.0` or later.
- [ ] Tags cover Israel, Hebrew, Home Front Command, small business, freelancer, accessibility, earthquake, hazmat, tsunami, radiological, missile alert, and business continuity.
- [ ] `metadata.json` has no `author` field.

## Add required content

- [ ] `SKILL.md` comprehensive English guide.
- [ ] `SKILL_HE.md` same depth in natural Israeli Hebrew with ₪ and DD/MM/YYYY examples.
- [ ] `references/api-reference.md` equivalent non-API reference.
- [ ] `references/workflow-guide.md`.
- [ ] `references/troubleshooting.md`.
- [ ] `references/test-scenarios.md` with 20+ scenarios.
- [ ] `references/migration-checklist.md`.
- [ ] `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `requirements-dev.txt`.

## Safety migration

- [ ] Add official-instructions override.
- [ ] Separate missile behavior from earthquake behavior.
- [ ] Separate hazmat behavior from underground shelter behavior.
- [ ] Add accessibility and special populations.
- [ ] Add business continuity, bookkeeping, insurance, suppliers, and reopening criteria.
- [ ] Add anti-patterns and troubleshooting.

## Script migration

- [ ] Typed sync/async helper exists.
- [ ] Click/Typer CLI exists.
- [ ] 5+ examples exist.
- [ ] pytest suite has 20+ tests and passes.
