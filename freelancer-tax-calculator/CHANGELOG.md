# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.


## [2.2.0] - 2026-06-01

### Added

- Web verification log with pass 1 and skeptical pass 2 sources for VAT, osek patur ceiling, small-business normative expenses, income-tax advances, and National Insurance values.
- Explicit 2026 default values in English and Hebrew guides.
- Test coverage for web-validated 2026 National Insurance defaults.

### Changed

- Corrected default National Insurance and health-insurance combined reduced rate from 5.97 percent to 7.70 percent.
- Corrected default National Insurance and health-insurance combined regular rate from 17.83 percent to 18.00 percent.
- Corrected default annual reduced threshold from ₪90,264 to ₪92,436.
- Corrected default annual ceiling from ₪601,680 to ₪622,920.
- Corrected micro-business normative expense eligibility logic to allow eligible low-turnover osek murshe scenarios as well as osek patur scenarios.
- Updated README and references to describe the official BTL adjustment caveat and local reserve-estimate scope.

### Verified

- Pass 1 confirmed VAT at 18 percent from Tax Authority sources and the patur ceiling at ₪122,833 from Tax Authority service pages.
- Pass 2 confirmed VAT using OECD and Knesset or Tax Authority history sources.
- Pass 1 found stale BTL defaults in v2.
- Pass 2 confirmed corrected BTL 2026 rates, reduced base, and annual ceiling using the BTL 2026 circular.
- Pass 1 and Pass 2 confirmed the 30 percent normative expense route and corrected the eligible osek murshe treatment.

## [2.1.0] - 2026-06-01

### Added

- Branding audit report.
- Hebrew quality-assurance log.
- Installable Python package interface for `from freelancer_tax_calculator import ...`.
- Console script entry point named `freelancer-tax-calculator`.
- Scenario `create` and `run` workflow with stable scenario IDs.
- Environment-aware examples that accept `--env sandbox|production` and read `FTC_` environment variables.
- Income-tax advance base selection: `revenue` or `profit`.
- Compile check in the verification process.

### Changed

- Moved the real client implementation to an underscored module name.
- Removed the hyphenated client filename and dynamic import pattern.
- Updated README installation to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Added `pytest-asyncio` to development requirements.
- Updated Hebrew wording, date format, and professional terminology.
- Rechecked public Markdown for neutral voice and visual-mark references.

### Removed

- Public Markdown emoji.
- Hyphenated client module.
- Import examples that required path-based dynamic loading.

## [2.0.0] - 2026-06-01

### Added

- English guide with decision tree, examples, edge cases, troubleshooting, anti-patterns, and production checklist.
- Hebrew guide with Israeli accounting terminology and localized formatting guidance.
- Regulatory and calculation reference with official source links, local request and response examples, and error table.
- End-to-end workflow guide.
- Troubleshooting reference.
- Test scenario catalogue with more than 20 scenarios.
- Migration checklist.
- Typed sync and async Python helper.
- Click-based CLI.
- Pytest suite with more than 20 tests.
- Runnable example scripts.
- README, MIT license, pyproject, and development requirements.

### Changed

- Refocused the package on tax calculation for Israeli freelancers and small businesses.
- Renamed metadata and skill identity to `freelancer-tax-calculator`.
- Made rates and thresholds configurable.

### Removed

- Visual marks, distribution callouts, and attribution metadata.
- Operations-only scope that did not calculate VAT, advances, or National Insurance.
