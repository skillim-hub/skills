# API and regulation reference

This helper is offline-first. It does not call Instagram, TikTok, YouTube, Meta, Google, Israel Tax Authority, or any government service directly. Use this reference to map local files, internal systems, and future integrations to the client data model.

Web validation on 03/06/2026 confirmed the standard Israeli VAT rate as 18% from 01/01/2025. Keep the rate as a planning aid only. Recheck official Tax Authority publications before issuing invoices, approving creator payments, or launching production workflows.

## Local module API

Import the helper after installation:

```python
from influencer_collaboration_client import (
    InfluencerCollaborationClient,
    InfluencerProfile,
    CampaignBrief,
    CampaignMetric,
)
```

### `InfluencerProfile`

Request object:

```json
{
  "handle": "haifa_food",
  "display_name": "דנה",
  "platform": "instagram",
  "niche": "אוכל בחיפה",
  "followers": 18000,
  "avg_views": 9000,
  "avg_likes": 620,
  "avg_comments": 80,
  "location": "חיפה",
  "audience_israel_pct": 0.91,
  "audience_age_min": 21,
  "audience_age_max": 44,
  "contact_email": "creator@example.test",
  "past_brand_conflicts": [],
  "notes": "קהל צפוני חזק"
}
```

Validation errors:

| Field | Error | Fix |
|---|---|---|
| `handle` | `handle must not be empty` | Provide a non-empty handle without URL noise |
| `followers` | `followers must be non-negative` | Use zero when unknown |
| `avg_views` and engagement fields | `metrics must be non-negative` | Clean imported analytics |
| `audience_israel_pct` | `audience_israel_pct must be between 0 and 1` | Convert percentages to decimals |
| age range | `audience age range is invalid` | Ensure maximum age is not below minimum age |

### `CampaignBrief`

Request object:

```json
{
  "business_name": "קפה שכונתי",
  "product_or_service": "תפריט בוקר חדש",
  "goal": "foot_traffic",
  "target_locations": ["חיפה"],
  "target_segments": ["food"],
  "budget_ils": 6500,
  "start_date": "10/06/2026",
  "end_date": "25/06/2026",
  "required_disclosure": "פרסומת",
  "usage_rights_days": 30,
  "deliverables": ["reel", "story"],
  "coupon_code": "HAIFA10"
}
```

Validation errors:

| Field | Error | Fix |
|---|---|---|
| `business_name` | `business_name is required` | Add the public business name |
| `product_or_service` | `product_or_service is required` | Describe the offer |
| `budget_ils` | `budget_ils must be positive` | Use a positive ₪ amount |
| `start_date`, `end_date` | `end_date must be on or after start_date` | Correct dates |
| `usage_rights_days` | `usage_rights_days must be non-negative` | Use zero when no reuse is granted |
| `deliverables` | `at least one deliverable is required` | Add story, reel, post, video, or article |

### Score response

Call:

```python
client = InfluencerCollaborationClient()
score = client.score_profile(profile, brief)
```

Response example:

```json
{
  "handle": "haifa_food",
  "total_score": 88.42,
  "fit_score": 100.0,
  "engagement_score": 98.75,
  "israel_relevance_score": 91.0,
  "budget_score": 100.0,
  "risk_score": 100.0,
  "recommendation": "shortlist",
  "reasons": [
    "niche matches food",
    "estimated local reach 8190",
    "estimated fee ₪1,110"
  ]
}
```

### Outreach response

Call:

```python
message = client.generate_outreach(profile, brief, tone="professional")
```

Response example:

```json
{
  "subject": "הצעה לשיתוף פעולה מסחרי עם קפה שכונתי",
  "body": "שלום דנה, יש התאמה אפשרית בין הקהל שלך לבין קפה שכונתי...",
  "language": "he",
  "disclosure_line": "גילוי נדרש בפרסום: פרסומת",
  "follow_up_body": "שלום דנה, מעקב קצר לגבי ההצעה..."
}
```

### Disclosure validation

Call:

```python
valid, issues = client.validate_disclosure("פרסומת בשיתוף עסק מקומי. קוד הטבה LOCAL10")
```

Response:

```json
{
  "valid": true,
  "issues": []
}
```

Potential issues:

| Issue | Meaning | Fix |
|---|---|---|
| `missing clear commercial disclosure` | No clear Hebrew sponsorship wording found | Add `פרסומת`, `ממומן`, `בשיתוף`, or equivalent clear wording |
| `disclosure appears too late` | Disclosure is buried after the opening section | Move disclosure to the start |
| `English-only disclosure is not enough for Hebrew audience` | English hashtag alone is insufficient for Hebrew content | Add Hebrew wording |

### Campaign summary response

Input:

```json
[
  {
    "handle": "haifa_food",
    "spend_ils": 2400,
    "impressions": 38000,
    "views": 16000,
    "clicks": 820,
    "leads": 95,
    "sales": 34,
    "revenue_ils": 5100,
    "date_reported": "30/06/2026"
  }
]
```

Output:

```json
{
  "spend_ils": 2400,
  "impressions": 38000,
  "views": 16000,
  "clicks": 820,
  "leads": 95,
  "sales": 34,
  "revenue_ils": 5100,
  "cpm_ils": 63.16,
  "cpc_ils": 2.93,
  "cpl_ils": 25.26,
  "cost_per_sale_ils": 70.59,
  "roas": 2.13,
  "conversion_rate": 0.0415,
  "recommendations": ["keep the best creators and negotiate content reuse"]
}
```

## CSV import format

Required columns:

```csv
handle,display_name,platform,niche,followers,avg_views,avg_likes,avg_comments,location,audience_israel_pct
haifa_food,דנה,instagram,אוכל בחיפה,18000,9000,620,80,חיפה,0.91
```

Optional columns:

| Column | Type | Note |
|---|---|---|
| `audience_age_min` | integer | Defaults to 18 |
| `audience_age_max` | integer | Defaults to 54 |
| `contact_email` | string | Use only when permission exists |
| `past_brand_conflicts` | pipe-separated string | Example: `brand_a|brand_b` |
| `notes` | string | Useful for manual review |

## Verified Israeli rate and source notes

| Check | Verified status on 03/06/2026 | Operational use |
|---|---|---|
| Standard VAT rate | 18% from 01/01/2025, double-confirmed against Tax Authority and Knesset sources | Use `DEFAULT_ISRAEL_VAT_RATE = 0.18` only for planning notes; do not replace accounting review |
| Exempt-dealer threshold | Not encoded as a constant because thresholds can change by tax year | Ask the creator for current VAT status and documentation rather than guessing |
| Invoice allocation service | Official Tax Authority service exists for requesting allocation numbers for tax invoices | Do not embed endpoint hosts or paths in this offline helper; integrate only after official technical onboarding |
| Webhook event names | Not applicable | No Israeli government or platform webhook is called by this package |
| Official influencer registry API | Not found and not referenced | Use manual sourcing, platform exports, or approved vendor exports instead of claiming official registry coverage |

## Israeli regulation checklist

Validate the following against current official sources before launch.

| Area | Israeli source to check | Operational implication |
|---|---|---|
| Commercial disclosure | Consumer Protection Law, 5741-1981, and Consumer Protection Authority guidance on advertising, misleading advertising, ratings, reviews, bloggers, and influencers | Require clear Hebrew disclosure such as `פרסומת`, `ממומן`, `בשיתוף`, or `שיתוף פעולה מסחרי` near the start |
| Privacy and leads | Protection of Privacy Law, 5741-1981, including database and direct-mailing duties where relevant | Collect only needed lead data, explain use, protect files, and avoid unnecessary sharing |
| Privacy reform | Protection of Privacy Law Amendment 13 and related Privacy Protection Authority guidance | Review data minimization, security duties, and database obligations |
| Tax documentation | Value Added Tax Law, Income Tax Ordinance, Israel Tax Authority bookkeeping instructions, and Israel Invoices allocation-number services where relevant | Confirm invoice or receipt handling, VAT status, withholding duties, and allocation-number duties where relevant |
| Spam and direct marketing | Communications Law section 30A | Do not add leads to marketing messages without lawful consent |
| Accessibility | Equal Rights for Persons with Disabilities regulations and Israeli accessibility standard practice | Consider captions, readable text, and accessible landing pages |
| Minors | Youth employment, privacy, and advertising restrictions where minors appear or are targeted | Require additional review and consent process |
| Health or supplements | Public Health regulations, Ministry of Health guidance, and claim substantiation rules | Avoid medical claims without approval and evidence |
| Financial services | Securities, credit, insurance, banking, and investment-advice restrictions where relevant | Avoid unlicensed advice or performance promises |
| Lotteries and promotions | Penal Law restrictions and permit requirements for prize promotions | Check whether a permit or official rules are needed |
| Alcohol | Restrictions on advertising alcoholic beverages | Review age targeting and content restrictions |

## External platform fields

When exporting data from a social platform or an internal spreadsheet, map fields as follows:

| External field | Local field | Transformation |
|---|---|---|
| Username | `handle` | Strip URL and leading symbol |
| Full name | `display_name` | Preserve Hebrew spelling |
| Platform | `platform` | Lowercase allowed value |
| Category | `niche` | Keep free text |
| Followers | `followers` | Integer |
| Views per post | `avg_views` | Average last 10 to 20 posts |
| Likes per post | `avg_likes` | Average comparable content |
| Comments per post | `avg_comments` | Exclude giveaways when possible |
| Top country Israel | `audience_israel_pct` | Convert 91 percent to 0.91 |
| City | `location` | Prefer city or region |
| Brand conflicts | `past_brand_conflicts` | Use list or pipe-separated values |

## Error table for integrations

| Scenario | Symptom | Recommended handling |
|---|---|---|
| Platform export missing views | `avg_views` equals zero | Fall back to follower-based reach estimate and mark manual review |
| Audience screenshot outdated | Date older than 90 days | Request updated screenshot |
| Imported percent uses `91` instead of `0.91` | Validation fails or score overstates relevance | Divide by 100 before import |
| Duplicate creator appears on multiple platforms | Multiple rows with same person | Score separately, then consolidate by business objective |
| Paid partnership term absent | Disclosure validation fails | Add exact Hebrew wording to content approval |
| Coupon code reused by multiple creators | Attribution impossible | Generate one code per creator |
| Lead data exported without consent field | Privacy risk | Add consent capture and retention rules before launch |
| Invoice status unknown | Payment delay | Add supplier details before publication |
