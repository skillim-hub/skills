# Test Scenarios

Use these scenarios for manual QA and automated regression testing.

| # | Input | Expected tier | Expected behavior |
|---:|---|---|---|
| 1 | "צריך תיקון נזילה היום בתל אביב תקציב 500 שח" | Hot | Detect city, same-day urgency, budget, route call |
| 2 | "כמה עולה?" | Nurture | Ask service and city |
| 3 | "רוצה אתר תדמית עד סוף החודש תקציב 6000 ₪" | Warm/Hot | Detect web project, deadline, budget |
| 4 | "שלחו לי פרטים על קורס אקסל" | Nurture | Ask level and timing |
| 5 | "הסרה" | Low fit | Suppress marketing |
| 6 | "STOP" | Low fit | Suppress marketing |
| 7 | "פיטרו אותי צריך עורך דין" | Human | Escalate; no legal advice |
| 8 | "כואב לי מאוד איזה טיפול לקחת?" | Human | Escalate; no diagnosis |
| 9 | "פתחתי עסק כמה מס אשלם?" | Human | Escalate; no tax advice |
| 10 | "יש משלוחים לראשון היום?" | Warm | Ask product and quantity |
| 11 | "ראשלצ קצר חשמל דחוף" | Hot/Human | Normalize city; safety handoff if risk |
| 12 | "תא נזילה שבוע הבא" | Warm | Normalize Tel Aviv and week urgency |
| 13 | "לא רוצה לתת תקציב" | Nurture/Warm | Continue without budget |
| 14 | "אתם מגיעים לאילת?" | Low fit | Out-of-area review |
| 15 | Voice note only | Nurture | Ask city and urgency in text |
| 16 | Photo only | Nurture | Ask what appears and desired help |
| 17 | "אפשר נציג?" | Human | Handoff immediately |
| 18 | "לא בוט בבקשה" | Human | Handoff immediately |
| 19 | Duplicate message ID | Same original | Do not create duplicate CRM record |
| 20 | "אני רוצה החזר כספי" | Support | Route to support |
| 21 | "חברה בעמ צריכה הנהלת חשבונות מ-01/07/2026" | Warm | Detect accounting/entity/start date |
| 22 | "כמה עולה טיפול לילד בן 8?" | Human | Escalate due to minor/medical context |
| 23 | "צריך חשבונית מס/קבלה" | Support | Route accounting/support |
| 24 | "תשלחו לי מבצע" | Nurture | Ask separate promotional consent |
| 25 | "יש ריח שרוף מהלוח חשמל" | Human | Safety message and urgent handoff |
| 26 | "צריך שיפוץ רמת גן תקציב 20000" | Hot/Warm | Detect city, budget, service; ask scope |
| 27 | "סתם בודק" | Nurture | Send info, no immediate sales call |
| 28 | "תתקשרו אלי ב-18:30" | Human/Warm | Capture callback time and handoff |
| 29 | "מחוץ לאזור שלכם אבל אשמח להמלצה" | Low fit | Offer checklist/referral |
| 30 | "האם המחיר כולל מעמ?" | Warm | Clarify VAT accurately |

## Acceptance checks

- At least 20 scenarios pass.
- Opt-out works in Hebrew and English.
- Sensitive cases route to human.
- City aliases normalize correctly.
- Budget extraction handles ₪, שח, ranges, and plain numbers in context.
- Phone normalization handles Israeli mobile formats.
- CSV export preserves Hebrew.
- CLI single and batch modes work.
- pytest suite passes.
