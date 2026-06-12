# Troubleshooting Guide

Use this guide when a travel request cannot proceed normally or a traveler reports an issue.

## Triage checklist

1. Identify status: quote, pending payment, booked, cancelled, failed, or unknown.
2. Collect supplier, booking reference, traveler name, dates, and channel.
3. Classify issue: availability, price, payment, document, flight, rail, hotel, cancellation, refund, or currency.
4. Check whether a time deadline exists.
5. Preserve evidence: confirmation email, payment receipt, invoice, screenshot, supplier message.
6. Avoid collecting full card number, passport scan, OTP, or password.

## Common issues

### Offer expired

Symptoms: price no longer appears, API returns `OFFER_EXPIRED`, or supplier cart resets.

Resolution:

1. Re-run search.
2. Compare old and new prices.
3. Mark old quote as expired.
4. Request approval for any increase.
5. Do not book automatically.

### Rate changed

Symptoms: hotel or flight price changes at payment, or supplier returns `RATE_CHANGED`.

Resolution: stop payment, recalculate total in ₪, update cancellation and baggage details, request approval.

### Payment authorization failed

Resolution:

1. Ask whether a 3D Secure screen appeared.
2. Ask for card issuer country and card type only.
3. Check whether foreign transactions are enabled.
4. Verify amount and currency.
5. Avoid repeated retries.
6. Ask supplier whether an authorization hold exists.

### Duplicate charge

Resolution:

1. Record both dates, amounts, currencies, and supplier descriptors.
2. Determine authorization versus capture.
3. Ask supplier for payment ledger.
4. Track expected release/refund date.
5. Warn that FX differences may remain after refund.

### Missing Israeli VAT invoice

Resolution:

1. Confirm whether supplier is Israeli.
2. Request חשבונית מס/קבלה after payment.
3. Provide business details supplied by the user.
4. If supplier is foreign, record foreign invoice and ask accountant to review treatment.
5. Do not promise VAT input deduction.

### Wrong passenger name

Resolution: stop ticketing if possible, compare with passport Latin spelling, ask airline/supplier for correction fee and rules, never assume name correction is free, reissue only after approval.

### Baggage missing

Resolution: check fare rules, add checked-bag price, compare against a fare family including baggage, update total and approval summary.

### Hotel cannot confirm late check-in

Resolution: send late-arrival request, ask for written confirmation, add emergency contact, consider alternative property if no response.

### Train disruption

Resolution: check official rail or transit source, add bus/taxi fallback, recalculate arrival time, warn if itinerary connects to flight.

### Currency mismatch

Resolution: record supplier currency, ask whether dynamic currency conversion was selected, compare supplier conversion versus card conversion, show estimate until settlement posts.

### Refund lower than expected

Resolution: compare original charge, cancellation policy, and refund transaction; separate supplier penalty from FX/card effects; ask supplier for refund breakdown; store both charge and refund exchange evidence.

## Error catalog

| Error code | User-facing message | Action |
|---|---|---|
| INVALID_DATE_RANGE | תאריך הסיום קודם לתאריך ההתחלה. | Ask for corrected dates. |
| MISSING_TRAVELER | חסר מספר נוסעים. | Require at least one traveler. |
| MISSING_PASSPORT_PROMPT | נסיעה לחו״ל דורשת בדיקת דרכון. | Ask for nationality and expiry month/year. |
| FX_RATE_MISSING | חסר שער מטבע מתועד. | Fetch approved rate or mark estimate. |
| OFFER_EXPIRED | הצעת המחיר פגה. | Re-price before approval. |
| PAYMENT_RETRY_BLOCKED | אין לבצע ניסיון חיוב חוזר ללא בדיקה. | Pause and verify. |
| INVOICE_TYPE_UNKNOWN | סוג המסמך החשבונאי לא ברור. | Request document copy or supplier clarification. |
| SEPARATE_TICKET_RISK | המסלול כולל כרטיסים נפרדים. | Add warning and protected alternative. |
| LOCAL_TAX_UNCONFIRMED | מס מקומי לא אומת. | Mark local payment risk. |
| SUPPLIER_TERMS_UNVERIFIED | תנאי הספק לא אומתו. | Keep status as quote only. |

## Escalation templates

### Airline schedule change

```text
Subject: Assistance required for schedule change - booking {booking_reference}

Please provide the available options for booking {booking_reference}.
Include free rebooking options, refund eligibility, baggage impact, and deadline for selecting an option.
```

### Hotel invoice request in Hebrew

```text
שלום,
אבקש לקבל חשבונית מס/קבלה עבור הזמנה {booking_reference}.
החיוב בוצע בתאריך {payment_date} בסך {amount}.
נא לשלוח את המסמך לכתובת {email}.
תודה.
```

### Refund follow-up

```text
Subject: Refund status request - booking {booking_reference}

Please confirm refund amount, refund currency, processing date, cancellation fee, and expected posting date.
Attach the refund receipt or transaction reference.
```

## Production monitoring

Track quote-to-book conversion failures, expired offers, supplier error rates, payment authorization failures, missing invoice cases, FX estimate versus settlement variance, manual approval delays, cancellation requests near deadline, and Hebrew parsing errors for dates and station names.

## Safe fallback

```markdown
Status: Cannot verify live availability.
Action required: Check supplier directly before payment.
Current estimate: Based on provided or cached data only.
Risk: Price, schedule, cancellation, and currency may change.
```
