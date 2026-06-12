# Workflow Guide

Use these workflows to run the skill in real business situations. Each workflow includes data requirements, timing, message output, quality checks, and failure handling.

## Workflow 1: Home service check-in then review request

Scenario: electrician, plumber, technician, locksmith, installer, cleaner.

### Trigger

A service job is marked complete in the CRM or job diary.

### Required data

```json
{
  "business_name": "אור חשמל",
  "customer_name": "דנה",
  "phone_e164": "+972501234567",
  "event_type": "service_completed",
  "event_date": "03/06/2026",
  "channel": "whatsapp",
  "sentiment": "unknown",
  "review_url": "https://g.page/r/example/review"
}
```

### Steps

1. Verify that the service is complete.
2. Check opt-out and complaint status.
3. Send a satisfaction check-in, not a review request.
4. Wait for a positive reply such as `הכול מעולה`, `תודה`, `כן`, `מרוצה`.
5. Send the review request 10-30 minutes later, only inside a friendly Israeli window.
6. Log both messages with the same job ID.

### First message

```text
היי דנה, תודה שבחרת באור חשמל. רציתי לוודא שהכול תקין אחרי השירות מ-03/06/2026. אם יש משהו שדורש טיפול נוסף, אפשר לענות כאן ואטפל בזה בהקדם.
```

### Second message after positive reply

```text
היי דנה, תודה על העדכון. אם השירות היה טוב עבורך, אפשר להשאיר חוות דעת קצרה כאן:
https://g.page/r/example/review
זה עוזר ללקוחות נוספים להבין למה לצפות. תודה רבה.
```

### Failure handling

| Problem | Action |
|---|---|
| Customer reports issue | Create service ticket and stop review flow. |
| No response | Do not send review request automatically unless policy permits neutral one-step review requests. |
| Friday 13:10 | Schedule Sunday 09:30. |
| Review link missing | Create internal task to add link. |

## Workflow 2: Freelancer project delivery

Scenario: designer, developer, copywriter, consultant, translator.

### Trigger

Final files or deliverables are sent.

### Timing

- Delivery confirmation: same day during business hours.
- Feedback request: 24-48 hours after delivery.
- Review request: after explicit positive feedback.

### Message

```text
היי נועה, תודה על העבודה המשותפת. רציתי לוודא שהקבצים מ-03/06/2026 התקבלו ונפתחים תקין. אם צריך תיקון קטן או הבהרה, אפשר לענות כאן.
```

### Positive follow-up

```text
היי נועה, תודה על המשוב. אם התהליך היה מוצלח עבורך, אפשר להשאיר חוות דעת קצרה כאן:
{review_url}
זה עוזר ללקוחות נוספים לקבל החלטה. תודה רבה.
```

### Checklist

- Include no confidential project details.
- Avoid public review request when NDA or confidentiality applies.
- Ask for private testimonial approval if public review is unsuitable.

## Workflow 3: Accountant missing documents

Scenario: bookkeeper or accountant collecting invoices and receipts for monthly VAT reporting.

### Trigger

Cutoff date approaches and required documents are missing.

### Required data

```json
{
  "business_name": "כהן הנהלת חשבונות",
  "customer_name": "יואב",
  "event_type": "missing_documents",
  "period_label": "מאי 2026",
  "due_date": "10/06/2026",
  "channel": "whatsapp",
  "business_type": "accountant"
}
```

### Message

```text
היי יואב, חסרים עדיין מסמכים להשלמת הדיווח עבור מאי 2026. נא לשלוח את החשבוניות/קבלות החסרות עד 10/06/2026 כדי לאפשר הגשה בזמן. תודה.
```

### Notes

- Use `חשבונית מס/קבלה`, `קבלה`, `הוצאה`, `דו"ח מע"מ`, and `ניכוי מס במקור` correctly.
- Do not send a list of sensitive suppliers in SMS.
- Use a secure portal when documents contain personal data.

### Failure handling

| Problem | Action |
|---|---|
| Customer already uploaded documents | Apologize briefly and mark complete. |
| Customer asks for extension | Create task and notify accountant. |
| Customer inactive | Try approved alternate channel only if allowed. |

## Workflow 4: Payment reminder for small business

Scenario: invoice issued, due date passed or approaching.

### Trigger

Invoice due date is 1 day away, same day, or 3 days overdue.

### Message for upcoming due date

```text
היי דנה, תזכורת נעימה לגבי חשבונית מס/קבלה מ-03/06/2026 על סך ₪1,250. אם נוח, אפשר להסדיר תשלום בקישור:
{payment_url}
תודה.
```

### Guardrails

- Do not threaten legal action.
- Do not send public embarrassment messages.
- Do not imply debt collection unless an approved legal process exists.
- Provide a path to report payment already made.

## Workflow 5: Online shop delivery check-in

Scenario: retail purchase or delivery.

### Trigger

Carrier marks package delivered.

### Timing

Send 24 hours after delivery at 10:00-12:00 or 18:00-20:00.

### Message

```text
היי דנה, רציתי לוודא שהמשלוח מ-03/06/2026 הגיע תקין. אם יש בעיה, אפשר לענות כאן. אם הכול בסדר, תודה על הבחירה בסטודיו הבית.
```

### Next step

If the customer replies positively, send review request. If the customer reports missing or damaged goods, create a support ticket and stop review request.

## Workflow 6: Appointment reminder

Scenario: appointment-based business.

### Message

```text
היי דנה, תזכורת לפגישה עם סטודיו הבית בתאריך 04/06/2026 בשעה 10:30. אם צריך לשנות מועד, נא לעדכן מראש. תודה.
```

Sensitive industries: for clinics, therapy, legal consultations, and minors, do not include service type. Use only date, time, location, and contact path.

## Workflow 7: Consumer follow-up to a provider

```text
היי, אשמח לקבל עדכון לגבי הטיפול בפנייה מ-03/06/2026. אם חסר פרט נוסף מצדי, אפשר לעדכן כאן. תודה.
```

If no answer after two business days:

```text
היי, זו תזכורת נוספת לגבי הפנייה מ-03/06/2026. נא לעדכן סטטוס או מועד צפוי לטיפול. תודה.
```

## Workflow 8: Multi-branch business

Use the branch-specific review link. Do not send all customers to a generic location when the review platform expects branch-level reviews.

```json
{
  "branch_name": "סניף רמת גן",
  "review_url": "https://g.page/r/branch-example/review",
  "location_context": "רמת גן"
}
```

## Workflow 9: Manual approval queue

Use when the business handles sensitive services or wants owner approval.

```json
{
  "status": "pending_approval",
  "message_he": "היי דנה...",
  "risk_flags": ["sensitive_business_type"],
  "approve_by": "2026-06-04T17:00:00+03:00"
}
```

Approval rules:

- Approve only when no complaint is open.
- Edit out sensitive details.
- Confirm link and recipient.
- Send inside a friendly window.

## Workflow 10: Bulk CSV preview

CSV columns:

```csv
customer_name,phone_e164,event_type,event_date,channel,sentiment,consent_status,review_url
דנה,+972501234567,service_completed,03/06/2026,whatsapp,unknown,transactional,https://g.page/r/example/review
```

Process:

1. Validate phone numbers.
2. Normalize dates.
3. Remove opted-out contacts.
4. Generate preview only.
5. Manually approve the first 20 messages.
6. Queue the remainder with rate limits.

## Workflow quality gates

- `should_send` must be true.
- `fallback_action` must be empty.
- `recommended_send_at` must be inside an Israeli-friendly window.
- `message_he` must not contain unresolved placeholders.
- `review_url` must be present for direct review requests.
- `amount_ils` must be formatted with `₪`.
- Sensitive details must be absent from SMS and WhatsApp.
- Opt-out line must exist for promotional content.
