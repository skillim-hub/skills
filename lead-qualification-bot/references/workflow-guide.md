# Workflow Guide

## Workflow 1: Urgent tradesperson lead

Customer: "יש קצר בבית כמה עולה?"

1. Ask city.
2. Ask whether it is today, this week, or flexible.
3. Ask for a short description or photo if safe.
4. Show short service privacy notice.
5. If same-day and in service area, route to hot queue.
6. Send a safety message for electrical/fire risk.

Expected handoff note:

```text
[HOT] דנה, 050-123-4567, ראשון לציון
צורך: קצר חשמל היום
הסכמה לשירות: כן
פעולה: להתקשר עד 10:30
```

## Workflow 2: Freelancer project inquiry

Customer: "צריך אתר לעסק חדש"

Ask project type, deadline, budget range in ₪, example links, and callback time. A lead with a defined scope, deadline, and realistic budget is hot or warm. A user who says "רק בודק" is nurture.

## Workflow 3: Accounting inquiry

Customer: "פתחתי עסק ואני לא יודע אם עוסק פטור או מורשה"

Collect activity type, planned start date in DD/MM/YYYY, expected invoice volume, and callback time. Do not answer "מה עדיף" or "כמה מס אשלם" inside the bot. Route to a qualified professional.

## Workflow 4: Clinic appointment request

Customer: "יש לי כאבים חזקים, צריך תור"

Route to human. Add emergency disclaimer where appropriate. Collect branch/city and callback time only if safe. Avoid medical diagnosis.

## Workflow 5: Course provider nurture

Customer: "אפשר פרטים על קורס אקסל?"

Ask current level and desired start timing. Send syllabus or booking link. Ask promotional consent separately before updates and benefits.

## Workflow 6: Retail delivery

Customer: "יש משלוחים לחולון?"

Ask product, quantity, desired date, delivery area, and callback/payment expectation. Clarify delivery fee and whether prices include VAT where relevant.

## Workflow 7: Human queue

| Tier | Queue | SLA |
|---|---|---|
| Hot | hot_leads | 15 minutes |
| Warm | sales_today | same business day |
| Nurture | nurture | 2-5 business days |
| Low fit | low_fit_review | optional |
| Human | human_sensitive | immediate |
| Support | support | according to policy |

## Workflow 8: CRM export

1. Normalize phone to E.164.
2. Dedupe by phone and message ID.
3. Create or update contact.
4. Create lead/opportunity.
5. Store transcript summary, not unnecessary full transcript.
6. Store consent fields.
7. Assign owner and SLA.
8. Send WhatsApp confirmation.

## Workflow 9: CSV-only operation

Best for businesses with fewer than 20 weekly leads.

```bash
python scripts/lead-qualification-bot-cli.py batch --input scripts/examples/sample_leads.csv --output qualified_leads.csv
```

Review hot leads first, then warm leads, then nurture. Delete stale spam and invalid records according to retention policy.

## Workflow 10: Weekly improvement

Review 20 conversations and check: first reply usefulness, abandonment points, hot lead response time, opt-out handling, sensitive handoffs, score accuracy, and conversion by tier.
