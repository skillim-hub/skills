# Workflow Guide

Use these end-to-end workflows as operating procedures. Replace sample dates and names with verified customer details.

## Workflow 1: consumer renewal

1. Record customer consent.
2. Validate Israeli ID and phone.
3. Enter expiry date as DD/MM/YYYY in the customer file and ISO date in the CLI.
4. Run readiness check.
5. If ready, open the official renewal service and complete identity verification.
6. Pay official fee in ₪ only through the official driver-license payment page. Use `https://ecom.gov.il/voucherspa/input/209` for driver-license payment handoff.
7. Save receipt number and confirmation number.
8. Schedule next reminder.

CLI:

```bash
driving-license-booker readiness   --env sandbox   --name "Dana Levi"   --national-id 039456785   --phone 0501234567   --license-number 1234567   --expiry-date 2026-08-31   --not-paid   --medical-required
```

## Workflow 2: freelancer with expiring license

1. Ask whether the freelancer drives for income, deliveries, client visits, or regulated work.
2. Mark the license as business-critical.
3. Create renewal record and add a reminder seven business days before expiry.
4. If renewal is blocked, prepare appointment in the nearest relevant city.
5. Record private service fee, VAT if applicable, and any official ₪ fee separately.

## Workflow 3: delivery business driver roster

1. Export active drivers from payroll or operations system.
2. Normalize phone numbers and validate ID checksums.
3. Create one record per driver; do not combine drivers into one request.
4. Track expiry date, license class, and role-critical status.
5. Review exceptions weekly.
6. Escalate expired or blocked licenses before scheduling shifts.

## Workflow 4: office appointment with accessibility need

1. Confirm that an office visit is required.
2. Record only the accessibility need needed for appointment logistics.
3. Search preferred city first, then nearby cities.
4. Save appointment reference and arrival instructions.
5. Send the customer a document checklist.
6. Review the appointment reminder two business days before the visit.

## Workflow 5: practical test coordination

1. Confirm candidate details and license class.
2. Collect at least two date windows.
3. Generate teacher message.
4. Wait for teacher confirmation.
5. Convert the local draft to confirmed only after the teacher confirms.
6. Add reminders for candidate documents, pickup city, and arrival time.

## Workflow 6: payment failure

1. Stop repeated payment attempts.
2. Check whether an official receipt exists.
3. If no receipt exists and no card charge appears, retry once through the official page.
4. If a card charge exists without receipt, document the date, amount in ₪, and reference shown by the card provider.
5. Escalate to the official payment support channel.

## Workflow 7: invalid customer data

1. Stop official handoff.
2. Read the exact invalid field back to the customer.
3. Re-enter the corrected detail.
4. Re-run local validation.
5. Keep the failed value only as short operational note if needed for audit.

## Workflow 8: renewal blocked by medical declaration

1. Mark renewal readiness as blocked.
2. Send the customer the official declaration path.
3. Avoid collecting medical details beyond completion status.
4. Re-check readiness after completion.
5. Continue renewal or prepare bureau appointment if still blocked.
