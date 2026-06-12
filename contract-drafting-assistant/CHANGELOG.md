# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog principles, and the package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added live-source verification log with two-pass validation rows for Israeli statutory, tax, public-data, and official terminology references.
- Added 2026 Contracts (General Part) Law section 25 interpretation guidance for business contracts and exclusions for standard, consumer, employment, and collective-agreement contexts.
- Added live verification notes for the 18% Israeli VAT assumption, Bank of Israel exchange-rate endpoint, data.gov.il CKAN endpoint, companies dataset/search, withholding-tax certificate checks, and privacy outsourcing controls.
- Added test scenarios for post-2026 business contract interpretation and VAT verification before signing.


### Verification findings

- Double-confirmed: standard Israeli VAT rate.
- Double-confirmed: VAT clause style should use lawful-rate wording rather than permanent rate text.
- Double-confirmed: tax-invoice allocation is a live Tax Authority workflow and thresholds should not be hardcoded.
- Double-confirmed: withholding-tax certificates should be checked through Tax Authority certificate services.
- Corrected: added the 2026 Contracts (General Part) Law section 25 interpretation amendment.
- Corrected: business-contract interpretation guidance now distinguishes business contracts from standard, consumer, employment, and collective-agreement contexts.
- Double-confirmed: Contracts (General Part) Law identity.
- Double-confirmed: Remedies Law identity.
- Double-confirmed: Standard Contracts Law and unfair-term warnings.
- Double-confirmed: consumer cancellation concepts.
- Double-confirmed: official consumer-protection terminology.
- Double-confirmed: Privacy Protection data-security regulations.
- Double-confirmed: privacy outsourcing supplier terms.
- Double-confirmed: serious security incident reporting concept.
- Double-confirmed: Copyright Law reference and assignment/license distinction.
- Double-confirmed: Electronic Signature Law reference.
- Double-confirmed: Arbitration Law reference.
- Double-confirmed: Sale Law reference.
- Double-confirmed: Agency Law reference.
- Double-confirmed: Guarantee Law reference.
- Double-confirmed: Pledge Law reference.
- Double-confirmed: interest and linkage source handling.
- Double-confirmed: Defective Products Liability Law reference.
- Double-confirmed: employee-contractor classification risk reference.
- Double-confirmed: data.gov.il CKAN endpoint.
- Double-confirmed: companies dataset and Corporations Authority search workflow.
- Double-confirmed: Bank of Israel exchange-rate page.
- Double-confirmed: Bank of Israel JSON endpoint.
- Double-confirmed: no single municipal permit API assumption should be made.
- Double-confirmed: webhook event names are not applicable to this local helper package.
- Double-confirmed: official Hebrew terminology for tax, consumer, privacy, and contract workflows.
- Corrected: absolute legal-compliance positioning was replaced with drafting and risk-review positioning.

### Changed

- Replaced absolute compliance positioning with draft-and-risk-review language.
- Clarified that contract clauses should usually say "VAT at the lawful rate" or "מע״מ כדין" rather than permanently hardcoding a tax rate in legal text.
- Clarified that Bank of Israel representative rates are indicators and must be selected contractually if used for linkage.
- Expanded API-reference coverage for non-API public lookup workflows and explicitly marked webhooks as not applicable.

### Fixed

- Corrected omission of the 2026 Contracts (General Part) Law interpretation amendment from prior package versions.
- Kept helper VAT default at 18% after double validation.

## [2.1.0] - 2026-06-02

### Changed

- Moved the real Python implementation into underscored module files and removed hyphenated implementation files.
- Updated installation instructions to use editable installation followed by development requirements.
- Updated quick-start flow to persist a create-response identifier before the validation step.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print structured JSON using `ensure_ascii=False` and `indent=2`.
- Updated package configuration so top-level module imports work after editable installation.
- Updated date localization to `DD/MM/YYYY` in public guidance and helper output.
- Tightened Hebrew text by removing niqqud and replacing non-neutral phrasing.

### Added

- Added branding and attribution audit report.
- Added Hebrew quality assurance log.

### Fixed

- Removed importlib-based shims and direct loading of hyphenated Python files.
- Removed stale references to deleted Python filenames.
- Confirmed public Markdown contains no decorative image, visual identity, or emoji content.

## [2.0.0] - 2026-06-02

### Added

- Expanded scope from a narrow employment-contract workflow to a general Israeli contract drafting assistant.
- Added comprehensive English guide with decision trees, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- Added comprehensive Hebrew guide with Israeli professional terminology, ₪ currency formatting, and DD/MM/YYYY dates.
- Added statutory and public-data reference covering contracts, remedies, standard terms, consumer protection, VAT, privacy, data security, copyright, sale, arbitration, and electronic signatures.
- Added workflow guide for freelance services, consumer services, NDAs, sale/supply, website terms, negotiation, and final handoff.
- Added standalone troubleshooting guide with severity model and replacement clause snippets.
- Added 30 concrete test scenarios.
- Added migration checklist.
- Added typed sync/async helper module.
- Added Typer CLI.
- Added runnable scenario scripts.
- Added pytest suite with more than 20 tests.
- Added project configuration and development requirements.
- Added MIT license.

### Changed

- Renamed package to `contract-drafting-assistant`.
- Switched drafting voice to neutral imperative style.
- Replaced employment-only examples with broader Israeli small-business, freelancer, and consumer examples.
- Added risk scanner and renderer for Hebrew and English drafts.
- Added structured handling for VAT, personal data, IP, consumer status, liability, and worker-classification risk.

### Removed

- Removed metadata fields identifying a person or organization.
- Removed promotional compatibility callouts.
- Removed visual identity asset, decorative marker, decorative header, and image references.
- Removed employment-only positioning as the primary purpose.
