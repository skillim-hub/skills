# Migration Checklist

## Cleanup

- [ ] Remove branding, badges, logos, banners, and personal credits.
- [ ] Remove promotional language.
- [ ] Keep neutral imperative instructions.
- [ ] Keep the license notice as required.
- [ ] Delete image references unless they are necessary and privacy-safe.

## Privacy

- [ ] Remove password and one-time-code fields.
- [ ] Remove default full ID-number fields.
- [ ] Split logistics records from medical records.
- [ ] Mask phone numbers and ID numbers in shared outputs.
- [ ] Delete old screenshots with unrelated medical data.
- [ ] Define retention and deletion rules.
- [ ] Add consent status.

## Data model

Recommended fields:

```yaml
case_id:
created_at:
patient_alias:
consent_confirmed:
kupat_cholim:
medication_name:
strength_form:
supply_days:
repeats_left:
valid_until:
last_dispensed:
preferred_fulfillment:
pharmacy:
urgency:
recommended_path:
status:
confirmation_number:
follow_up_date:
price_nis:
privacy_flags:
notes_minimized:
```

Avoid fields:

```yaml
portal_password:
otp:
full_id_number:
diagnosis:
full_prescription_file:
payment_card:
```

## Operations

- [ ] Replace portal automation with human-in-the-loop drafting.
- [ ] Add manual review before sending messages.
- [ ] Add urgent escalation routes.
- [ ] Add pharmacy stock, delivery, price, cold-chain, and pickup checks.
- [ ] Add caregiver, child, travel, holiday, stock-out, and controlled-medication scenarios.
- [ ] Run tests.
- [ ] Compile Python scripts.
- [ ] Package the final directory as a zip.


## Web-validation migration notes

- [ ] Replace any unconditional Be prescription-delivery step with a branch/app verification step.
- [ ] Replace any unconditional Newpharm prescription-delivery step with licensed-pharmacy verification.
- [ ] Keep provider fees as reference-only values and verify them before payment.
- [ ] Do not add public endpoint paths or webhook event names unless a provider supplies official documentation.
