# End-to-end workflow guide

## Workflow 1: Adult passport renewal

Use when an adult needs a new or renewed passport.

1. Classify as `passport_renewal`.
2. Validate Teudat Zehut and Israeli phone.
3. Ask whether the current passport is available.
4. Build a city/date/time preference.
5. Direct the user to the official appointment channel.
6. Record only non-secret confirmation details.
7. Generate a calendar reminder and arrival checklist.

Checklist: Teudat Zehut, current passport if available, appointment confirmation, payment method if required, printed confirmation for SMS problems.

Done criteria: official confirmation exists, calendar reminder exists, required documents are listed, no password/OTP/payment/biometric data was stored.

## Workflow 2: First Teudat Zehut for a minor

Use for first identity card issuance, often around age 16.

1. Confirm the applicant is a minor.
2. Add parent/guardian checklist.
3. Verify whether both parent and minor must attend under current official guidance.
4. Prepare relationship or guardianship documentation only if required.
5. Book through the official channel.
6. Add reminders for school, exams, travel, or work deadlines.

Edge handling: divorced/separated parents, one parent abroad, guardianship orders, and court documents require official guidance. Do not provide custody legal advice.

## Workflow 3: Lost or stolen Teudat Zehut

1. Classify as `id_lost_stolen`.
2. Ask whether there is suspected misuse.
3. Prepare official loss/theft/damage checklist.
4. Search earliest official slot within an acceptable radius.
5. Add business-impact notes for bank KYC, payroll, supplier onboarding, invoices, and digital signature.
6. After replacement, update dependent records.

Post-receipt list: bank, accountant or bookkeeper, payroll or invoicing platform, digital signature provider, insurance or pension administrator, and any government business portals that depend on identity verification.

## Workflow 4: Urgent passport before travel

1. Ask for departure date.
2. Ask for current passport status.
3. Ask whether the traveler is a minor.
4. Mark urgent when travel is within 30 days.
5. Use official urgent guidance only.
6. Rank the earliest official slots first.
7. Never guarantee issuance, boarding eligibility, or processing time.

Output template:

```markdown
Urgency: travel on 15/08/2026
Risk: appointment availability and issuance time are not guaranteed.
Recommended action: use official urgent guidance and book the earliest eligible appointment through the official channel.
Bring: Teudat Zehut, current passport if available, travel proof if official guidance requires it.
```

## Workflow 5: Family passport appointments

1. Create one row per applicant.
2. Mark minors.
3. Build a per-person checklist.
4. Check whether one slot per applicant is required.
5. Avoid overlapping appointments when the same guardian must attend.
6. Prefer the same bureau, adjacent times, and enough buffer.

Example planning table:

| Applicant | Service | Minor | Special requirement |
|---|---|---:|---|
| Parent 1 | `passport_renewal` | No | Current passport |
| Child 1 | `passport_new` | Yes | Parent/guardian consent |
| Child 2 | `passport_renewal` | Yes | Parent/guardian consent + current passport |

## Workflow 6: Freelancer or small-business owner

1. Keep the process personal.
2. Identify business deadline: bank, accountant, tender, payroll, digital signature, supplier verification.
3. Prepare earliest official appointment plan.
4. Add a post-appointment update checklist.
5. Avoid storing full ID numbers in shared business files.

## Workflow 7: Employee needs valid ID

1. Treat appointment as the employee’s personal government process.
2. Do not collect the employee’s government login, password, OTP, or payment details.
3. Provide employee-facing instructions and deadline plan.
4. Store only employment records that the business has a lawful basis to keep.
5. Mask ID in shared task trackers.

## Workflow 8: Address update

1. Check whether online service is sufficient.
2. If online service is enough, do not schedule an appointment.
3. If in-person service is required, classify as `address_update`.
4. Prepare proof of address only as instructed by the official page.
5. Remind the user that address changes can affect mail, banks, municipal notices, business licensing, and official letters.

## Workflow 9: Name or personal-status update

1. Identify the basis: marriage, divorce, court order, or other civil-status change.
2. Add official civil-status documents to the checklist.
3. Check whether both passport and ID must be updated.
4. Schedule the relevant Population and Immigration Authority service.
5. Add downstream updates: bank, accountant, payroll, Tax Authority account, National Insurance account, health fund, digital signature provider, business licenses, and registry records.

## Workflow 10: Accessibility-first booking

1. Record accessibility need without collecting unnecessary medical details.
2. Prefer accessible bureaus and times with arrival buffer.
3. Verify branch accessibility from official sources.
4. Add companion and printed-confirmation notes if useful.
5. Avoid unverified parking or transportation claims.

## Workflow 11: Rebooking or cancellation

1. Ask for non-secret confirmation details only.
2. Search for a replacement before canceling if the deadline is close.
3. Keep the old appointment until a better replacement is confirmed.
4. Cancel unneeded duplicates through the official channel.
5. Update reminders and checklists.
