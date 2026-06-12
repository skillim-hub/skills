# Test Scenarios

Use these scenarios for manual QA, regression tests, prompt checks, or acceptance reviews. Each scenario includes input, expected labels, and notes. Adjust expectations only after reviewing real business chats.

## Scenario table

| # | Scenario | Input text | Expected primary intent | Expected sentiment | Notes |
|---:|---|---|---|---|---|
| 1 | Invoice request | אפשר לקבל חשבונית מס על 350 ₪? | `billing_tax` | neutral | Route to finance workflow. |
| 2 | Receipt request | אני צריכה קבלה על התשלום מאתמול | `billing_tax` | neutral | Use DD/MM/YYYY when asking for date. |
| 3 | VAT question | המחיר כולל מע״מ? | `billing_tax` | neutral | Avoid hard-coded VAT answer unless approved. |
| 4 | Appointment scheduling | אפשר לקבוע תור ליום שני בבוקר? | `appointment` | neutral | Offer two concrete slots. |
| 5 | Appointment move | צריך להזיז את התור ל-24/06/2026 | `appointment` | neutral | Confirm date format. |
| 6 | Delivery delay | המשלוח לא הגיע ואני מחכה כבר שבוע | `delivery` | negative | Review logistics and tracking. |
| 7 | Delivery tracking | יש מספר מעקב לחבילה? | `delivery` | neutral | Provide tracking action. |
| 8 | Refund demand | רוצה החזר, המוצר לא הגיע | `cancellation_refund` or `delivery` | negative | Combined logistics/refund case. |
| 9 | Cancellation request | אני רוצה לבטל את העסקה | `cancellation_refund` | neutral | Route to cancellation workflow. |
| 10 | Product stock | יש את הדגם הזה במלאי בצבע שחור? | `product_info` | neutral | Sales/product info. |
| 11 | Warranty | כמה זמן אחריות יש על המוצר? | `product_info` | neutral | Avoid legal conclusion; use approved warranty text. |
| 12 | Complaint | השירות גרוע ואני רוצה לדבר עם מנהל | `complaint` or `human_agent` | negative | Escalate. |
| 13 | Technical login | לא מצליח להתחבר לאפליקציה | `technical_support` | negative | Support workflow. |
| 14 | Password reset mixed language | ה-login לא עובד, reset password please | `technical_support` | neutral/negative | Mixed language. |
| 15 | Sales lead | מעוניינת בהצעת מחיר ודמו | `sales_lead` | neutral | Sales follow-up. |
| 16 | Human agent | אפשר לדבר עם נציג? | `human_agent` | neutral | Escalate immediately. |
| 17 | Privacy deletion | תמחקו את הפרטים שלי מהמערכת | `legal_privacy` | neutral/negative | Privacy owner. |
| 18 | Unsubscribe | הסר אותי מרשימת התפוצה, זה ספאם | `legal_privacy` | negative | Marketing suppression. |
| 19 | Sensitive email | המייל שלי dana@example.co.il | `unknown` | neutral | `risk_flags.email = 1`. |
| 20 | Sensitive phone | תחזרו אליי ל-052-123-4567 | `human_agent` or `unknown` | neutral | `risk_flags.phone = 1`. |
| 21 | Israeli ID-like value | תז 123456782 | `unknown` | neutral | `risk_flags.israeli_id_like = 1`. |
| 22 | Card-like value | שילמתי בכרטיס 4111 1111 1111 1111 | `billing_tax` or `unknown` | neutral | `risk_flags.credit_card_like = 1`. |
| 23 | Resolved positive | תודה רבה, הסתדר. שירות מעולה | `small_talk` or prior intent | positive | Resolution should be `resolved` in conversation context. |
| 24 | Sarcasm | איזה יופי, שוב האתר נפל | `technical_support` | neutral/negative | Manual review; sarcasm may be missed. |
| 25 | Broadcast noise | ההודעות והשיחות מוצפנות מקצה לקצה | `unknown` | neutral | Filter WhatsApp system lines. |
| 26 | Accessibility | קשה לי לקרוא באתר, אפשר מענה טלפוני? | `unknown` or custom accessibility | neutral | Escalate to accessibility/service owner. |
| 27 | Legal threat | אם לא תחזירו לי כסף אני פונה לעורך דין | `cancellation_refund` or `legal_privacy` | negative | Manager/legal review. |
| 28 | Duplicate charge | חויבתי פעמיים באשראי | `billing_tax` | negative | Finance escalation. |
| 29 | Price before purchase | כמה עולה החבילה החודשית? | `sales_lead` or `product_info` | neutral | Sales follow-up. |
| 30 | Mixed resolved | הייתה תקלה אבל עכשיו עובד, תודה | `technical_support` | positive/neutral | Context should reduce urgency. |

## Full conversation scenarios

### 1. Resolved invoice request

```json
{
  "session_id": "case-001",
  "messages": [
    {"sender": "user", "text": "שלום, אפשר לקבל חשבונית מס על 350 ₪?", "timestamp": "2026-06-01T09:00:00"},
    {"sender": "bot", "text": "כן. נא לשלוח שם עסק ומספר עוסק.", "timestamp": "2026-06-01T09:00:08"},
    {"sender": "user", "text": "תודה רבה, הסתדר.", "timestamp": "2026-06-01T09:01:00"}
  ]
}
```

Expected:

```json
{
  "primary_intent": "billing_tax",
  "resolution_status": "resolved",
  "unresolved": false,
  "first_response_seconds": 8
}
```

### 2. Delivery complaint with escalation

```json
{
  "session_id": "case-002",
  "messages": [
    {"sender": "user", "text": "המשלוח לא הגיע ואני רוצה נציג עכשיו", "timestamp": "2026-06-02T18:00:00"},
    {"sender": "bot", "text": "אפשר מספר הזמנה?", "timestamp": "2026-06-02T18:02:00"}
  ]
}
```

Expected:

```json
{
  "primary_intent": "delivery",
  "sentiment": "negative",
  "escalation_requested": true,
  "resolution_status": "needs_human_review"
}
```

### 3. Open final question

```json
{
  "session_id": "case-003",
  "messages": [
    {"sender": "bot", "text": "שלום, איך אפשר לעזור?"},
    {"sender": "user", "text": "כמה עולה משלוח לאילת?"}
  ]
}
```

Expected:

```json
{
  "drop_off": true,
  "unresolved": true,
  "resolution_status": "open_question"
}
```

### 4. Privacy request with identifier

```json
{
  "session_id": "case-004",
  "messages": [
    {"sender": "user", "text": "תמחקו את הפרטים שלי. המייל שלי dana@example.co.il"}
  ]
}
```

Expected:

```json
{
  "primary_intent": "legal_privacy",
  "risk_flags": {"email": 1},
  "unresolved": true
}
```

### 5. CSV import scenario

Input:

```csv
session_id,sender,text,timestamp
s1,user,"אפשר לקבוע תור ל-03/06/2026?",03/06/2026 09:00:00
s1,bot,"כן, פנוי ב-10:30 או 12:00",03/06/2026 09:01:00
s2,user,"השירות גרוע, רוצה החזר",03/06/2026 10:00:00
```

Expected:

- two conversations
- `s1` primary intent `appointment`
- `s2` negative sentiment
- dataset unresolved rate greater than zero

## Regression checks

Run these checks after changing lexicons, custom intents, or timestamp parsing:

1. Hebrew text remains unescaped in JSON output.
2. `billing_tax` still catches חשבונית, קבלה, מע״מ.
3. `appointment` still catches תור, פגישה, להזיז.
4. `delivery` still catches משלוח, שליח, מספר מעקב.
5. `cancellation_refund` still catches ביטול, החזר, זיכוי.
6. `technical_support` still catches תקלה, התחברות, סיסמה.
7. `legal_privacy` still catches פרטיות, הסר, ספאם.
8. Phone masking does not remove regular prices.
9. Israeli ID-like detection validates checksum.
10. Card-like detection validates Luhn checksum.
11. DD/MM/YYYY timestamps parse correctly.
12. Missing timestamps do not crash response-time metrics.
13. A final customer question sets `unresolved`.
14. A resolved “תודה, הסתדר” conversation is not marked unresolved.
15. Custom intents can outrank default intents when they have stronger matches.
16. CSV grouping by `session_id` works.
17. JSONL input works line by line.
18. Async client returns the same aggregate count as sync client.
19. Drop-off excludes conversations ending with bot/business reply.
20. Recommendations are non-empty.

## Manual sampling checklist

For every production run, sample:

- 10 negative chats.
- 10 unresolved chats.
- 10 chats from the top intent.
- 5 chats with sensitive-data flags.
- 5 chats labeled `unknown`.
- Every chat with legal/privacy terms in small datasets.

Record:

```text
Sample date: DD/MM/YYYY
Reviewer:
Dataset period:
False positives:
False negatives:
New terms to add:
Template changes:
Owner:
Next review:
```

## Acceptance threshold examples

Use practical thresholds rather than perfection:

| Metric | Initial target |
|---|---:|
| Top-intent manual precision | 80%+ |
| Sensitive phone/email masking | 95%+ on sampled exports |
| Unresolved queue recall | High recall preferred over low false positives |
| Sarcasm detection | Manual review required |
| Response-time calculation | 90%+ of conversations with timestamps |
| Weekly dashboard consistency | Same filters and same taxonomy version |

## Scenario generation template

Create new scenarios using this structure:

```json
{
  "id": "custom-001",
  "business_context": "clinic / store / freelancer / accountant / delivery",
  "input": "customer message or full conversation",
  "expected_intent": "intent_name",
  "expected_sentiment": "positive|neutral|negative",
  "expected_flags": {},
  "manual_review_required": true,
  "notes": "why this matters"
}
```
