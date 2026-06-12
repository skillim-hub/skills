# Changelog

All notable changes to this skill package are documented in this file.

The format follows Keep a Changelog, and versioning follows Semantic Versioning.



## [1.2.0] - 2026-06-03

### Added

- `references/verification-log.md` with pass 1 and skeptical pass 2 source columns, short source quotes, access date, status tags, and summary counts.
- Live-verified provider notes for PayPlus, Cardcom, Tranzila, Grow Payments, and YabandPay / YaadPay.
- Explicit current Israeli VAT-rate note: 18% from 01/01/2025, subject to accountant review for actual reward treatment.
- Gateway adapter aliases for legacy provider names: `meshulam` maps to `grow`, and `yaadpay` maps to `yabandpay`.

### Changed

- Updated package metadata and Python project version to `1.2.0`.
- Clarified that generic internal refund examples are not provider endpoint paths.
- Replaced Meshulam-only wording with Grow Payments (formerly Meshulam).
- Replaced Yaad Sarig / YaadPay wording with YabandPay / YaadPay and public-doc caveats.
- Added verified PayPlus endpoint and header examples.

### Verification findings

- ✗→✓ Current Israeli VAT rate: Added explicit 18% VAT note in English and Hebrew docs and API reference.
- ✓✓ VAT transition date: No conflicting package content found; VAT note now carries the date.
- ✓✓ Withholding tax confirmations: Kept cash-payout withholding controls.
- ✓✓ Tax invoice allocation fields: Kept accounting-document guidance; added verified fields in API reference.
- ✓✓ Privacy authority role: Kept privacy, consent, retention, and data-minimization controls.
- ✓✓ Privacy Amendment 13 notification threshold: Added reference that large sensitive databases may trigger notification duties.
- ✓✓ Spam Law / Communications Law Section 30A: Kept marketing consent and opt-out guidance.
- ✓✓ Consumer-protection anti-misleading rule: Kept requirement to publish clear terms, exclusions, caps, expiry, and reversals.
- ✓✓ Bank of Israel payment-systems terminology: Kept Bank of Israel terminology and official English terminology.
- ✓✓ SHVA / Ashrait payment-card services: Kept SHVA as infrastructure reference, not a reward-payout API.
- ✗→✓ PayPlus refund endpoint: Added verified PayPlus endpoint and headers; clarified generic internal endpoints are not provider endpoints.
- ✓✓ PayPlus callback behavior: Kept callback/webhook verification requirements and added PayPlus callback note.
- ✓✓ Cardcom refund/token behavior: Added Cardcom-specific notes for POST, URL encoding, and Name-to-Value responses.
- ✓✓ Tranzila authentication/refund: Added HMAC/access-token note and kept terminal-level permission warnings.
- ✗→✓ Grow Payments naming: Replaced Meshulam-only references with Grow Payments (formerly Meshulam).
- ✗→✓ Grow webhook event names: Removed implication that fixed event names are available; require account-specific verification.
- ✗→✓ YabandPay / YaadPay public docs: Replaced Yaad Sarig / YaadPay wording with YabandPay / YaadPay and public-doc caveats.
- ✓✓ YabandPay portal refunds: Kept manual/portal fallback guidance where API refund availability must be verified.
- ✓✓ Referral-program function claim: Kept core package description; legal/payment claims remain Israel-source validated.


## [1.1.0] - 2026-06-03

### Added

- Branding and visual-reference audit report under `references/branding-audit.md`.
- Hebrew QA log under `references/hebrew-qa-log.md`.
- Installable `referral_program_manager` Python package under `src/`.
- JSON-output CLI responses for easier shell chaining.
- Environment-aware runnable examples with `--env sandbox|production`.
- `pytest-asyncio` development dependency.
- Syntax validation through `compileall`.

### Changed

- Replaced hyphenated client implementation file with an underscored helper and installable package module.
- Updated README quick start to extract identifiers from JSON responses and feed them into later commands.
- Updated Hebrew localization to use ₪ and DD/MM/YYYY date examples.
- Refined Hebrew terminology to reduce avoidable English loanwords.
- Bumped package and metadata version to `1.1.0`.

### Removed

- Hyphenated Python client implementation path that required path-based loading.

## [1.0.0] - 2026-06-03

### Added

- Comprehensive English guide.
- Comprehensive Hebrew guide with Israeli business terminology.
- Israeli payment-gateway and regulation reference.
- Workflow guide, troubleshooting guide, test scenarios, and migration checklist.
- Typed sync and async Python client.
- Typer CLI.
- Pytest suite with more than 20 tests.
- Five runnable examples.
- MIT license with neutral copyright notice.
- Python packaging metadata and development dependencies.

### Changed

- Replaced stub content with production-ready operating guidance.
- Bumped metadata version from `0.1.0` to `1.0.0`.
- Expanded tags and localization metadata.

### Removed

- Non-neutral package markers and presentation artifacts from the stub lineage.

## [0.1.0] - 2026-06-03

### Added

- Initial stub package.
