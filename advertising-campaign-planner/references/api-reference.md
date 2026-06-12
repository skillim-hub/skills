# Israeli Regulatory and Data Reference

This is a non-API planning skill. Use this file as the reference layer for Israeli regulatory sources, structured request/response contracts, validation errors, and compliance mappings. Verify current text before launch because laws, regulator positions, and platform rules can change.

## Israeli sources and checks

| Area | Source to verify | Campaign planning use |
|---|---|---|
| Consumer advertising | Consumer Protection Law, 5741-1981; Consumer Protection Regulations; Israeli Consumer Protection and Fair Trade Authority publications | Misleading advertising, price, discount, identity, availability, warranty, cancellation, material terms |
| Direct marketing | Communications Law (Telecommunications and Broadcasts), section 30A | Consent, sender identity, unsubscribe, commercial message wording |
| Privacy | Protection of Privacy Law, 5741-1981; Protection of Privacy Regulations, including data security regulations; Privacy Protection Authority guidance | Lead forms, remarketing, customer-list uploads, cookies, database duties, purpose limitation |
| Accessibility | Equal Rights for Persons with Disabilities Law; Service Accessibility Regulations | Landing pages, forms, documents, videos, contact channels |
| VAT and tax | VAT Law; Israel Tax Authority guidance | Consumer price display, VAT wording, invoice/tax-saving claims |
| Health and cosmetics | Ministry of Health rules and professional requirements | Medical/cosmetic/supplement claims, before/after, professional licensing |
| Finance, credit, insurance, securities | Bank of Israel, Capital Market Authority, Israel Securities Authority, sector rules | Licensing, risk disclosure, fees, guarantees, investment/insurance/credit claims |
| Sponsored content | Consumer Protection and Fair Trade Authority publications and enforcement positions and misleading-advertising principles | Influencer disclosure, advertorials, affiliate links, gifted products |
| Lotteries and prizes | Penal Law and permit practice for chance-based promotions | Eligibility, odds, rules, chance/prize mechanics, permit needs |
| Minors | Consumer protection, privacy, sector rules, platform policies | Child-directed ads, parental consent, manipulative design, targeting limits |
| Environmental claims | Consumer protection and substantiation principles | "Green", "natural", "eco", "organic", "sustainable" claims |

## Planning request contract

```json
{
  "business": "Independent accountant",
  "goal": "leads",
  "monthly_budget": 6000,
  "avg_order_value": 2400,
  "gross_margin": 0.7,
  "languages": ["he", "ru"],
  "cities": ["Petah Tikva", "Ramat Gan"],
  "sector": "professional_services",
  "audience": "self-employed workers and small companies",
  "offer": "Free 20-minute consultation",
  "regulated_flags": ["tax_advice"],
  "has_website": true,
  "uses_remarketing": true,
  "uses_direct_messages": false,
  "service_languages": ["he", "ru"],
  "date": "03/06/2026"
}
```

## Field rules

| Field | Type | Required | Rule |
|---|---|---:|---|
| `business` | string | Yes | 2–120 characters |
| `goal` | enum | Yes | `leads`, `bookings`, `sales`, `calls`, `store_visits`, `awareness` |
| `monthly_budget` | number | Yes | Greater than 0; warn below ₪1,000 |
| `avg_order_value` | number | For ROI | Greater than 0 |
| `gross_margin` | number | For ROI | 0–1 decimal |
| `languages` | array | Yes | `he`, `ar`, `ru`, `en` |
| `cities` | array | No | Empty means Israel nationwide |
| `regulated_flags` | array | No | `health`, `finance`, `tax_advice`, `minors`, `alcohol`, `lottery`, `environmental`, `real_estate`, `employment`, `cosmetics` |
| `date` | string | No | Prefer DD/MM/YYYY |

## Planning response example

```json
{
  "campaign_summary": {"business": "Independent accountant", "goal": "leads", "budget": "₪6,000", "risk_level": "medium"},
  "assumptions": ["Lead-to-sale rate must be verified in CRM."],
  "audience_segments": [{"name": "New self-employed workers", "need": "Open files correctly", "message_angle": "Start with a clear checklist"}],
  "channel_mix": [{"channel": "Google Search", "budget": 3300, "percentage": 55}],
  "roi_estimate": {"break_even_cpa": 1680, "roi": 0.12, "interpretation": "Verify attribution before scaling."},
  "compliance_flags": [{"code": "TAX_CLAIM_REVIEW", "severity": "warning", "field": "regulated_flags"}],
  "launch_checklist": ["Verify VAT display and offer terms.", "Add privacy notice to lead form."]
}
```

## ROI request and response

Request:

```json
{"spend": 4500, "clicks": 1800, "conversions": 54, "avg_order_value": 350, "gross_margin": 0.48}
```

Response:

```json
{
  "spend": 4500.0,
  "clicks": 1800,
  "conversions": 54,
  "conversion_rate": 0.03,
  "cost_per_click": 2.5,
  "cost_per_conversion": 83.33,
  "gross_profit": 9072.0,
  "roi": 1.016,
  "break_even_conversions": 27,
  "break_even_cpa": 168.0,
  "interpretation": "Estimated gross-profit ROI is 101.6%; verify attribution, refunds, and marginal CPA before scaling."
}
```

## Error and warning table

| Code | Trigger | Fix |
|---|---|---|
| `MISSING_BUSINESS` | Empty business field | Add business type or description |
| `INVALID_GOAL` | Unsupported goal | Use a supported enum value |
| `INVALID_BUDGET` | Budget <= 0 | Enter budget above ₪0 |
| `TINY_BUDGET_FRAGMENTATION` | Budget below ₪1,000 | Use one primary channel |
| `INVALID_AOV` | AOV <= 0 | Enter positive average order value |
| `INVALID_MARGIN` | Margin outside 0–1 | Enter decimal margin |
| `UNSUPPORTED_LANGUAGE` | Language not supported | Use `he`, `ar`, `ru`, or `en` |
| `REGULATED_REVIEW_REQUIRED` | Sensitive sector or flag | Add manual review and substantiation |
| `DIRECT_MARKETING_CONSENT_REQUIRED` | Email/SMS/WhatsApp marketing | Verify consent, sender identity, removal |
| `PRIVACY_NOTICE_REQUIRED` | Remarketing or lead capture risk | Add privacy notice and data-use review |
| `NO_SERVICE_LANGUAGE` | Advertised language cannot be served | Remove language or add routing |
| `UNSUPPORTED_CLAIM_RISK` | Guarantee/cure/savings style claim | Remove or substantiate permitted claim |
| `MATERIAL_TERMS_REQUIRED` | Urgency/discount without clear terms | Add dates, limits, VAT, delivery, cancellation |
| `ACCESSIBILITY_CHECK_REQUIRED` | Landing/form/video workflow | Check accessibility before launch |

## Platform mapping

| Planning concept | Google Ads | Meta | TikTok/YouTube | Email/SMS/WhatsApp |
|---|---|---|---|---|
| High-intent capture | Keywords, local assets, calls | Limited | Limited | Not acquisition without consent |
| Prospecting | Broad category/search expansion | Broad/interests/lookalikes | Creative-led audience testing | Consented list only |
| Retargeting | Remarketing/customer match | Website/custom audience | Website/custom audience | Consent-based direct marketing |
| Measurement | Tags, enhanced conversions, call tracking | Pixel/CAPI/lead forms | Pixel/events | Replies, clicks, purchases, opt-outs |
| Compliance review | Claims and landing page | Claims, targeting, landing page | Claims, minors, landing page | Consent and unsubscribe |

## Audit fields

Keep plan date, assumptions, claims, offer terms, compliance flags, language routing, tracking map, optimization decisions, and final launch approval evidence.


## Officially verified constants and non-API scope

| Item | Verified value | Planning impact |
|---|---|---|
| Israeli VAT rate | 18% from 01/01/2025 | Use for VAT-inclusive consumer price examples unless a lawful exemption or zero-rate applies. |
| API endpoints used by this package | None | This is a local planning helper. Do not send campaign data to Israeli government APIs. |
| Webhook event names used by this package | None | No webhook listener or event taxonomy is implemented. |
| Optional future tax-invoice integration | Israel Tax Authority OpenAPI documentation exists for invoice allocation | Keep separate from campaign planning; use official Tax Authority developer material before implementation. |

The package does not implement an Israeli government API client. The file remains a regulatory and data-contract reference for internal plan objects, validation errors, and optional future integrations.
