# Workflow Guide

Use these workflows as implementation blueprints for Israeli appointment scheduling over WhatsApp.

## Workflow 1: New Appointment

Customer:

```text
היי, אפשר תור לתספורת מחר אחר הצהריים?
```

Steps:

1. Receive webhook.
2. Deduplicate by provider message ID.
3. Normalize phone to `972...`.
4. Detect intent `new_appointment`.
5. Extract service `תספורת`, date preference `tomorrow`, time preference `afternoon`.
6. Check service catalog: duration 30 minutes, price ₪90, staff any.
7. Search calendar in `Asia/Jerusalem`.
8. Offer up to three slots.

```text
בשמחה. זמינים מחר לתספורת:
1. 14:30
2. 15:15
3. 17:00
להמשך יש להשיב עם מספר האפשרות.
```

9. Customer replies `2`.
10. Create calendar event and persist appointment.
11. Send confirmation.
12. Create 24-hour and 2-hour reminders.

Failure handling:

| Failure | Handling |
|---|---|
| Service not recognized | Ask customer to choose from short list |
| No slot | Offer nearest dates |
| Ambiguous reply | Ask for a number |
| Calendar write fails | Do not send confirmation; route to staff |
| Confirmation send fails | Keep appointment, mark failed, alert staff |

## Workflow 2: Reminder Dispatch

Select reminders where appointment is `confirmed`, reminder is `pending`, send time is due, appointment start is in the future, phone is valid, and idempotency key has not been sent.

Steps:

1. Load due reminders.
2. Lock records or mark `processing`.
3. Re-check appointment status.
4. Build Hebrew reminder.
5. Send WhatsApp message.
6. Store provider message ID.
7. Mark `sent`.

Example:

```text
תזכורת: התור שלך לייעוץ ראשוני בקליניקת הדוגמה נקבע ביום 18/06/2026 בשעה 10:30.
כתובת: רחוב הרצל 10, תל אביב.
לאישור הגעה יש להשיב 1. לשינוי או ביטול יש להשיב 2.
```

Idempotency key:

```text
apt_123:1440:appointment_reminder_he
```

## Workflow 3: Reschedule

Customer replies `2` to a reminder.

Steps:

1. Resolve the active appointment.
2. Mark `reschedule_requested`.
3. Ask for preferred day or offer available slots.
4. Hold selected slot briefly.
5. Update calendar after selection.
6. Recalculate reminders.
7. Send updated confirmation.

```text
אין בעיה, אפשר להזיז את התור.
זמינים כרגע:
1. 19/06/2026 בשעה 09:30
2. 19/06/2026 בשעה 13:00
3. 21/06/2026 בשעה 10:00
להמשך יש להשיב עם מספר האפשרות.
```

Guardrails: keep the original event until the new slot is confirmed, store the previous start time, and notify staff for late changes.

## Workflow 4: Cancellation

Customer:

```text
בטלי לי את התור
```

Steps:

1. Resolve active appointment.
2. Check cancellation policy.
3. Cancel automatically only when inside the allowed window.
4. Route late-cancellation fee cases to staff.
5. Update calendar.
6. Mark reminders skipped.
7. Send acknowledgement.

```text
התור לייעוץ ראשוני בתאריך 18/06/2026 בשעה 10:30 בוטל.
לקביעת מועד חדש יש להשיב "תור חדש".
```

Late cancellation:

```text
התור קרוב למועד שנקבע. לפי מדיניות העסק, ביטול מאוחר עשוי להיות כרוך בחיוב.
הבקשה הועברה לטיפול צוות.
```

## Workflow 5: No-Show

1. Staff marks `no_show` after appointment time.
2. Stop remaining reminders.
3. Send at most one neutral follow-up where policy permits.

```text
נראה שהתור היום לא התקיים. לקביעת מועד חדש אפשר להשיב "תור חדש".
```

Do not auto-charge by bot message alone.

## Workflow 6: Waiting List

1. Ask whether the customer wants to join a waiting list.
2. Store preferred days and hours.
3. When cancellation opens a slot, offer it with a short expiry.
4. Confirm the first eligible acceptance according to policy.

```text
התפנה תור ביום 17/06/2026 בשעה 12:00.
לתפיסת התור יש להשיב 1 עד השעה 10:30.
```

## Workflow 7: Staff Escalation

Escalate medical/legal/financial requests, threats, angry messages, refund disputes, cancellation-fee disputes, multiple appointments for one phone, low confidence, and media messages.

Escalation note:

```json
{
  "reason": "late_cancellation_fee",
  "customer_phone": "972541234567",
  "appointment_id": "apt_123",
  "last_message": "אני רוצה לבטל ולא לשלם",
  "recommended_action": "Call customer before cancellation"
}
```

## Workflow 8: CSV Import

CSV:

```csv
customer_name,customer_phone,service_name,start_at,duration_minutes,price_ils,location
דנה,054-123-4567,ייעוץ ראשוני,2026-06-18T10:30:00+03:00,45,250,"רחוב הרצל 10, תל אביב"
```

Rules:

- Normalize phone.
- Reject duplicate `(phone, start_at, service)`.
- Reject naive datetimes.
- Reject past reminders.
- Import as `confirmed` only when staff already confirmed.
- Do not send confirmations automatically after import unless explicitly selected.

## Workflow 9: Opt-Out

Customer:

```text
הסר
```

Steps:

1. Mark WhatsApp opt-out.
2. Stop non-essential reminders.
3. Send one acknowledgement.
4. Keep a human contact path.

```text
הבקשה התקבלה. לא יישלחו הודעות WhatsApp נוספות שאינן נדרשות לשירות שכבר הוזמן.
לקביעת תור בעתיד ניתן לפנות בטלפון 03-123-4567.
```

Detect: `הסר`, `להסרה`, `STOP`, `stop`, `אל תשלחו`, `לא לשלוח`.

## Workflow 10: End-of-Day Review

Run at closing time.

Checklist:

- Tomorrow’s appointments.
- Sent or queued 24-hour reminders.
- Failed messages.
- Open reschedule requests.
- Invalid phone numbers.
- Calendar conflicts.
- Staff escalations.

Summary:

```text
סיכום תורים ל-18/06/2026:
סה"כ תורים: 14
תזכורות נשלחו: 13
כשלי שליחה: 1
בקשות שינוי פתוחות: 2
ביטולים היום: 1
```
