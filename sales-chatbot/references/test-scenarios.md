# Test Scenarios

Use these scenarios before production release and after catalog or policy changes. Expected output can vary by product catalog, but required behavior must remain stable.

| # | Customer message | Context | Expected behavior |
|---:|---|---|---|
| 1 | "שלום, יש משהו לניהול לקוחות?" | consent true | Greeting or product-fit reply; recommend CRM |
| 2 | "כמה עולה CRM לעסק קטן?" | consent true | Show ₪ price including VAT |
| 3 | "אפשר בתשלומים?" | preferred installments 3 | Show total and per-installment wording |
| 4 | "יקר לי, יש משהו עד 300 שקל?" | budget 300 | Avoid upgrade above budget |
| 5 | "אני רוצה דוחות ואוטומציות" | budget 600 | Offer professional package if catalog supports it |
| 6 | "מה מגיע עם זה?" | active cart | Explain primary item and relevant add-ons |
| 7 | "תוסיף הדרכה" | active cart | Cross-sell setup/training item |
| 8 | "אני רוצה להזמין עכשיו" | consent true | Next step: secure payment link, no card data in chat |
| 9 | "שלח לי קישור תשלום" | selected SKU | Create payment handoff; do not ask for card number |
| 10 | "אפשר חשבונית לעסק?" | B2B | Ask for invoice details through secure process |
| 11 | "המחיר כולל מע״מ?" | consumer | Answer clearly with VAT wording |
| 12 | "אני מחיפה, מתי המשלוח?" | city Haifa | Give cautious delivery estimate |
| 13 | "אני גר ביישוב מרוחק" | remote city | Handoff or cautious delivery verification |
| 14 | "מה האחריות?" | product selected | State warranty if known, otherwise policy summary |
| 15 | "אני רוצה לבטל" | active order | No selling; policy summary and handoff if needed |
| 16 | "המוצר הגיע שבור" | order exists | Complaint handoff |
| 17 | "חויבתי פעמיים" | payment issue | Handoff to billing, no upsell |
| 18 | "תפסיקו לשלוח לי הודעות" | any | Mark opt-out, confirm removal |
| 19 | "מי אתם בכלל?" | no consent | Service answer only; no promotional pitch |
| 20 | "שלח מבצע חדש" | no consent | Ask for consent or avoid marketing |
| 21 | "יש הנחה למזומן?" | consumer | Follow approved policy; do not suggest undocumented payment |
| 22 | "אפשר לשלם 12 תשלומים?" | product max 3 | Cap at allowed max and show total |
| 23 | "יש לכם את זה במלאי?" | target product | Confirm only if stock data exists |
| 24 | "המתחרה זול יותר" | price objection | Compare value, service, delivery; no defamation |
| 25 | "אני צריך הצעה עד מחר" | urgent | Generate quote and valid-until date DD/MM/YYYY |
| 26 | "דבר איתי בלשון נקבה" | preference | Use respectful feminine wording where templates support it |
| 27 | "אני לא מבין טכנולוגיה" | low confidence | Offer setup/training cross-sell gently |
| 28 | "תשלח לי למייל" | email provided | Use secure CRM/email flow |
| 29 | "הנה מספר כרטיס..." | sensitive data | Stop and instruct not to send card data |
| 30 | "אפשר להחזיר אחרי פתיחה?" | warranty/refund | Neutral policy and handoff for specifics |

## Automated pytest coverage

The bundled test suite covers:

- Price formatting with ₪.
- VAT wording.
- DD/MM/YYYY date formatting.
- Intent classification.
- Opt-out flow.
- Complaint handoff.
- Base recommendation.
- Upsell and cross-sell behavior.
- Budget-sensitive upsell blocking.
- Installment cap.
- Async method behavior.
- Quote generation.
- Catalog validation.
- Duplicate SKU handling.
- Missing cross-sell reference.
- Out-of-stock warning.
- Age confirmation warning.
- Structured response keys.
- Empty catalog rejection.
- JSON catalog loading.

## Manual review checklist

For each scenario, verify:

1. Hebrew sounds natural.
2. The bot asks only one next-step question.
3. Price includes ₪.
4. Full total appears whenever installments appear.
5. No card details are requested.
6. Opt-out stops marketing.
7. Complaints do not trigger sales offers.
8. Handoff includes useful summary.
9. Dates use DD/MM/YYYY.
10. Add-ons are relevant to the main product.


## Web-validated scenarios

31. Invoice allocation current threshold check: create a B2B quote above ₪5,000 before VAT on 03/06/2026, fetch `MinimumAmount`, and require an allocation-number workflow before final invoice issue.
32. Bank of Israel conversion disclosure: quote a USD-linked service in ₪, fetch the representative rate for the requested date, and show the rate date in the operator note.
33. WhatsApp status webhook: receive a payload containing `statuses`, update delivery telemetry, and avoid treating delivery as payment confirmation.
