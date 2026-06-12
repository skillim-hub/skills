# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.



## [2.2.0] - 2026-06-04

### Added

- Web-validated `references/verification-log.md` with Pass 1 and Pass 2 sources per row.
- Official 2026 checkpoint tables in English and Hebrew guides.
- Current VAT, pension, National Insurance, Keren Hishtalmut, Israel Invoice, Form 161, Form 135, Form 126, privacy, and API documentation checks.

### Changed

- Clarified that provider API paths, hosts, webhook event names, and error codes are illustrative unless confirmed by official developer-portal or signed vendor documentation.
- Added explicit 18% VAT checkpoint effective 01/01/2025.
- Added 2026 Israel Invoice allocation-number threshold: ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026.
- Added employee pension baseline of 18.5% with 6% employee, 6.5% employer pension, and 6% employer severance, subject to exceptions.
- Added severance completion warning where 6% may need review against 8.33%.
- Added self-employed pension bracket references of 4.45% and 12.55%.
- Added Keren Hishtalmut 2026 references for ₪188,544 employee salary basis and ₪293,397 self-employed income ceiling.
- Added National Insurance self-employed 2026 classification and example-rate checkpoints.

### Verified

- Pass 1 and Pass 2 double-confirmed 16 checks.
- Corrected in Pass 2: 0.
- Final unconfirmed items: 1; public webhook event names were not confirmed and must not be invented.

## [2.1.0] - 2026-06-04

### Added

- Branding, author, logo, badge, and Markdown emoji audit report.
- Hebrew QA log with terminology and localization changes.
- Plan creation and retrieval flow with `plan_id` for chained quick-start use.
- CLI `create` and `show` commands.
- Environment-aware examples using `--env sandbox|production` and environment variables.

### Changed

- Removed duplicate hyphenated client script; the underscored client module is the implementation.
- Updated README installation to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated examples to print JSON using `json.dumps(ensure_ascii=False, indent=2)`.
- Updated Hebrew date localization to DD/MM/YYYY.
- Updated package configuration so `from benefit_perk_planner_client import ...` works after editable install.

### Fixed

- Verified public Markdown contains no emoji, badge URLs, logo references, banner images, or branding callouts.
- Confirmed Python syntax with `compileall`.

## [2.0.0] - 2026-06-04

### Added

- Comprehensive English operating guide with examples, edge cases, decision tree, troubleshooting, anti-patterns, and production checklist.
- Hebrew operating guide with Israeli professional terminology, ₪ formatting, and DD-MM-YYYY localization.
- Israeli source and integration reference with request/response examples and error tables.
- Workflow guide for meal benefits, Keren Hishtalmut, freelancers, salary comparisons, migrations, and quarterly reviews.
- Dedicated troubleshooting guide.
- 30 concrete test scenarios.
- Migration checklist for moving from informal perks to documented policy.
- Typed synchronous and asynchronous Python planner client.
- Typer CLI.
- Five runnable scenario scripts plus a request-file example.
- pytest suite with more than 20 tests.
- MIT license.
- Python packaging and development requirements.

### Changed

- Reworked content into neutral, imperative, implementation-focused guidance.
- Expanded Israeli small-business, freelancer, employee, and consumer coverage.
- Removed promotional and identity-specific material.
