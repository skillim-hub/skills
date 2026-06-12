# Workflow Guide

## Workflow 1: Intake

Trigger: a paper notice, email, SMS, leasing-company invoice, toll notice, or collection letter arrives.

Steps:

1. Save the original notice.
2. Create `YYYYMMDD-vehicle-notice` case ID.
3. Normalize vehicle number.
4. Classify issuer type.
5. Record amount, notice date, due date, and source.
6. Add a calendar reminder.
7. Move to issuer-specific verification.

Output: register row, case folder, next action, owner.

## Workflow 2: Municipal parking fine

1. Open the municipality's official payment or appeal portal.
2. Enter vehicle number and notice number.
3. Enter ID/company number only when required.
4. Compare vehicle, notice, amount, date, location, status.
5. Save result page.
6. Update status.
7. Continue to payment approval, appeal, or transfer review.

Acceptance criteria: official result saved, amount reconciled, due date recorded.

## Workflow 3: Parking-app evidence

1. Collect receipt from Pango, Cello, meter, or approved service.
2. Confirm same vehicle, city, zone, and enforcement time.
3. Confirm the session was active and not refunded.
4. Prepare concise cancellation request.
5. Attach receipt and notice.
6. Submit through official channel.
7. Save confirmation and set reminder.

## Workflow 4: Company vehicle driver identification

1. Identify vehicle custodian at offense time.
2. Review dispatch logs, calendar, GPS, fuel card, parking app, and vehicle assignment.
3. Ask likely driver for confirmation.
4. Decide: transfer, company pays, contest, or escalate.
5. Document decision.

## Workflow 5: Liability transfer

1. Confirm transfer is available for the fine type.
2. Check deadline.
3. Collect driver details and declaration where required.
4. Attach assignment records.
5. Submit through official channel.
6. Save confirmation.
7. Track result.

## Workflow 6: Payment approval

1. Verify official source.
2. Confirm amount and deadline.
3. Confirm not already paid.
4. Apply approval threshold: ₪250, ₪500, ₪1,000 or internal policy.
5. Generate memo.
6. Pay through official channel.
7. Save receipt.
8. Update register and accounting category.

## Workflow 7: Toll-road notice

1. Verify toll operator.
2. Request trip itemization.
3. Split principal toll, enforcement fee, collection cost, and leasing admin fee.
4. Compare trip dates with business records.
5. Check subscription or transponder.
6. Pay or contest.
7. Store receipt and trip list.

## Workflow 8: Collection-stage case

1. Identify original issuer.
2. Request itemized breakdown.
3. Verify original fine.
4. Check notices, dates, and delivery.
5. Escalate urgent enforcement documents.
6. Pay only if payment closes the underlying case.
7. Save closure confirmation.

## Workflow 9: Duplicate payment prevention

1. Search register by vehicle and notice.
2. Search bank/card transactions.
3. Ask employee or leasing company for receipts.
4. Check official portal status.
5. Mark `duplicate_payment_risk`.
6. Pay only after reconciliation.

## Workflow 10: Month-end reconciliation

1. Export register.
2. Export bank/card transactions.
3. Match by amount, issuer, date, notice.
4. Confirm every paid case has receipt.
5. Confirm every open case has a reminder.
6. Review accounting classifications.
7. Report paid, open, overdue, appeal, collection, and duplicate-risk cases.

## Workflow 11: Sold vehicle

1. Collect sale agreement and ownership-transfer proof.
2. Compare offense date/time with transfer date/time.
3. Verify registered owner at offense time.
4. Submit cancellation or transfer request.
5. Track response.

## Workflow 12: Consumer one-off case

1. Identify issuer.
2. Use official portal.
3. Verify vehicle, notice, amount, and due date.
4. Check contest evidence.
5. Pay or submit request.
6. Save receipt or confirmation.



## Source-specific deadline rule

Do not copy a deadline from one issuer to another. The web validation found Tel Aviv-specific deadlines for cancellation, conversion to court hearing, and transfer requests, and a separate Fast Lane appeal deadline. Treat every deadline as issuer-specific and notice-specific until confirmed on the current official page or on the notice itself.
