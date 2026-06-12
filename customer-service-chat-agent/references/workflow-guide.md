# Workflow Guide

Use these workflows to implement a Hebrew customer-service chat agent end to end.

## Workflow 1: Build the knowledge base

1. Collect current FAQ, prices, policies, opening hours, delivery SLA, payment methods, invoice requirements, and human owners.
2. Remove stale prices, expired holiday hours, and old refund promises.
3. Convert each FAQ into structured records:

```json
{"id": "faq_delivery_gush_dan", "intent": "delivery", "question_he": "כמה זמן משלוח בגוש דן?", "answer_he": "משלוח בגוש דן נמשך בדרך כלל 1-3 ימי עסקים.", "conditions": ["לא כולל חגים"], "owner": "operations", "last_reviewed": "03/06/2026"}
```

4. Mark each item as direct answer, clarification required, live lookup required, or human handoff.
5. Review Hebrew wording and accounting terms.
6. Version the knowledge base.

Done criteria: every answer has owner, review date, approved wording, and escalation rule.

## Workflow 2: Standard FAQ

Customer: "אתם פתוחים ביום שישי?"

1. Detect hours intent.
2. Check regular and holiday hours.
3. Answer only from source.

Reply:

```text
ביום שישי פתוח בין 09:00-13:00. אם מדובר באיסוף עצמי, כדאי להגיע עד 12:30.
```

## Workflow 3: Order status

1. Ask for order number or phone if missing.
2. Validate format.
3. Call order API.
4. Handle not found, identity mismatch, timeout, and late delivery.
5. Provide status and tracking if safe.

Handoff packet for late delivery:

```json
{"intent": "late_delivery", "urgency": "high", "summary": "הזמנה 10493 איחרה מעבר ל-SLA ואין עדכון מחברת השליחויות.", "recommended_next_action": "תפעול יבדוק מול חברת השליחויות ויחזור ללקוח."}
```

## Workflow 4: Refund or return

1. Acknowledge the issue.
2. Do not approve a refund automatically.
3. Ask for order number, purchase date, item condition, and photo if relevant.
4. Explain policy only if approved.
5. Hand off refund approval.

Reply:

```text
מבין שזה מתסכל. החזר כספי על מוצר פגום מחייב בדיקה, לכן אעביר לנציג. אפשר לשלוח מספר הזמנה, תאריך רכישה ותמונה של הפגם?
```

## Workflow 5: Invoice request

1. Ask for order number if missing.
2. Confirm payment through order/accounting source.
3. Ask private customer for full name and email.
4. Ask business customer for legal name, ח.פ./ע.מ., and email.
5. Create document in accounting system.
6. Escalate VAT status, duplicate document, credit note, or invalid ID errors.

## Workflow 6: Appointment booking

1. Identify service type and preferred time.
2. Query booking system.
3. Present exact available slots only.
4. Create booking after explicit customer choice.
5. Confirm as DD/MM/YYYY HH:MM.

Never invent appointment availability.

## Workflow 7: Technical support

1. Ask for error text or screenshot if useful.
2. Offer safe basics: refresh, official password reset, another browser.
3. Never ask for password, OTP, or card details.
4. Escalate suspected account takeover, security, or payment issue.

## Workflow 8: Privacy deletion/export

1. Detect privacy intent.
2. Avoid discussing stored data in chat.
3. Ask for contact channel for verification.
4. Create privacy ticket.
5. Confirm handoff to responsible person.

## Workflow 9: Angry customer or payment dispute

1. Acknowledge frustration.
2. Detect chargeback, duplicate charge, legal threat, or complaint.
3. Collect order/payment reference only.
4. Escalate high urgency.

Reply:

```text
מבין שזה מתסכל. טענה לחיוב כפול חייבת בדיקה של צוות חיובים. אפשר לשלוח מספר הזמנה או אסמכתת תשלום, בלי מספר כרטיס מלא?
```

## Workflow 10: Accessibility issue

1. Acknowledge the accessibility problem.
2. Offer alternate channel: phone, WhatsApp, email, or human support.
3. Collect page link, device, browser, assistive technology only if useful.
4. Escalate to accessibility/support owner.

## Workflow 11: Monitoring after launch

Daily for first two weeks:

- Review all low-confidence and handoff conversations.
- Add missing FAQ entries.
- Fix Hebrew phrasing customers misunderstood.
- Check APfailures and latency.
- Confirm handoff SLA compliance.

Weekly:

- Update top intents.
- Add regression tests.
- Remove unnecessary data fields.
- Review privacy and payment incidents.
