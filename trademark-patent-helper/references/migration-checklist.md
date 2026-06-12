# Migration checklist

## Content

- [ ] Remove branding, badges, banners, package logos, image references, author names, and distribution callouts.
- [ ] Remove `author` from metadata.
- [ ] Use MIT license with the required collective-author notice.
- [ ] Replace promotional tone with neutral imperative instructions.
- [ ] Provide English and Hebrew guides.
- [ ] Add Israeli small-business, freelancer, startup, importer, and consumer examples.
- [ ] Add official-fee/form/deadline verification warnings.
- [ ] Add trademark/patent/design/copyright/company/domain distinctions.
- [ ] Add confidentiality warning for patent matters.
- [ ] Add public disclosure timeline.
- [ ] Add employee, contractor, founder, and academic ownership checks.

## Structure

- [ ] Root includes `README.md`, `CHANGELOG.md`, `LICENSE`, `metadata.json`, `pyproject.toml`, and `requirements-dev.txt`.
- [ ] `references/` includes `api-reference.md`, `workflow-guide.md`, `document-workflows.md`, `troubleshooting.md`, `test-scenarios.md`, and `migration-checklist.md`.
- [ ] `scripts/` includes client, CLI, pytest suite, and examples.

## Localization

- [ ] Use natural Israeli legal/business terminology.
- [ ] Use ₪ for money examples.
- [ ] Use DD/MM/YYYY for Hebrew-local dates.
- [ ] Avoid unnecessary transliteration where Hebrew terminology exists.
- [ ] Preserve common professional acronyms such as PCT and SaaS only where useful.

## CLI/client

- [ ] Add typed data objects.
- [ ] Support sync and async assessment.
- [ ] Support JSON and Markdown output.
- [ ] Validate trademark classes 1-45.
- [ ] Detect descriptive marks, broad classes, public disclosures, ownership risk, regulated fields, and business-method risk.
- [ ] Add Click or Typer CLI.
- [ ] Add runnable examples.

## Tests

- [ ] Include at least 20 pytest tests.
- [ ] Test trademark, patent, CLI, async, date normalization, and serialization.
- [ ] Run pytest from package root.
- [ ] Confirm all tests pass before archiving.

## Packaging

- [ ] Exclude caches and temporary files.
- [ ] Confirm total file count.
- [ ] Confirm archive path is `/mnt/data/trademark-patent-helper-enhanced.zip`.
