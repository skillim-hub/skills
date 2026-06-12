# Changelog

All notable changes are documented here. The format follows Keep a Changelog and semantic versioning.



## [2.1.0] - 2026-06-04

### Added
- Web-validated `references/verification-log.md` with two-pass validation, snippets, URLs, and access date.
- VAT context note confirming the general Israeli VAT rate as 18% from 01/01/2025 while avoiding tax-calculation logic.
- Hazardous-materials permit and fee-caution note for businesses that deal with poisons or hazardous substances.
- README web-validation section.

### Changed
- Hostile aircraft guidance now follows the double-confirmed 10-minute rule unless another alert or explicit official instruction is received.
- Radiological guidance now defers to official emergency and medical authorities instead of listing unsupported self-help procedures.
- Metadata version bumped to 2.1.0.

### Verified
- ✓✓ VAT general rate: Added web-validated VAT note; no CLI tax calculation was added.
- ✓✓ VAT order effective date: Documented 18% from 01/01/2025 as contextual reference only.
- ✓✓ Emergency numbers 100/101/102/104: No change required.
- ✓✓ Municipality 106 and Home Front Command 104: No change required.
- ✓✓ Home Front Command alert channels: No change required.
- ✓✓ Rocket/missile protected-space action: No change required.
- ✓✓ Standard rocket/missile 10-minute stay: No change required for ordinary rocket/missile wording.
- ✓✓ Ballistic/large-scale missile explicit release: No change required.
- ✗→✓ Hostile aircraft / drone alert stay time: Corrected SKILL.md, SKILL_HE.md, client, changelog, and tests.
- ✓✓ Earthquake behavior: No change required.
- ✓✓ Earthquake mamad door/window open: No change required.
- ✓✓ Tsunami coastal evacuation: No change required.
- ✓✓ Tsunami vertical evacuation: No change required.
- ✓✓ Hazardous-materials shelter-in-place behavior: No change required.
- ✓✓ Hazardous-substances permit awareness: Added permit/rate/form caution to api-reference.
- ✓✓ Poisons permit form and fee handling: Confirmed no fee calculation should be included.
- ✓✓ Traffic behavior during siren: No change required.
- ✓✓ Terrorist infiltration instructions: No change required; municipal page used as second-pass operational confirmation.
- ✗→✓ Radiological detailed public behavior: Corrected package to remove unsupported detailed radiological self-help steps.
- ✓✓ Home Front Command public API endpoints and webhooks: Kept package explicitly offline; no endpoint or webhook reference added.

## [2.0.1] - 2026-06-04

### Added
- Branding, attribution, visual-asset and badge, and emoji audit report.
- Hebrew QA log covering terminology, localization, neutral voice, and no-nikud review.
- Installable Python module `disaster_preparedness_guide`.
- CLI create/review chain so a plan id from a create response can be used in the next step.

### Changed
- Replaced the hyphenated client script with `scripts/disaster_preparedness_guide_client.py`.
- Updated README install flow to `pip install -e .` and development requirements.
- Updated examples to read environment variables, accept `--env sandbox|production`, and emit JSON with `ensure_ascii=False`.
- Localized Hebrew dates to DD/MM/YYYY and reduced unnecessary Anglicisms.

### Fixed
- Public Markdown audit confirmed no badges, visual-asset references, attribution metadata, GitHub handles, or public emoji.
- Syntax check added with `python -m compileall scripts/ -q`.

## [2.0.0] - 2026-06-04

### Added
- Comprehensive English and Hebrew guides.
- Decision trees, examples, edge cases, troubleshooting, anti-patterns, and production checklist.
- Official-channel/regulation reference for a non-API skill.
- Workflow guide, troubleshooting guide, test scenarios, and migration checklist.
- Typed offline sync/async helper, Click CLI, pytest suite, and examples.
- README, MIT LICENSE, pyproject, and development requirements.

### Changed
- Skill identity changed to `disaster-preparedness-guide`.
- Expanded coverage for small businesses, freelancers, consumers, accessibility, records, and reopening.
- Clarified official-instructions override.

### Removed
- Attribution metadata, visual marks and badges, image references, decorative images, and distribution callouts.
- Any claim of live alert API access.

## [1.0.0] - 2026-05-29

### Added
- Initial emergency protocol notes and lookup behavior.
