# API and Regulation Reference

This reference lists Israeli legal/regulatory considerations and practical data-source patterns for reputation monitoring. It is not legal advice. Use qualified Israeli review for production systems that process personal data, sensitive data, minors, medical issues, regulated industries, financial claims, automated decisions, or serious public allegations.

## Israeli legal and regulatory map

| Area | Israeli source | Practical relevance |
|---|---|---|
| Privacy and databases | Protection of Privacy Law, 5741-1981 | Personal data collection, purpose limitation, retention, database duties, direct-mailing concerns. |
| Data security | Protection of Privacy Regulations (Data Security), 5777-2017 | Access controls, audit logs, incident handling, outsourcing, deletion, backups. |
| Direct marketing/spam | Communications Law (Telecommunications and Broadcasting), Section 30A | Do not use collected mentions to send unsolicited marketing messages. |
| Consumer protection | Consumer Protection Law, 5741-1981; Consumer Protection and Fair Trade Authority | Pricing, refunds, misleading advertising, warranties, cancellation, stock claims. |
| Defamation | Defamation Prohibition Law, 5725-1965 | Public accusations and replies that may harm reputation. Preserve evidence and avoid threats without review. |
| Copyright | Copyright Law, 5768-2007 | Screenshots, copied comments, images, and report excerpts. Prefer links and minimal excerpts. |
| Accessibility | Equal Rights for Persons with Disabilities Law and accessibility duties | Complaints about websites, service access, captions, or screen-reader support. |
| Health/safety | Ministry of Health and sector-specific duties | Food, clinics, cosmetics, allergens, poisoning, injury, sanitation. |
| Tax/accounting | Israel Tax Authority rules for invoices and receipts | Complaints about חשבונית מס, קבלה, זיכוי, חיוב כפול, מע״מ. |
| Employment/privacy | Labor and privacy rules | Mentions naming employees require minimization and internal handling. |

## Platform-source guidance

### Facebook and Instagram public content

Use official Meta tooling, approved vendor access, permitted public-page exports, or manually supplied evidence. Do not collect private groups or personal profiles without permission.

Normalized record:

```json
{
  "source": "facebook",
  "date": "24/06/2026",
  "url": "https://www.facebook.com/example/posts/123",
  "author": "public-page-user",
  "text": "השירות היה מצוין אבל חיכיתי הרבה זמן למענה",
  "engagement": 18
}
```

Error table:

| Error | Meaning | Action |
|---|---|---|
| `PERMISSION_DENIED` | Missing page, group, or app permission | Re-check lawful access. Do not bypass. |
| `RATE_LIMITED` | Too many requests | Back off and lower frequency. |
| `CONTENT_UNAVAILABLE` | Deleted, restricted, or private content | Store only permitted reference. |
| `FIELD_NOT_AVAILABLE` | API/export does not expose a field | Remove field or use an approved export. |

### X / Twitter

Use approved API access or authorized exports. Minimize profile metadata.

Example request pattern:

```http
GET /2/tweets/search/recent?query=("שם העסק" OR "BusinessName") lang:he -is:retweet
Authorization: Bearer <token>
```

Normalized response:

```json
{
  "source": "x",
  "date": "24/06/2026",
  "url": "https://x.com/user/status/123",
  "author": "@user",
  "text": "לא להתקרב, משלוח איחר בשעתיים",
  "engagement": 27
}
```

Error table:

| HTTP status | Meaning | Action |
|---:|---|---|
| 400 | Invalid query syntax | Escape quotes and simplify variants. |
| 401 | Token missing or invalid | Rotate token and verify environment variables. |
| 403 | Access tier lacks endpoint | Use permitted endpoint or export. |
| 429 | Rate limit | Use exponential backoff and batching. |

### TikTok public comments

Prefer approved business tools, platform exports, or vendor integrations. Do not automate collection from private accounts.

```json
{
  "source": "tiktok",
  "date": "24/06/2026",
  "url": "https://www.tiktok.com/@brand/video/123",
  "author": "public-commenter",
  "text": "הקופון לא עובד וזה ממש מבאס",
  "engagement": 8
}
```

Common issues:

| Issue | Cause | Mitigation |
|---|---|---|
| Partial thread | Export contains top-level comments only | Mark context incomplete. |
| Emoji-only comment | Sentiment hidden in emoji | Preserve emoji and set low confidence. |
| Missing duet/stitch context | Related video not included | Manual review. |

### News comments

Collect only from permitted exports, public APIs, RSS/comment endpoints where available, or manual evidence. Treat anonymous one-line comments as lower confidence unless repeated or highly engaged.

```json
{
  "source": "news_comment",
  "date": "24/06/2026",
  "url": "https://news.example/article/123#comment-9",
  "author": "anonymous",
  "text": "עוד עסק שמבטיח מבצעים ואז אין מלאי",
  "engagement": 3
}
```

### Reviews and Google Business Profile exports

Use tools available to the business. Keep replies professional and do not disclose customer details.

```json
{
  "source": "review",
  "date": "24/06/2026",
  "author": "public-reviewer",
  "rating": 2,
  "text": "האוכל טוב אבל המקום לא נקי",
  "url": "internal-review-export-row-42"
}
```

## Generic local schema

```json
{
  "mentions": [
    {
      "date": "24/06/2026",
      "source": "facebook",
      "brand": "המאפייה של דנה",
      "author": "@customer",
      "url": "https://example.com/post/123",
      "text": "טעים מאוד אבל השירות איטי",
      "engagement": 12,
      "topic": "service",
      "branch": "תל אביב"
    }
  ]
}
```

## Internal API wrapper example

Request:

```http
POST /v1/reputation/analyze
Content-Type: application/json
Authorization: Bearer <internal-token>
```

```json
{
  "locale": "he-IL",
  "currency": "ILS",
  "date_format": "DD/MM/YYYY",
  "mentions": [
    {
      "date": "24/06/2026",
      "source": "facebook",
      "text": "שירות מעולה אבל חיכינו המון זמן",
      "engagement": 6
    }
  ]
}
```

Response:

```json
{
  "summary": {
    "total": 1,
    "positive": 0,
    "mixed": 1,
    "neutral": 0,
    "negative": 0,
    "urgent": 0
  },
  "items": [
    {
      "sentiment": "mixed",
      "score": -0.05,
      "risk_score": 25,
      "topics": ["support"],
      "recommended_action": "Reply if public response would help; route to support"
    }
  ]
}
```

## Local helper error table

| Code | Cause | Fix |
|---|---|---|
| `INPUT_MISSING` | File path does not exist | Check path and working directory. |
| `UNSUPPORTED_FORMAT` | File is not CSV, JSON, or JSONL | Convert file format. |
| `TEXT_FIELD_MISSING` | No text field was found | Add `text` column or pass `--text-field`. |
| `BAD_ENCODING` | File is not UTF-8 readable | Export as UTF-8. |
| `EMPTY_DATASET` | No usable rows | Check filters and export. |
| `INVALID_ENGAGEMENT` | Engagement is not numeric | Clean column. |
| `WRITE_FAILED` | Output path not writable | Choose writable output path. |

## Data protection controls

## Web-validated 2026 notes

The following notes were validated against official or primary sources on 03/06/2026 and are operational guardrails for Israeli reputation monitoring.

| Topic | Current validated guidance |
|---|---|
| Israeli VAT | Standard VAT is 18% from 01/01/2025 and remains the validated 2026 rate. When price complaints mention `מע״מ`, `מחיר כולל`, or `₪`, route to accounting or consumer-protection review. |
| Price display | Israeli consumer-protection guidance requires presenting an inclusive price for goods or services offered to consumers, subject to legal exceptions. |
| Privacy | The Privacy Protection Authority is the official regulator for personal information in digital databases. Treat social-monitoring exports as personal-data risk unless minimized and redacted. |
| Data security | The Privacy Protection Regulations (Data Security), 5777-2017 apply to private and public sectors and require organizational controls for database security. |
| Direct marketing | Section 30A of the Communications Law is relevant when monitoring output is used for marketing; do not convert collected mentions into unsolicited advertising. |
| Facebook/Page comments | Use Pages API, Graph API, Page permissions, webhooks, or permitted exports. Do not bypass Page ownership, permissions, private groups, or unavailable fields. |
| X/Twitter search | The recent search endpoint is `GET https://api.x.com/2/tweets/search/recent`; it searches the last 7 days and is subject to current access tier and rate limits. |
| TikTok comments | TikTok comment access is scope-dependent. Use approved Research API, TikTok API for Business comment endpoints where applicable, approved vendors, or manual exports. Do not describe TikTok as offering a general unrestricted public-comment firehose. |
| Google Business Profile reviews | The Business Profile APIs can list, get, reply to, and delete review replies for verified locations, and notifications can cover new or updated reviews. |
| News comments | No single Israeli official API covers news comments. Use site-provided feeds, permitted exports, licensed monitoring vendors, or manual evidence; label context as partial when thread data is incomplete. |

Minimum controls:

- Store only mention text, source, timestamp, URL/reference, labels, and operational notes.
- Redact phone numbers, emails, Israeli ID-like numbers, addresses, and health details unless needed for a case.
- Restrict access to staff with a business need.
- Maintain a separate escalation queue for legal, safety, privacy, media, and regulator items.
- Document lawful source, collection purpose, retention period, deletion process, and processors.
- Mark high-impact automated classifications for human review.

## Retention suggestions

| Data type | Suggested retention | Notes |
|---|---:|---|
| Aggregate metrics | 24 months | Avoid personal text. |
| Routine public mention | 6-12 months | Shorter when possible. |
| Resolved support case | Business/legal need | Minimize fields. |
| Legal/safety/privacy incident | Per qualified advice | Preserve evidence carefully. |
| Raw export file | Delete after processing when possible | Keep normalized minimum. |

## Evidence handling

1. Save public URL and timestamp.
2. Preserve exact text only when lawful and necessary.
3. Capture screenshot only when permitted and needed.
4. Redact irrelevant personal data before wider sharing.
5. Track access.
6. Add notes separately instead of editing evidence.

## Hebrew accounting and consumer terms

| Term | Meaning | Handling |
|---|---|---|
| `חשבונית מס` | Tax invoice | Route to accounting. |
| `קבלה` | Receipt | Route to billing/support. |
| `זיכוי` | Credit/refund | Check transaction record. |
| `חיוב כפול` | Double charge | Higher risk; respond quickly. |
| `מחיר כולל מע״מ` | VAT-inclusive price | Verify ad and invoice consistency. |
| `ביטול עסקה` | Transaction cancellation | Check consumer-law duties and policy. |
| `אחריות` | Warranty | Route to service owner. |
