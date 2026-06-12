# API and Israeli Regulatory Reference

This reference lists Israeli regulatory topics and optional public-data interfaces that commonly affect customer-chat analysis for small businesses, freelancers, and consumer-facing teams. Use it to decide when chat insights require masking, escalation, or professional review.

The analyzer does not call external services by default. External APIs are optional enrichment sources. Verify current endpoint details, legal obligations, and professional requirements before production use.

## Reference matrix

| Topic | Type | Typical chat trigger | Analyzer action | Human review |
|---|---|---|---|---|
| Protection of Privacy Law, 5741-1981 | Regulation | customer identifiers, deletion requests, database mentions | Flag `legal_privacy` and sensitive patterns | Privacy owner or counsel |
| Protection of Privacy Regulations (Data Security), 5777-2017 | Regulation | export, storage, dashboard sharing | Mask and restrict raw data | Security/privacy owner |
| Privacy Protection Regulations (Transfer of Data to Databases Abroad), 5761-2001 | Regulation | external processors, cloud exports, offshore analytics | Minimize and review transfer basis | Privacy owner or counsel |
| Communications Law (Telecommunications and Broadcasting), 5742-1982, Section 30A | Regulation | unsubscribe, הסר, spam, mailing consent | Flag `legal_privacy` | Marketing/compliance owner |
| Consumer Protection Law, 5741-1981 | Regulation | cancellation, refund, misleading information, warranty | Flag `cancellation_refund` or `complaint` | Service manager or counsel |
| Consumer Protection Regulations (Cancellation of Transaction), 5771-2010 | Regulation | ביטול עסקה, החזר, התחרטתי | Route to cancellation workflow | Service manager or counsel |
| Value Added Tax Law, 5736-1975 | Regulation | חשבונית מס, מע״מ, קבלה, זיכוי | Flag `billing_tax` | Bookkeeper/accountant |
| Income Tax Ordinance | Regulation | receipt, withholding tax, business identifier | Flag `billing_tax` | Accountant |
| Equal Rights for Persons with Disabilities Regulations (Service Accessibility Adjustments), 5773-2013 | Regulation | accessibility requests, accessible service, phone alternative | Flag for service-accessibility review | Service/accessibility owner |
| data.gov.il CKAN API | Public data API | locality, public dataset enrichment | Optional enrichment only | Data owner |
| Bank of Israel exchange-rate service | Public data API | foreign-currency mentions in chats | Optional currency-context enrichment | Finance owner |


## Web-validated source status

The sources below were checked on 2026-06-03 and re-checked with a second source or query before this package was bundled.

| Area | Current status for this package |
|---|---|
| Israeli VAT | The standard Israeli VAT rate is 18% for chargeable events from 01/01/2025 onward. Keep the analyzer rate-free; use this only as a verified context note and re-check before issuing accounting text. |
| Privacy | Treat personal identifiers, deletion requests, database mentions, and external processor use as privacy-review triggers. Include Amendment 13 review in production checklists. |
| Data transfer abroad | Do not send raw chat exports to offshore processors or public APIs without a documented transfer basis, minimization, retention, and access review. |
| Spam/unsubscribe | Treat `הסר`, `ספאם`, and consent objections as suppression-workflow triggers, not as ordinary service tickets. |
| Cancellation/refund | Treat cancellation and refund phrases as routing triggers. Do not quote fixed legal outcomes unless approved by counsel or the service owner. |
| Accessibility | Route accessible-service or accessible-document requests to a service owner and offer an accessible contact path. |
| data.gov.il | CKAN `datastore_search` remains valid for optional public-data enrichment. |
| Bank of Israel | The quick `PublicApi/GetExchangeRates` endpoint is documented by the Bank of Israel; the newer series-database REST API is also official. Use exchange rates for context only unless finance approves source, date, and rounding. |
| Webhooks | No webhook feature is provided by this package; webhook event names are not applicable. |

See `references/verification-log.md` for source snippets, URLs, access date, and double-validation status.

## Regulatory handling contracts

For non-API regulations, treat each item as a policy rule that receives a normalized conversation and returns routing labels. The examples below use the analyzer output format rather than an external HTTP API.

### Privacy and data-security review

**Source to verify:** Israeli Protection of Privacy Law, 5741-1981; Protection of Privacy Regulations (Data Security), 5777-2017.

**Chat triggers**

- Phone number, email, Israeli ID-like value, card-like number.
- “תמחקו את הפרטים שלי”
- “איזה מידע שמרתם עליי?”
- “מאגר מידע”
- “הסכמה”
- “פרטיות”

**Analysis request**

```json
{
  "session_id": "privacy-001",
  "messages": [
    {
      "sender": "user",
      "text": "תמחקו את הפרטים שלי. המייל שלי dana@example.co.il",
      "timestamp": "03/06/2026 14:00:00"
    }
  ]
}
```

**Analysis response**

```json
{
  "primary_intent": "legal_privacy",
  "risk_flags": {
    "email": 1
  },
  "unresolved": true,
  "recommendations": [
    "Mask identifiers before exporting examples; retain only fields required for the analysis purpose."
  ]
}
```

**Error and escalation table**

| Condition | Severity | Handling |
|---|---:|---|
| Raw identifiers exported to a broad audience | High | Stop sharing, replace with masked export, record remediation. |
| Deletion/access request detected | High | Route to privacy owner; do not answer with generic bot text. |
| External analytics processor requested | High | Review transfer, purpose, retention, and access controls. |
| Only aggregated, masked trend counts exported | Low | Keep retention and access controls documented. |

### Marketing, unsubscribe, and spam review

**Source to verify:** Communications Law (Telecommunications and Broadcasting), 5742-1982, Section 30A.

**Chat triggers**

- “הסר”
- “אל תשלחו לי הודעות”
- “ספאם”
- “לא נתתי הסכמה”
- “unsubscribe”

**Analysis request**

```json
{
  "session_id": "marketing-001",
  "messages": [
    {
      "sender": "user",
      "text": "תפסיקו לשלוח לי פרסומות, זה ספאם. הסר."
    }
  ]
}
```

**Analysis response**

```json
{
  "primary_intent": "legal_privacy",
  "sentiment": {
    "label": "negative"
  },
  "resolution_status": "at_risk"
}
```

**Error and escalation table**

| Condition | Severity | Handling |
|---|---:|---|
| Customer requests removal from marketing | High | Route to suppression workflow immediately. |
| Chat combines purchase service and promotional consent | Medium | Separate service messages from marketing messages. |
| Bot continues marketing after unsubscribe signal | High | Stop automation and review campaign rules. |

### Consumer cancellation and refund review

**Source to verify:** Consumer Protection Law, 5741-1981; Consumer Protection Regulations (Cancellation of Transaction), 5771-2010.

**Chat triggers**

- “ביטול עסקה”
- “החזר”
- “זיכוי”
- “התחרטתי”
- “הטעיה”
- “לא קיבלתי את המוצר”

**Analysis request**

```json
{
  "session_id": "refund-001",
  "messages": [
    {
      "sender": "user",
      "text": "קניתי אתמול ב-240 ₪ ואני רוצה לבטל את העסקה ולקבל החזר."
    }
  ]
}
```

**Analysis response**

```json
{
  "primary_intent": "cancellation_refund",
  "sentiment": {
    "label": "neutral"
  },
  "unresolved": true,
  "recommendations": [
    "Show the cancellation policy, transaction date, and refund channel before asking for more details."
  ]
}
```

**Error and escalation table**

| Condition | Severity | Handling |
|---|---:|---|
| Cancellation request unanswered | High | Add to daily follow-up queue. |
| Customer alleges misleading information | High | Escalate to service manager. |
| Refund request lacks transaction date | Medium | Ask for date in `DD/MM/YYYY` format and purchase channel. |
| Bot quotes a fixed legal rule without review | High | Replace with approved policy text. |

### Tax, invoice, and accounting review

**Source to verify:** Value Added Tax Law, 5736-1975; Income Tax Ordinance; current guidance from the Israel Tax Authority and the business accountant.

**Verified context on 2026-06-03:** the standard VAT rate is 18% for relevant chargeable events from 01/01/2025 onward. Do not encode the rate in classifier logic. Use the rate only in approved finance templates that have a maintenance owner.

**Chat triggers**

- “חשבונית מס”
- “קבלה”
- “מע״מ”
- “עוסק פטור”
- “עוסק מורשה”
- “זיכוי”
- “ניכוי מס במקור”

**Analysis request**

```json
{
  "session_id": "tax-001",
  "messages": [
    {
      "sender": "user",
      "text": "אפשר חשבונית מס וקבלה על 1,250 ₪ ל-31/05/2026?"
    }
  ]
}
```

**Analysis response**

```json
{
  "primary_intent": "billing_tax",
  "top_terms": [["חשבונית", 1], ["קבלה", 1]],
  "recommendations": [
    "Route invoice, receipt, VAT, and refund questions to an approved finance workflow."
  ]
}
```

**Error and escalation table**

| Condition | Severity | Handling |
|---|---:|---|
| Customer asks for retroactive document correction | Medium | Route to bookkeeper/accountant. |
| Message contains business identifier or tax number | Medium | Mask before export. |
| Analyzer output hard-codes VAT rate | High | Remove fixed rate from classifier logic; keep any rate in a maintained finance template only. |
| Chat includes withholding-tax certificate terms | Medium | Route to accountant. |

### Service accessibility review

**Source to verify:** Equal Rights for Persons with Disabilities Regulations (Service Accessibility Adjustments), 5773-2013.

**Chat triggers**

- “נגיש”
- “הנגשה”
- “קשה לי לקרוא”
- “אפשר טלפון במקום צ׳אט?”
- “שפת סימנים”
- “מסמך נגיש”

**Analysis request**

```json
{
  "session_id": "accessibility-001",
  "messages": [
    {
      "sender": "user",
      "text": "קשה לי לקרוא באתר. אפשר לקבל מענה טלפוני?"
    }
  ]
}
```

**Analysis response**

```json
{
  "primary_intent": "unknown",
  "recommendations": [
    "Route accessibility-related messages to a service owner and offer an accessible contact path."
  ]
}
```

**Error and escalation table**

| Condition | Severity | Handling |
|---|---:|---|
| Accessibility request ignored | High | Route to service owner. |
| Customer asks for accessible document | Medium | Provide approved accessible format. |
| Chatbot loops without alternative contact path | High | Add escalation path. |

## Optional public-data API enrichment

External enrichment is optional. Keep it outside the core analyzer unless the business has a documented reason to enrich chat data.

### data.gov.il CKAN API

Use for optional lookup of public datasets, such as locality lists or public registers that a business already has a lawful reason to use.

**Example request**

```http
GET https://data.gov.il/api/3/action/datastore_search?resource_id=<resource-id>&limit=5
Accept: application/json
```

**Example response**

```json
{
  "success": true,
  "result": {
    "records": [
      {
        "_id": 1,
        "שם_ישוב": "תל אביב - יפו",
        "סמל_ישוב": 5000
      }
    ],
    "limit": 5,
    "total": 1
  }
}
```

**Adapter guidance**

```python
def enrich_locality(record: dict) -> dict:
    return {
        "locality_name": record.get("שם_ישוב"),
        "locality_code": record.get("סמל_ישוב")
    }
```

**Error table**

| HTTP/API condition | Meaning | Handling |
|---|---|---|
| `success=false` | CKAN action failed | Log action and retry only if transient. |
| `404` | Dataset or resource ID changed | Update resource ID from the official catalog. |
| `429` | Rate limit or throttling | Back off and cache approved lookups. |
| unexpected schema | Dataset columns changed | Fail closed; do not enrich silently. |

### Bank of Israel exchange-rate service

Use only when chats mention foreign-currency payments and finance needs context. Do not convert amounts for binding quotes unless finance approved the source, date, and rounding method.

Two official retrieval paths were validated on 2026-06-03:

- Quick JSON API: `https://www.boi.org.il/PublicApi/GetExchangeRates?asJson=true`
- Series database REST API: `https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/`

Prefer the series database API when historical filtering, CSV output, or metadata labels are required. Keep the quick JSON API for simple current-rate context.

**Example request**

```http
GET https://www.boi.org.il/PublicApi/GetExchangeRates?asJson=true
Accept: application/json
```

**Example response**

```json
{
  "exchangeRates": [
    {
      "key": "USD",
      "currentExchangeRate": 3.70,
      "currentChange": 0.15,
      "lastUpdate": "2026-06-03"
    }
  ]
}
```

**Adapter guidance**

```python
def attach_currency_context(chat_amount: dict, rate_record: dict) -> dict:
    return {
        "original_amount": chat_amount,
        "rate_currency": rate_record["key"],
        "rate_date": rate_record["lastUpdate"],
        "rate_value": rate_record["currentExchangeRate"],
        "note": "Context only; not a binding quote."
    }
```

**Error table**

| HTTP/API condition | Meaning | Handling |
|---|---|---|
| `503` or timeout | Service unavailable | Keep original chat amount; retry later. |
| missing currency | Currency not published in response | Leave unenriched and flag for finance review. |
| stale date | Rate date differs from transaction date | Do not use for binding calculation. |
| schema change | Field names changed | Stop enrichment and update adapter. |

## Internal analyzer API

### `ChatDataAnalyzerClient.analyze_text(text)`

**Request**

```python
analyzer.analyze_text("המשלוח לא הגיע ואני רוצה החזר דחוף")
```

**Response**

```json
{
  "language": "he",
  "sentiment": {
    "label": "negative",
    "score": -0.5
  },
  "intents": [
    {
      "intent": "cancellation_refund",
      "score": 2.0,
      "hits": ["החזר"]
    }
  ],
  "risk_flags": {},
  "top_terms": [["משלוח", 1], ["הגיע", 1]],
  "anonymized_text": "המשלוח לא הגיע ואני רוצה החזר דחוף"
}
```

**Errors**

| Exception | Cause | Handling |
|---|---|---|
| `ValidationError` | Invalid data shape or timestamp | Fix input and rerun. |
| `json.JSONDecodeError` | Bad JSON/JSONL file | Validate export syntax. |
| `UnicodeDecodeError` | Wrong file encoding | Save as UTF-8. |

### `ChatDataAnalyzerClient.analyze_dataset(conversations)`

**Request**

```python
dataset = analyzer.analyze_dataset([
    {
        "session_id": "s1",
        "messages": [
            {"sender": "user", "text": "אפשר לקבוע תור?"},
            {"sender": "bot", "text": "כן, איזה יום נוח לך?"}
        ]
    }
])
```

**Response**

```json
{
  "conversation_count": 1,
  "total_messages": 2,
  "intent_distribution": {
    "appointment": 1
  },
  "drop_off_rate": 0.0,
  "escalation_rate": 0.0,
  "unresolved_rate": 0.0
}
```

## Compliance-safe implementation rules

1. Keep external enrichment optional and documented.
2. Never send raw chat logs to public APIs for enrichment.
3. Prefer aggregate reporting over raw examples.
4. Mask identifiers before using examples in tickets, presentations, or external vendor reviews.
5. Keep legal, accounting, cancellation, and privacy wording in approved templates rather than in classifier logic.
6. Re-check official Israeli sources before relying on a rule in production.
