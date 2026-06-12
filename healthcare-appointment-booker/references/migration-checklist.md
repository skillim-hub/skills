# Migration Checklist

## Inventory

- [ ] List current templates and appointment notes.
- [ ] Find any stored ID numbers, passwords, SMS codes, or medical files.
- [ ] Find scraping, automated login, slot polling, or CAPTCHA handling.
- [ ] Identify supported HMOs and unsupported providers.
- [ ] Identify retention periods and access permissions.

## Remove unsafe behavior

- [ ] Remove credential collection.
- [ ] Remove SMS/OTP handling.
- [ ] Remove scraping and queue bypass.
- [ ] Remove diagnosis logic.
- [ ] Remove unnecessary medical-history storage.
- [ ] Replace unofficial phone numbers with official-channel verification.

## Data migration

- [ ] Convert diagnoses to broad service categories where possible.
- [ ] Redact ID numbers.
- [ ] Keep confirmation numbers only when needed.
- [ ] Add retention delete date.
- [ ] Encrypt retained records.
- [ ] Confirm caregiver/client consent records.

## Workflow migration

- [ ] Add urgency screening before every booking.
- [ ] Add HMO enum.
- [ ] Add specialty mapping.
- [ ] Add referral/order status.
- [ ] Add language and accessibility fields.
- [ ] Add no-availability fallback.
- [ ] Add cancellation/reschedule workflow.
- [ ] Add paid-service disclosure where relevant.

## Hebrew localization

- [ ] Use DD/MM/YYYY.
- [ ] Use ₪ for pricing.
- [ ] Use הפניה, התחייבות, טופס 17, מכון שבהסדר, מוקד רפואה דחופה.
- [ ] Avoid unnecessary transliteration.
- [ ] Use natural forms such as מבקש/ת and צריך/ה where suitable.
- [ ] Review wording with an Israeli operations reviewer.

## Client and CLI

- [ ] Validate dates.
- [ ] Validate HMO values.
- [ ] Screen emergency red flags.
- [ ] Keep adapter boundary for authorized channels only.
- [ ] Add JSON and text outputs.
- [ ] Run pytest with at least 20 tests.

## Production

- [ ] Verify official HMO contacts.
- [ ] Verify privacy and healthcare requirements.
- [ ] Document retention and deletion.
- [ ] Train staff on privacy and escalation.
- [ ] Run all scenarios.
- [ ] Publish changelog.
