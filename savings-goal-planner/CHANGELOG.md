# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, source quotes, URLs, and access date.
- Added explicit official-reference notes for VAT, Bank of Israel policy-rate context, inflation-target terminology, CBS price-index API paths, National Insurance brackets, retirement age, training funds, and investment provident funds.
- Added CLI tests for the new `--expected-pension` option and the compatibility `--state-pension` alias.

### Changed

- Replaced public retirement examples using `--state-pension` with `--expected-pension`.
- Clarified that Bank of Israel policy-rate data is market context and not a product yield.
- Clarified that vehicle preset returns, fees, and tax rates are scenario defaults, not official product quotes.
- Corrected 2026 investment provident fund cap references to ₪83,641 after second-pass validation found a stale 2025 figure.
- Expanded API reference examples for CBS `catalog/tree`, `data/price`, `data/calculator/{id}`, and `price_selected_b` endpoint paths.
- Updated Hebrew quality notes for 02/06/2026 source validation, professional terminology, and DD/MM/YYYY formatting.

### Verified

- Pass 1 and Pass 2 double-confirmed the Israeli VAT rate of 18% from 01/01/2025.
- Pass 1 and Pass 2 double-confirmed Bank of Israel policy rate of 3.75% after the 25/05/2026 decision.
- Pass 1 and Pass 2 double-confirmed the 1-3% inflation-target range.
- Pass 1 and Pass 2 double-confirmed National Insurance self-employed 2026 thresholds and rates.
- Pass 1 and Pass 2 double-confirmed retirement-age terminology and the need for user-specific input.
- Pass 1 and Pass 2 confirmed that no webhook event names apply because the package is a deterministic non-API helper.

## [2.1.0] - 2026-06-02

### Added

- Added installable `savings_goal_planner` Python package.
- Added JSON-backed stored goal workflow with `create-goal`, `show-goal`, `list-goals`, and `delete-goal`.
- Added public `GoalRepository` and `StoredGoal` types.
- Added branding audit report.
- Added Hebrew quality assurance log.
- Added explicit example support for `--env sandbox|production` and environment-variable inputs.

### Changed

- Moved runtime imports away from the hyphenated client filename.
- Replaced dynamic script import with package imports.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to extract the created goal identifier and reuse it in the next command.
- Updated development requirements to include `pytest-asyncio`.
- Updated Hebrew text for DD/MM/YYYY localization, neutral imperative voice, and Israeli professional terminology.

### Removed

- Removed the hyphenated client implementation file.
- Removed script path import workarounds from public examples.
- Removed any status-marker, image, or visual mark references from public Markdown.

## [2.0.0] - 2026-06-02

### Added

- Complete neutral `savings-goal-planner` skill package.
- English `SKILL.md` with concrete examples, edge cases, Mermaid decision trees, troubleshooting, anti-patterns, and production checklist.
- Hebrew `SKILL_HE.md` with Israeli professional terminology and shekel formatting.
- Official source and regulation reference in `references/api-reference.md`.
- End-to-end workflows in `references/workflow-guide.md`.
- Extended troubleshooting in `references/troubleshooting.md`.
- More than 20 concrete scenarios in `references/test-scenarios.md`.
- Migration checklist in `references/migration-checklist.md`.
- Typed synchronous and asynchronous calculation helper.
- Full Click command-line interface.
- Pytest suite with more than 20 tests.
- Six runnable example scripts.
- Package metadata, README, MIT license, pyproject, and development requirements.

### Changed

- Reframed the package from shopping and deal optimization to savings-goal planning.
- Added Israeli vehicle modelling presets for cash, bank deposits, money-market funds, government bond funds, taxable portfolios, equity index funds, training funds, investment provident funds, and pension funds.
- Added retirement gap modelling using real returns and today's shekels.
- Added business and freelancer reserve workflows for VAT, income tax, and National Insurance.

### Removed

- Removed branding.
- Removed organization attribution.
- Removed creator-attribution metadata.
- Removed visual mark and image references.
- Removed shopping-deal and loyalty-program focus.

### Security

- Added input validation for negative amounts, invalid periods, invalid rates, and unknown vehicle keys.
- Added explicit warnings for unsuitable horizons, aggressive return assumptions, high inflation assumptions, and affordability pressure.
