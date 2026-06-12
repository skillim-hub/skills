# Workflow Guide

Use these workflows to turn the Sales Chatbot helper into a production-ready flow for Israeli small businesses, freelancers, and consumer storefronts.

## Workflow 1: WhatsApp lead to paid order

### Goal

Convert an inbound WhatsApp question into a safe product recommendation, quote, and payment link.

### Steps

1. Receive inbound message through WhatsApp provider.
2. Normalize phone number to international format.
3. Load customer state: name, city, marketing consent, previous cart, preferred language, active service window.
4. Load active catalog and business policy.
5. Call `SalesChatbotClient.recommend(message, context)`.
6. If `handoff_required` is true, send a short service reply and create a CRM task.
7. If safe to continue, send `reply_he`.
8. If customer accepts, create quote record with `quote_id`.
9. Create payment link through provider.
10. Send payment link with reminder not to share card data in chat.
11. On payment success, create accounting document.
12. Send receipt/invoice link and shipment or onboarding instructions.

### Data captured

```json
{
  "phone": "972501234567",
  "message": "כמה עולה CRM לעסק קטן?",
  "intent": "price",
  "quote_id": "SC-03062026-AB12CD34",
  "selected_sku": "BASIC-CRM",
  "consent_state": "granted",
  "handoff_required": false
}
```

### Exit criteria

- Price includes ₪ and VAT wording.
- Installments show full total.
- Payment uses secure provider link.
- Quote ID appears in CRM.
- Invoice step is queued after payment success.

## Workflow 2: Website chat product discovery

### Goal

Help a visitor select a product without forcing contact details too early.

### Steps

1. Ask one discovery question: use case, budget, urgency, or quantity.
2. Match answer to catalog tags.
3. Present one primary recommendation.
4. Offer one upgrade only when it fits the budget.
5. Offer one cross-sell only when it prevents future friction.
6. Ask for preferred next action: call, quote, secure payment link, or pickup.
7. Request personal data only after the customer chooses a next step.

### Example response

```text
לפי מה שתיארת, חבילת CRM בסיסית מתאימה להתחלה.
המחיר: ₪249.00 כולל מע״מ.
אפשר לשלם עד 3 תשלומים שווים; סך הכול נשאר ₪249.00.
אם חשוב לך דוחות ואוטומציות, חבילת CRM מקצועית נותנת יותר גמישות.
רוצה הצעת מחיר מסודרת או קישור תשלום מאובטח?
```

## Workflow 3: Freelancer quote for service package

### Goal

Turn a service inquiry into a scope-limited quote.

### Steps

1. Identify service category and deliverable.
2. Ask for deadline and scope.
3. Recommend the closest service package.
4. Offer add-on only when it reduces risk: setup call, extra revision, fast delivery.
5. Present price, VAT status, and validity date.
6. For ongoing service, state monthly billing and cancellation terms.
7. Generate quote text with `make_quote()`.
8. Send quote by email or CRM, not only in chat.

### Quote content

- Customer name.
- Service name.
- Scope.
- Price in ₪.
- VAT wording.
- Payment terms.
- Delivery date or estimated timeline.
- Validity date in DD/MM/YYYY.
- Exclusions.
- Handoff contact.

## Workflow 4: Retail cross-sell after product selection

### Goal

Add value without irritating the customer.

### Rule

Offer one add-on only after the customer has accepted the main product or asked what else is needed.

### Good add-ons

| Main item | Good cross-sell | Reason |
|---|---|---|
| Printer | Paper or toner | Prevents immediate second purchase |
| Coffee machine | Descaling kit | Maintains product |
| Gift | Greeting card | Completes gift experience |
| CRM setup | Training hour | Speeds implementation |
| Laptop | Protective sleeve | Reduces damage risk |

### Script

```text
מעולה. כדי שלא תצטרך להשלים הזמנה נוספת אחר כך, כדאי להוסיף {addon}.
זה עולה ₪{price} כולל מע״מ ומתאים כי {reason}.
להוסיף להזמנה?
```

## Workflow 5: Complaint to service handoff

### Goal

Stop selling and create a useful handoff.

### Trigger terms

"תקלה", "שבור", "לא הגיע", "חויבתי", "כועס", "תלונה", "עורך דין", "ביטול", "החזר".

### Steps

1. Acknowledge the issue.
2. Do not upsell or cross-sell.
3. Ask only for order number and short description.
4. Create CRM task with conversation transcript and quote/order IDs.
5. Send service handoff response.
6. Mark conversation as service-only until resolution.

### Handoff summary

```json
{
  "reason": "complaint",
  "customer_message": "המוצר הגיע שבור",
  "order_id": "ORDER-1001",
  "last_quote_id": "SC-03062026-AB12CD34",
  "recommended_action": "human_service_review"
}
```

## Workflow 6: Opt-out and consent maintenance

### Goal

Handle unsubscribe requests immediately.

### Steps

1. Detect phrases such as "הסר", "תפסיקו לשלוח", "לא לשלוח פרסומות".
2. Mark marketing consent as revoked.
3. Send confirmation.
4. Do not include a coupon, upsell, or survey in the opt-out confirmation.
5. Keep service notifications only when needed for active orders.

### Confirmation

```text
בוצע. הלקוח הוסר מרשימת הודעות שיווקיות. הודעות שירות הכרחיות יישלחו רק לגבי הזמנות פעילות.
```

## Workflow 7: Catalog update and release

### Steps

1. Export catalog from source of truth.
2. Validate required fields.
3. Run `python scripts/sales_chatbot_cli.py validate-catalog catalog.json`.
4. Run `pytest scripts/test_sales_chatbot_client.py`.
5. Run scenario scripts from `scripts/examples/`.
6. Compare 10 real customer messages against expected results.
7. Deploy catalog with version tag.
8. Keep previous catalog available for rollback.

## Workflow 8: B2B invoice request

### Goal

Collect invoice details without exposing sensitive data unnecessarily.

### Steps

1. Ask for business name, business number, email, and billing address through secure form or controlled CRM field.
2. Confirm whether price is VAT-inclusive or plus VAT according to business policy.
3. Create payment or invoice workflow in accounting system.
4. For invoices where allocation may be required, use the accounting or tax-authority adapter.
5. Send document link after issue.

### Customer wording

```text
אפשר להפיק חשבונית לעסק. נא למלא את פרטי העסק בטופס המאובטח.
לאחר אישור התשלום, המסמך יישלח למייל שצוין.
```

## Workflow 9: Delivery exception

### Steps

1. Detect city or address outside standard delivery rules.
2. Avoid promising a specific date.
3. Offer pickup, alternate address, or human verification.
4. Update quote after delivery fee is confirmed.

### Wording

```text
לכתובת הזו נדרש אישור זמינות משלוח לפני תשלום.
נציג יבדוק זמן ועלות סופיים ויחזור אליך.
```

## Workflow 10: Monthly subscription renewal

### Steps

1. Confirm active subscription and renewal date.
2. Present monthly price and billing period.
3. Offer upgrade only if usage suggests need.
4. Provide cancellation path.
5. Avoid promotional messages without consent.

### Wording

```text
המנוי מתחדש ב־03/06/2026 במחיר ₪99.00 כולל מע״מ לחודש.
אפשר להמשיך באותו מסלול, לשדרג למסלול מתקדם או לבקש ביטול לפי תנאי השירות.
```
