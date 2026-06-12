# Workflow Guide

Use these workflows as implementation recipes for Israeli feedback collection.

## Workflow 1: Post-appointment WhatsApp review request

Best for: clinics, salons, personal trainers, tutors, repair visits.

Inputs:

```json
{
  "business_name": "קליניקת הדר",
  "platform": "google",
  "google_place_id": "ChIJexample",
  "channel": "whatsapp",
  "customer": {
    "full_name": "דנה כהן",
    "phone": "050-123-4567",
    "consent": true
  }
}
```

Steps:

1. Confirm appointment status is completed.
2. Exclude any customer with an open complaint, refund, or unresolved service issue.
3. Normalize phone to `+972501234567`.
4. Build Google review URL.
5. Generate WhatsApp text.
6. Validate Hebrew, opt-out text, and quiet time.
7. Send 1-3 hours after appointment, Sunday-Thursday.
8. Record message ID and opt-out state.
9. Send at most one reminder after 3-5 business days if allowed.

Message:

```text
שלום דנה, תודה שבחרת בקליניקת הדר.
אפשר להשאיר חוות דעת קצרה כאן?
https://www.google.com/maps/search/?api=1&query=Clinic+Hadar&query_place_id=ChIJexample
זה עוזר לאנשים באזור למצוא שירות אמין.
להסרה: השב/י הסר
```

Success criteria:

- Delivery accepted by WhatsApp provider.
- No opt-out breach.
- Review link opens the intended business.
- No sensitive appointment details appear in the message.

## Workflow 2: Ecommerce email after delivery

Best for: small Shopify/WooCommerce stores, marketplace sellers, specialty retailers.

Steps:

1. Wait for delivery confirmation plus 24-48 hours.
2. Skip refunded, cancelled, disputed, or delayed orders.
3. Personalize with first name and business name only.
4. Link to Google, Zap, or a first-party product feedback form.
5. Include a reply path for service issues.
6. Include opt-out wording.
7. Suppress customers who already reviewed the same order.

Email:

```text
Subject: איך הייתה ההזמנה?

שלום דנה,

מקווה שהמשלוח הגיע כמו שצריך.
חוות דעת קצרה תעזור ללקוחות אחרים לבחור נכון:
https://www.zap.co.il/clientcard.aspx?siteid=12345

אם הייתה בעיה בהזמנה, אפשר פשוט להשיב למייל הזה ולטפל בזה ישירות.

להסרה מרשימת הודעות כאלה, אפשר להשיב "הסרה".
```

## Workflow 3: SMS fallback for non-WhatsApp customers

Best for: appointment-based businesses that already send operational SMS reminders.

Steps:

1. Confirm SMS is an accepted operational channel for the customer.
2. Use a short branded HTTPS link.
3. Keep Hebrew first.
4. Add `להסרה: הסר`.
5. Avoid multi-message SMS unless cost and consent are acceptable.
6. Log provider message ID.

SMS:

```text
דנה, תודה שבחרת בקליניקת הדר. חוות דעת קצרה תעזור ללקוחות באזור: https://x.co/rev להסרה: הסר
```

## Workflow 4: Private-first rating gate for sensitive services

Best for: health, therapy, education, finance, legal, or high-value services.

Steps:

1. Send private feedback link rather than public review URL.
2. Ask for a 1-5 satisfaction rating.
3. Route:
   - 5: show public review link on thank-you page.
   - 4: ask what could improve.
   - 1-3: open a private service ticket.
4. Never pressure low-rating customers to change their feedback.
5. Avoid mentioning service details in the message.

Private message:

```text
שלום דנה, תודה על הביקור.
אפשר לשתף איך הייתה החוויה בקישור פרטי קצר?
https://clinic.example.co.il/feedback/abc
להסרה: השב/י הסר
```

## Workflow 5: Testimonial approval for a freelancer

Best for: designers, developers, consultants, photographers, copywriters.

Steps:

1. Ask for one sentence about the outcome.
2. Convert the response into a concise testimonial only if needed.
3. Send the exact proposed wording back for approval.
4. Offer attribution choices.
5. Store approval before publishing.

Approval request:

```text
שלום דנה,
אפשר להשתמש במשפט הבא כהמלצה באתר?

"העבודה הייתה מקצועית, מהירה וברורה לכל אורך הדרך."

אפשר לפרסם בשם פרטי בלבד, בשם החברה, בראשי תיבות או ללא שם.
לא יפורסם בלי אישור מפורש במייל חוזר.
```

## Workflow 6: Negative-review recovery

Best for: public complaint or low private score.

Steps:

1. Acknowledge without arguing.
2. Move to private channel.
3. Do not reveal private customer details.
4. Offer practical next step.
5. Record the case.
6. Do not ask for deletion.
7. After genuine resolution, a neutral follow-up may ask whether anything else is needed; avoid pressure.

Public response pattern:

```text
תודה ששיתפת. חשוב לבדוק את המקרה לעומק ולטפל בצורה מסודרת.
אפשר לפנות אלינו בפרטי עם פרטי התקשרות כדי שנוכל לבדוק ולעזור.
```

## Workflow 7: Monthly hygiene and link verification

Steps:

1. Re-test all review links on mobile and desktop.
2. Export suppression list.
3. Remove stale contacts beyond retention period.
4. Check failed sends and bounces.
5. Review sample messages for Hebrew and accessibility.
6. Reconfirm provider templates and API versions.
7. Sample 10 delivery logs and verify consent evidence.
8. Update campaign copy before holidays.

## Workflow 8: Consumer evidence log

Best for: an individual consumer tracking service interactions before filing a complaint or writing a public review.

Steps:

1. Keep a private timeline with dates in DD/MM/YYYY format.
2. Save invoices, messages, order numbers, photos, and names of representatives.
3. Request resolution privately first.
4. Avoid publishing claims that cannot be supported.
5. Separate factual timeline from opinion.
6. Do not solicit others to post coordinated negative reviews.

Evidence table:

| Date | Event | Evidence | Next action |
|---|---|---|---|
| 03/06/2026 | Technician visit | Invoice 123, WhatsApp screenshot | Request repair |
| 05-06-2026 | No response | Email copy | Escalate support |
