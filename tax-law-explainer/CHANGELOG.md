# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added
- Two-pass web validation log with pass 1 and pass 2 sources for official Israeli tax-law, VAT, real-estate, form, threshold, and API claims.
- Web-validated current reference values for VAT, exempt dealer threshold, residential rent, Form 1301 dates, purchase-tax bracket snapshot, and real-estate declaration timing.
- `TaxLawExplainerClient.reference_values()` for deterministic access to captured reference values.

### Changed
- Clarified that official Tax Authority API endpoint documentation requires software-house/developer registration and that this package does not call government APIs.
- Added current 2026 checkpoints to the workflow and troubleshooting guides.

### Web validation findings
- ✓✓ Current Israeli VAT rate: Added current VAT rate 18% and access date to reference values.
- ✓✓ VAT terminology and single-rate framing: Kept VAT terminology; added rate cross-reference.
- ✗→✓ Exempt dealer 2026 turnover ceiling: Inserted explicit 2026 threshold where the package previously only said to verify the threshold.
- ✓✓ Small business owner ceiling: Added cross-reference that the micro-business track follows the exempt-dealer ceiling.
- ✓✓ Annual individual return Form 1301 and 2026 filing dates for 2025 tax year: Added Form 1301 date references to the API/reference table.
- ✓✓ Withholding-tax and bookkeeping confirmations: Kept terminology and added service reference.
- ✗→✓ Residential rental income tracks: Added 2026 reference note for the 5,654 ₪ ceiling and 10% section 122 track.
- ✓✓ Purchase-tax single apartment brackets: Added bracket snapshot and warning to verify simulator before quoting final liability.
- ✓✓ Real Estate Taxation Law official English terminology: Kept English law name and added terminology note.
- ✓✓ Real-estate transaction reporting deadline: Added 30-day reporting reminder to real-estate workflow references.
- ✓✓ Income Tax Ordinance official English terminology: Kept law naming and connected Form 1301 to individual annual returns.
- ✗→✓ Israel Invoice allocation-number API/service existence: Corrected API wording: the skill has no government integration, but ITA APIs exist for registered software houses.
- ✓✓ API registration host / restricted developer docs: Added note that endpoint paths and webhook events are not public in this skill and require registered portal access.
- ✓✓ Webhook event names: Logged no webhook event names as applicable; no code change required.

## [2.1.0] - 2026-06-02

### Added
- Branding and emoji audit report.
- Hebrew quality-assurance log.
- Installable `tax_law_explainer` package with public imports.
- Example scripts with environment-variable support and `--env sandbox|production`.
- CLI environment option for sandbox and production-style dry-run contexts.
- Compileall syntax check as a release validation step.

### Changed
- Replaced hyphenated client implementation with an underscored compatibility wrapper and package module.
- Updated README install instructions to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick-start to show chained use of the explanation topic identifier.
- Localized Hebrew date style to DD/MM/YYYY and reduced unnecessary Anglicisms.
- Expanded tests for package import, wrapper presence, client-file removal, and CLI environment output.

### Removed
- Removed hyphenated `scripts/tax_law_explainer_client.py` implementation.

## [2.0.0] - 2026-06-02

### Added
- Comprehensive English guide with decision trees, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- Hebrew guide using natural Israeli professional terminology, ₪ currency formatting, and DD-MM-YYYY date style.
- Structured reference for Israeli tax statutes, official portals, forms, filing workflows, and helper request/response formats.
- End-to-end workflow guide covering freelancer onboarding, VAT correction, withholding, property transactions, audit response, and consumer checks.
- Dedicated troubleshooting guide.
- Test-scenario catalog with more than 20 concrete scenarios.
- Migration checklist for replacing older incomplete skill packages.
- Typed Python helper with synchronous and asynchronous interfaces.
- Typer CLI with explanation, checklist, scenario, validation, and export commands.
- Runnable examples under `scripts/examples`.
- Pytest suite with more than 20 passing tests.
- Packaging files, development requirements, MIT license, and README.

### Changed
- Removed organizational identity, visual marks, creator metadata, distribution language, and first-person voice.
- Expanded metadata tags and raised package version.

### Security
- Added explicit safeguards against producing filing-ready tax advice without supplied facts and current official verification.

## [1.0.0] - Initial package

### Added
- Initial baseline package.
