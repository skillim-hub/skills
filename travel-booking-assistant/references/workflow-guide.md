# Workflow Guide

This guide provides end-to-end workflows for common Israeli travel booking tasks.

## Workflow 1: Domestic Eilat business trip

### Scenario

A freelance consultant needs to travel from Tel Aviv to Eilat for a client workshop from 12/06/2026 to 14/06/2026 and needs documentation for bookkeeping.

### Steps

1. Create the travel brief.
2. Confirm whether the traveler needs to arrive before a specific meeting time.
3. Compare flight to Ramon plus transfer against car/bus alternatives.
4. Search hotel options by area and cancellation terms.
5. Request VAT invoice support from the Israeli hotel.
6. Calculate total in ₪.
7. Present a quote-only recommendation.
8. Ask for human approval before payment.
9. Store booking reference, invoice request, and receipt checklist.

### Example brief

```json
{
  "request_id": "tb-001",
  "locale": "he-IL",
  "trip_type": "domestic",
  "origin": "Tel Aviv",
  "destination": "Eilat",
  "start_date": "12/06/2026",
  "end_date": "14/06/2026",
  "travelers": [{"type": "adult", "count": 1}],
  "business": true,
  "needs_vat_invoice": true,
  "arrival_deadline": "12/06/2026 12:00",
  "bags": ["carry_on"]
}
```

### Output

```markdown
סטטוס: הצעת מחיר בלבד, לא בוצעה הזמנה.
המלצה: טיסה מנתב״ג לרמון בשעות הבוקר, מונית למלון בחוף הצפוני.
עלות משוערת: ₪1,740.
בדיקות לפני תשלום: כבודה, חשבונית מס למלון, מועד ביטול, העברה מרמון.
```

### Failure handling

- If flight inventory disappears, re-price and preserve the old quote as expired.
- If the hotel cannot issue a VAT invoice, flag it and offer another supplier.
- If arrival is near Shabbat or a holiday, add taxi fallback and check service gaps.

## Workflow 2: Israel Rail to airport

1. Collect flight departure time.
2. Decide required airport arrival buffer.
3. Search rail route by arrival time, not departure time.
4. Add transfer and platform-change buffers.
5. Check service disruptions, weekend, or holiday restrictions.
6. Provide taxi fallback.
7. Warn that rail delay does not protect the flight.

Output:

```markdown
Recommendation: Take the train that arrives at Ben Gurion Airport at least 3 hours before international departure.
Risk: A rail delay is not protected by the airline.
Fallback: Pre-book taxi from Haifa if the route is disrupted.
```

## Workflow 3: Outbound business flight and hotel

1. Collect passport name, passport expiry month/year, nationality, and trip dates.
2. Search flights with baggage included.
3. Search hotels near conference location.
4. Convert EUR costs to ₪ using a documented rate.
5. Add card markup estimate.
6. Add city tax and deposit notes.
7. Compare refundable and non-refundable options.
8. Generate approval summary.
9. After approval, book and store references.

Cost template:

```markdown
| Item | Supplier currency | Rate | ₪ estimate | Notes |
|---|---:|---:|---:|---|
| Flight | EUR 392.50 | 3.3365 | ₪1,309.58 | Checked bag not included |
| Hotel | EUR 520.00 | 3.3365 | ₪1,734.98 | City tax may be local |
| Card markup | ₪3,044.56 | 2.8% | ₪85.25 | Estimated |
| Total |  |  | ₪3,129.81 | Quote only |
```

## Workflow 4: Consumer hotel cancellation support

1. Ask for booking reference, supplier, and booking date.
2. Read cancellation policy from confirmation.
3. Identify free-cancellation deadline and penalty.
4. Check whether payment was already captured.
5. Prepare cancellation request to supplier.
6. Preserve confirmation and refund evidence.
7. Avoid final legal conclusions unless verified by a professional source.

Supplier message:

```text
Subject: Cancellation request for booking {booking_reference}

Please cancel booking {booking_reference} for {traveler_name}, check-in {date}.
Before processing, confirm the cancellation fee, refund amount, refund currency, and expected refund date.
Please send written confirmation.
```

## Workflow 5: Missing VAT invoice

1. Confirm supplier is an Israeli business.
2. Confirm payment was captured.
3. Request a חשבונית מס/קבלה with business details.
4. Provide legal business name, עוסק מורשה/ח.פ. number if supplied by user, and email.
5. Store supplier response.
6. If unavailable, flag for accountant review.

Hebrew supplier message:

```text
שלום,
אבקש לשלוח חשבונית מס/קבלה עבור הזמנה {booking_reference}.
פרטי העסק לחשבונית:
שם העסק: {business_name}
מספר עוסק/ח.פ.: {tax_id}
דוא״ל למשלוח: {email}

תודה.
```

## Workflow 6: Payment failed on foreign supplier

1. Do not ask for full card number.
2. Ask for card type, issuing country, and whether 3D Secure appeared.
3. Check supplier currency and payment method.
4. Try an alternative approved payment method if available.
5. Avoid repeated blind retries.
6. Re-price if the rate expires.
7. Confirm whether any authorization hold was created.

## Workflow 7: Duplicate charge investigation

1. Collect supplier name, booking reference, charge dates, currencies, and amounts.
2. Distinguish authorization hold from captured charge.
3. Ask supplier for payment ledger.
4. Ask card issuer if needed.
5. Do not classify the issue as fraud unless evidence supports it.
6. Track refund currency and exchange-rate variance.

## Workflow 8: Separate ticket connection

1. Mark the connection as separate-ticket risk.
2. Add baggage reclaim, immigration, security, and re-check-in buffers.
3. Compare against a protected single-ticket itinerary.
4. If separate tickets remain preferred, document acceptance of risk.
5. Recommend travel insurance review.

## Workflow 9: Group travel for a small business

1. Collect traveler count and approval owner.
2. Avoid collecting full sensitive IDs in general notes.
3. Use a secure traveler profile system if needed.
4. Search group-friendly fares or flexible hotel rates.
5. Track per-traveler cost and shared costs.
6. Keep invoice details consistent.
7. Require human approval before payment.

## Workflow 10: Post-booking pack

```markdown
# Travel pack

- Booking reference:
- Supplier:
- Dates:
- Travelers:
- Total paid:
- Currency:
- Cancellation deadline:
- Check-in instructions:
- Baggage:
- Airport/train transfer:
- Invoice requested:
- Missing documents:
- Emergency supplier contact:
```

## Acceptance criteria

A workflow is complete only when status is marked quote, pending approval, booked, cancelled, or failed; every cost line has original currency and ₪ estimate; every non-₪ conversion has source and timestamp; every booking has supplier name and reference; every business booking has invoice/receipt status; every unverified rule is marked unverified.
