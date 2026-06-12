# Migration checklist

## Scope migration

- [ ] Rename skill slug to `passport-id-scheduler`.
- [ ] Remove unrelated tax, National Insurance, and company-registration workflows unless used only for downstream identity-document updates.
- [ ] Keep passport, Teudat Zehut, biometric, address, name/status, urgent travel, minor, accessibility, and family scheduling flows.
- [ ] Replace generic form-filling language with appointment planning and official-channel language.
- [ ] Remove browser automation instructions that could bypass safeguards.
- [ ] Remove CAPTCHA, queue, session, credential, OTP, and payment automation.
- [ ] Replace “submit form” with “prepare data and complete final booking through the official channel.”

## Metadata and files

- [ ] Remove branding.
- [ ] Remove visual assets and visual references.
- [ ] Keep contributor fields out of `metadata.json`.
- [ ] Use the neutral MIT license text from `LICENSE`.
- [ ] Bump version to `2.0.0` or later.
- [ ] Expand tags around passport, identity, biometric, Israeli appointments, small businesses, freelancers, and privacy.

## Data model migration

- [ ] Replace generic form records with `ApplicantProfile`.
- [ ] Replace form type with `ServiceType`.
- [ ] Add `AppointmentPreference`.
- [ ] Add `AppointmentCandidate` ranking.
- [ ] Add `urgent_travel_date`.
- [ ] Add `is_minor` and guardian flags.
- [ ] Add `accessibility_required`.
- [ ] Add ID masking helpers.

## CLI migration

- [ ] Add `validate-id`.
- [ ] Add `normalize-phone`.
- [ ] Add `classify`.
- [ ] Add `plan`.
- [ ] Add `rank-slots`.
- [ ] Add `checklist`.
- [ ] Add `make-ics`.
- [ ] Ensure JSON input/output works.
- [ ] Ensure Hebrew output works.
- [ ] Keep all commands local and safe.

## Testing migration

- [ ] Add at least 20 pytest tests.
- [ ] Test ID validation, including leading zeros and all-zero rejection.
- [ ] Test phone normalization.
- [ ] Test service classification.
- [ ] Test minor workflow.
- [ ] Test urgent travel workflow.
- [ ] Test appointment ranking.
- [ ] Test duplicate handling.
- [ ] Test unsafe source rejection.
- [ ] Test calendar export.
- [ ] Test CLI smoke commands.

## Documentation migration

- [ ] Create comprehensive `SKILL.md`.
- [ ] Create natural Hebrew `SKILL_HE.md`.
- [ ] Create `references/api-reference.md`.
- [ ] Create `references/workflow-guide.md`.
- [ ] Create `references/troubleshooting.md`.
- [ ] Create `references/test-scenarios.md`.
- [ ] Create `references/migration-checklist.md`.
- [ ] Add `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, and `requirements-dev.txt`.

## Production migration

- [ ] Verify official URLs and current requirements.
- [ ] Verify privacy obligations.
- [ ] Review business handling of employee ID data.
- [ ] Add retention policy.
- [ ] Mask sensitive logs.
- [ ] Confirm accessibility support path.
- [ ] Confirm manual fallback path if official appointment systems are unavailable.
