# Workflow Guide

Use these workflows to move from raw incoming leads to consistent routing, handoff, response, and reporting.

## Workflow 1: Web form to CRM

1. Collect name, phone or email, message, city or service location, product selection, and a separate marketing consent checkbox.
2. Submit the lead as UTF-8 JSON.
3. Normalize phone and email.
4. Detect language from explicit form selection or message.
5. Normalize region from city or text.
6. Normalize product interest.
7. Route using `LeadRouterClient.route_lead`.
8. Write the route result to CRM.
9. Create first-response due time from `sla_minutes`.
10. Send a service acknowledgement when appropriate.
11. Block promotional follow-up unless marketing consent is granted.
12. Monitor first response completion.

Example:

```json
{
  "name": "עדי כהן",
  "phone": "052-1234567",
  "message": "אשמח להצעת מחיר להתקנה ברעננה",
  "city": "רעננה",
  "product_interest": "installation",
  "channel": "web_form",
  "consent_marketing": true,
  "created_at": "2026-06-04T10:05:00+03:00"
}
```

Done condition: CRM contains original message, route result, owner or queue, first-response SLA, and consent status.

## Workflow 2: WhatsApp lead to regional team

1. Save inbound WhatsApp message with sender phone.
2. Preserve original text, emojis, and right-to-left characters.
3. Detect language.
4. Extract city or region from message.
5. Detect urgency terms such as `דחוף`, `עכשיו`, `emergency`, `срочно`, `طارئ`.
6. Route to regional owner when service is on-site.
7. If region is unknown, route to qualification and ask for service location.
8. Send a service acknowledgement in the detected language.
9. Do not send promotional templates unless consent is recorded.

Acknowledgements:

```text
HE: שלום, קיבלנו את הפנייה שלך. נציג מתאים יחזור אליך בהקדם.
AR: مرحباً، استلمنا طلبك وسيتواصل معك ممثل مناسب قريباً.
RU: Здравствуйте, мы получили ваш запрос. Подходящий специалист свяжется с вами в ближайшее время.
EN: Hello, the request was received. The right team will contact you shortly.
```

## Workflow 3: Phone call note to lead route

1. Capture phone number from caller ID or manual entry.
2. Enter a concise note with service requested, city, urgency, and preferred language if mentioned.
3. Add `channel = phone`.
4. Route the lead.
5. If phone area code is the only region signal, confirm location.
6. Create a callback task for the selected queue.

Example:

```json
{"name":"מרים","phone":"02-5555555","message":"מבקשת תור לייעוץ בירושלים, מעדיפה עברית","channel":"phone","product_interest":"appointments"}
```

Expected: `HE`, `JERUSALEM`, `appointments`, normal priority.

## Workflow 4: Russian-speaking support escalation

1. Detect Cyrillic script or explicit `language=ru`.
2. Detect support issue from text.
3. Route to Russian Support Queue when available.
4. If no Russian support is active, route to multilingual intake and add an escalation note.
5. Preserve original Russian text in CRM.
6. Add an internal summary only as an addition, not a replacement.

Example:

```json
{"name":"Марина","phone":"+972541112222","message":"После установки устройство не работает","city":"חיפה","channel":"web_form"}
```

Expected: Russian Support Queue, `support`, `RU`, `HAIFA`, high priority.

## Workflow 5: Arabic lead from northern locality

1. Detect Arabic script.
2. Normalize localities such as נצרת, אום אל-פחם, שפרעם, סכנין, טמרה, רהט, or الطيبة.
3. Determine whether the request is sales, support, billing, or installation.
4. Route to Arabic Sales Queue or Arabic Support Queue where available.
5. Attach region and original city to handoff when on-site service is needed.
6. Send first response in Arabic when possible.

## Workflow 6: Enterprise lead qualification

1. Detect enterprise terms: `branches`, `national rollout`, `procurement`, `רשת`, `סניפים`, `פריסה ארצית`.
2. Check budget if provided.
3. Override normal regional routing when service is national or remote.
4. Route to Enterprise Desk.
5. Attach budget, number of branches, city list, and company name.
6. Set SLA to 60 minutes or less during business hours.

## Workflow 7: Billing or receipt request

1. Detect `חשבונית`, `קבלה`, `חיוב`, `תשלום`, `invoice`, `receipt`, `refund`, `счет`, `فاتورة`.
2. Route to Billing Queue.
3. Keep transaction reference if supplied.
4. Avoid asking for payment card details in unsecured channels.
5. Use service response only.

## Workflow 8: CSV backfill

1. Export leads as UTF-8 CSV.
2. Include `name`, `phone`, `email`, `message`, `city`, `product_interest`, `channel`, `consent_marketing`.
3. Run:

```bash
python scripts/lead_router_cli.py batch incoming.csv routed.jsonl
```

4. Inspect warnings before outreach.
5. Import routed JSONL into CRM or review manually.
6. Do not trigger marketing campaigns from old leads without clear consent.

## Workflow 9: Manual override

1. Show route result to staff.
2. Allow override of assignee, department, priority, and SLA.
3. Require an override reason.
4. Save the original automatic result.
5. Save override timestamp and user.
6. Include overrides in weekly quality review.
7. Update rules only when repeated overrides reveal a clear pattern.

Recommended reasons: `staff_absence`, `holiday_schedule`, `special_customer`, `wrong_region`, `wrong_language`, `wrong_product`, `duplicate`, `campaign_exception`.

## Workflow 10: Daily routing quality review

Track total leads, routes by department, routes by language, routes by region, low-confidence count, missing-contact count, unknown-region count, missed SLA count, manual override count, and closure status by route.

Review questions:

- Which regions have the most unknown routes?
- Which product aliases are missing?
- Which language queue is overloaded?
- Which warnings correlate with missed SLA?
- Which overrides should become rules?

## Workflow 11: Holiday and outside-hours handling

1. Maintain business hours per department.
2. Maintain Israeli holiday closure dates and internal vacation days.
3. When a lead arrives outside active hours, calculate next working response time.
4. Keep urgent safety issues on the urgent path if emergency service exists.
5. Use realistic callback wording: `הפנייה התקבלה. נחזור אליך בתחילת יום הפעילות הבא.`

## Workflow 12: Safe deletion and retention

1. Define retention periods by lead outcome.
2. Keep audit logs with minimized fields.
3. Remove raw messages when no longer needed unless required for service dispute handling.
4. Keep marketing consent evidence only when needed.
5. Redact sensitive data before exporting reports.
