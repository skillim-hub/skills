# Workflow Guide

Use these workflows to move from intake to a review-ready Israeli lease draft.

## Workflow 1: Standard apartment lease

1. Collect landlord and tenant details.
2. Verify property address, city, and registry details if available.
3. Enter start date and end date in DD/MM/YYYY.
4. Enter monthly rent in ₪.
5. Calculate security and compare it to the common residential cap when coverage likely applies.
6. Add handover protocol, meter readings, keys, photographs, and inventory.
7. Add repair timing for urgent and ordinary defects.
8. Add balanced early termination language.
9. Export Markdown and send for legal review.

Example command:

```bash
lease-agreement-drafter draft --env sandbox --input scripts/examples/apartment_standard_input.json --output apartment-draft.md
```

## Workflow 2: Apartment with high security request

1. Run the draft with the requested security amount.
2. Review `RESIDENTIAL_DEPOSIT_CAP` warnings.
3. Reduce the amount when the lease appears covered by residential protections.
4. If the landlord insists on a higher amount, mark the issue for legal review and do not present the draft as compliant.
5. Keep proof of the final negotiated amount.

## Workflow 3: Furnished apartment

1. Add `furnished: true` in the property object.
2. Attach inventory with item condition, serial numbers when useful, and photos.
3. Separate ordinary wear from tenant-caused damage.
4. Add a return protocol matching the handover protocol.
5. Avoid charging replacement value for ordinary depreciation.

## Workflow 4: Apartment with pets

1. Ask whether pets are allowed, restricted, or prohibited.
2. Permit assistance animals when law requires accommodation.
3. Add cleaning, nuisance, damage, and building-rule obligations.
4. Avoid arbitrary penalties.
5. Do not use pet rules to override mandatory housing rights.

## Workflow 5: Small office for freelancer

1. Define permitted use precisely.
2. Confirm VAT treatment and tax invoice wording.
3. Allocate arnona, electricity, water, internet, parking, signage, and management fees.
4. Add access hours, keys, building rules, and shared area obligations.
5. Add professional liability and property insurance where relevant.
6. Check business license and accessibility implications.

## Workflow 6: Office fit-out before entry

1. Attach plans and written approval process.
2. Define who pays for works, permits, supervision, and restoration.
3. Require contractor insurance and compliance with building rules.
4. Set milestone dates and consequences for delay.
5. Add final inspection before rent commencement if negotiated.

## Workflow 7: Renewal or option exercise

1. Confirm option length and notice deadline.
2. Check whether rent adjustment, index linkage, or VAT changes apply.
3. Confirm no uncured material breach.
4. Require written notice of exercise.
5. Issue an amendment rather than editing the signed original without tracking changes.

## Workflow 8: Early exit

1. Read the early termination clause.
2. Check whether rights are mutual and whether notice was delivered correctly.
3. Calculate rent, utilities, management fees, and repairs through the exit date.
4. Inspect the property and update the return protocol.
5. Release or draw security only according to documented debt or damage.

## Workflow 9: Landlord template audit

1. Paste or load the landlord template.
2. Run `scan_template` or the CLI `audit` command.
3. Add missing repair, handover, and balanced termination clauses.
4. Review security, VAT, waiver, penalty, and unilateral-change clauses manually.
5. Produce a marked issue list for negotiation.

## Workflow 10: Production handoff

1. Save draft Markdown and JSON response.
2. Save all findings and checklist items.
3. Attach supporting documents.
4. Send unresolved issues to a professional reviewer.
5. Use a final PDF or signed document only after all open points are resolved.
