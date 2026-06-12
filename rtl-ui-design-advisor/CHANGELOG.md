# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-03

### Added
- Added `references/verification-log.md` with two-pass web validation and official-source snippets.
- Added verified standard Israeli VAT documentation: 18%, effective 01/01/2025, double-confirmed for 2026.
- Added clarification that privacy registration, notice, and DPO duties are context-dependent.
- Added verification-log tests.

### Changed
- Bumped metadata and package version to 2.2.0.
- Updated English and Hebrew guides to point to the web validation log for current VAT context while preserving the rule not to hard-code tax rates in UI.
- Expanded README file index to include the verification log.

### Pass 1 findings
- Israeli VAT rate confirmed as 18% from official Tax Authority terminology.
- Israeli accessibility terminology confirmed against gov.il accessibility sources.
- Privacy Protection Authority terminology confirmed against gov.il sources.
- Consumer price-display concerns confirmed against Consumer Protection Authority guidance.
- HTML `dir`, `bdi`, CSS logical properties, Tailwind logical utilities, React portal behavior, and W3C language-direction metadata guidance confirmed against primary sources.

### Pass 2 findings
- VAT effective date and 2026 currency confirmed against different official sources.
- Accessibility standard language confirmed against FAQ and public-sector accessibility statements.
- Privacy Amendment 13 registration and notice distinctions confirmed against different gov.il pages.
- Consumer cancellation/price guidance confirmed against a second Consumer Protection Authority page.
- Technical RTL guidance confirmed against separate W3C, MDN, React, and Tailwind sources.
- No final unconfirmed rows remained.


## [2.1.0] - 2026-06-03

### Added
- Added a deep neutrality audit report under `references/branding-audit.md`.
- Added Hebrew quality log under `references/hebrew-qa-log.md`.
- Added installable Python module under `src/rtl_ui_design_advisor`.
- Added stored audit workflow with `create-audit` and `show-audit`.
- Added environment-aware runnable examples that read environment variables and print JSON with preserved Hebrew.

### Changed
- Replaced the hyphenated client script with an underscored client script.
- Updated README installation to `pip install -e .` plus `pip install -r requirements-dev.txt`.
- Updated Israeli date examples to DD/MM/YYYY.
- Reworked Hebrew prose to reduce unnecessary Anglicisms and maintain neutral imperative wording.
- Updated imports to use `from rtl_ui_design_advisor import ...`.

### Fixed
- Removed public Markdown emoji, badge references, logo references, and banner references.
- Ensured metadata has no author field.
- Kept MIT license holder text as neutral authorship.
- Added syntax compilation check coverage for scripts.

## [2.0.0] - 2026-06-03

### Added
- Comprehensive English and Hebrew RTL implementation guides.
- Browser, framework, regulation, and localization reference.
- End-to-end workflow guide.
- Dedicated troubleshooting guide.
- Test-scenarios reference with more than 20 concrete cases.
- Migration checklist for existing LTR products.
- Static audit helper, command-line interface, examples, and pytest suite.

### Changed
- Removed branding, organization references, logos, distribution callouts, and metadata authorship.
- Reworked wording into neutral imperative guidance.
