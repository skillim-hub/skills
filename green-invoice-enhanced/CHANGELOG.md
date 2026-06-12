# Changelog

All notable changes are documented in this file. The format follows Keep a Changelog and uses semantic versioning.


## [1.5.0] - 2026-06-01

### Changed
- Live-validated public documentation links and added a full verification log with source URLs, short quotes, and access date.
- Updated authentication examples and client behavior for the 2026 token request change requiring `grant_type: "client_credentials"`.
- Updated token response handling to prefer `accessToken` while retaining compatibility with legacy `token` responses.
- Removed documentation claims that a nonstandard `X-Authorization-Bearer` response header is currently documented.
- Replaced generic SHAAM allocation wording with a dated threshold table for May 2024, January 2025, January 2026, and June 2026 onward.
- Clarified that the current webhook payload examples use `paymentMethod.type` strings such as `wire-transfer`, while the legacy numeric payment table is not confirmed in the public help-center pages.
- Removed any asserted pagination maximum where the public dynamic developer documentation could not be indexed with a stable max value.

### Verified
- Confirmed the public API documentation landing page, API-key help page, Tax Authority connection guide, webhook setup guide, webhook payload sample, document type code table, VAT rate, 2026 allocation thresholds, and 2026 API infrastructure update.

## [1.4.1] - 2026-05-31

### Fixed

- Replaced the hyphenated Python client module with a direct underscore module at `scripts/green_invoice_client.py`.
- Removed the import shim and updated tests, examples, CLI, README, and skill references to import `green_invoice_client` directly.
- Added editable-install metadata through `pyproject.toml` so `from green_invoice_client import GreenInvoiceClient` works after `python -m pip install -e .`.
- Added `requirements-dev.txt` with `pytest-asyncio` for async test execution.
- Rewrote the README quick-start email flow to extract the created document id with `jq` instead of hardcoding a sample id.
- Refactored runnable examples to read credentials from environment variables, accept `--env sandbox|production`, and print formatted JSON.
- Added verification, branding-audit, and Hebrew QA logs.
- Removed remaining neutralization issues found by the branding scan.

### Changed

- Bumped metadata version to 1.4.1.
- Clarified that live documentation validation must be re-run in an environment with web access.
- Updated Hebrew terminology for consistent use of וובהוק, לוח הבקרה, סביבת בדיקות, רשימת בדיקה, שע״מ, מע״מ, and DD/MM/YYYY examples.

## [1.4.0] - 2026-05-31

### Added

- Expanded English skill guide with authentication, document selection, payment selection, SHAAM allocation diagnostics, edge cases, troubleshooting, production checklist, and anti-patterns.
- Expanded Hebrew skill guide with professional Israeli bookkeeping terminology, localized examples, DD/MM/YYYY context, and Hebrew troubleshooting phrases.
- Added Mermaid decision trees for document type selection, payment type selection, SHAAM allocation requirements, and error recovery.
- Added complete end-to-end workflow examples with full request and response payloads.
- Expanded API reference into an endpoint catalogue with request examples, response examples, parameter tables, response field tables, pagination semantics, error-code handling, and webhook event tables.
- Expanded document workflow guide to cover all 13 document types and common lifecycles.
- Added standalone troubleshooting guide with symptom-diagnosis-fix tables, Hebrew error string explanations, and diagnostic curl snippets.
- Added sandbox test scenario guide with more than 20 concrete scenarios.
- Added migration checklist for teams moving from manual issuance or another invoicing provider.
- Added typed Python API client with sync and async methods, JWT refresh, retry with exponential backoff and jitter, Retry-After handling, structured logging, and webhook signature verification.
- Added command line interface for auth, clients, documents, items, payments, webhooks, and expenses.
- Added pytest suite with mocked transports for authentication, token refresh, document types, endpoint paths, pagination, errors, retries, async methods, payments, and webhook signatures.
- Added runnable examples for tax invoice-receipt, credit note refund, foreign-currency export, deposit receipt, webhook verification, and async document search.
- Added README with installation, quick start, CLI usage, tests, and file index.
- Added generic MIT License file.

### Changed

- Bumped metadata version to 1.4.0.
- Expanded metadata tags in Hebrew and English.
- Updated metadata descriptions to mention troubleshooting, CLI, examples, async client, and tests.
- Rewrote content in neutral imperative voice.
- Removed non-neutral attribution and distribution references.
- Removed author metadata.

### Security

- Documented secret-handling rules for API keys, bearer tokens, bank details, and card numbers.
- Added constant-time HMAC webhook signature verification helper.
- Added guidance to avoid replaying document creation after ambiguous network failures without reconciliation.
