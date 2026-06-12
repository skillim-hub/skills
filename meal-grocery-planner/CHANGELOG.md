# Changelog

All notable changes to this package are documented in this file. The format follows Keep a Changelog.


## [1.3.0] - 2026-06-04

### Added

- Added two-pass web verification log with official-source snippets, URLs, access date, and double-confirmation status.
- Added verified official context for VAT, supermarket price transparency, consumer price display, allergen labeling, kashrut marking, and controlled-price complaints.

### Changed

- Corrected Rami Levy generated search links from `/he/search` to `/he/online/search`.
- Corrected Yochananof generated search links to use the Yochananof domain rather than an unrelated retailer domain.
- Clarified that built-in delivery-fee and minimum-order values are sandbox estimates and must be checked in the live retailer cart.
- Updated API reference, English guide, Hebrew guide, README, workflow guide, troubleshooting guide, tests, examples, and script mirror to align with the web validation pass.

### Verified

- Confirmed the Israeli VAT rate at 18% from 01/01/2025 and cross-checked it with 2026 tax references.
- Confirmed official price-transparency duties for large food retailers and availability of retailer transparency pages or files.
- Confirmed public online shopping/search presence for Shufersal, Rami Levy, Victory, and Yochananof.
- Confirmed official terminology for consumer price display, food allergen labeling, kashrut marking, and supervised-price complaints.

## [1.2.0] - 2026-06-04

### Added

- Added installable `meal_grocery_planner` package with typed client exports.
- Added Typer command entry point named `meal-grocery-planner`.
- Added branding audit report.
- Added Hebrew quality log.
- Added syntax and test verification step to the release process.

### Changed

- Moved client implementation away from a hyphenated Python filename.
- Updated README installation commands to use editable installation and development requirements.
- Updated quick start to extract an order id from a create response and use it in a follow-up command.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with unescaped Hebrew.

### Removed

- Removed legacy hyphenated client script.
- Removed decorative public Markdown elements.

## [1.1.0] - 2026-06-04

### Added

- Added bilingual operating guides.
- Added API and regulation reference material.
- Added workflow guide, troubleshooting, test scenarios, migration checklist, examples, and pytest suite.
- Added MIT license and project metadata.

## [1.0.0] - 2026-06-04

### Added

- Initial neutral meal and grocery planning package.
