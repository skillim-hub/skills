# API and Regulation Reference

This reference supports organic scheduling workflows for Facebook, Instagram, TikTok, and LinkedIn in Israel. Verify platform documentation and Israeli legal requirements before production launch because API scopes, review requirements, rate limits, and regulations can change.

Validation status: key platform endpoints, Israeli regulatory points, timezone handling, and open-data endpoints were web-validated on 03/06/2026. See `references/verification-log.md` for source pairs, snippets, corrections, and unresolved items.

## Scope

Covered areas:

- Platform publishing APIs and content constraints.
- Israeli timezone, privacy, consumer, spam, accessibility, and disclosure considerations.
- Request and response examples for scheduler integrations.
- Operational error tables.
- Local data sources that can support Israeli scheduling workflows.

Not covered:

- Paid media buying.
- Political advertising.
- Scraping.
- Account takeover automation.
- Legal advice.

## Platform API overview

| Platform | API family | Typical use | Key production requirements |
|---|---|---|---|
| Facebook Page | Meta Graph API | Page posts, photos, videos, scheduling where supported | Page access token, permissions, app review, page role, policy compliance |
| Instagram Professional | Instagram Graph API | Media containers, Reels, captions, publishing | Business or Creator account connected to Facebook Page, media URL, publishing permissions |
| TikTok | TikTok Content Posting API | Upload or publish video content | OAuth, approved scopes, video metadata, status polling |
| LinkedIn | LinkedIn Marketing / Community APIs | Organization posts, member posts where authorized | OAuth, organization admin rights, approved products and scopes |

## Timezone reference

| Item | Value |
|---|---|
| IANA timezone | `Asia/Jerusalem` |
| Standard time | UTC+02:00 |
| Daylight time | UTC+03:00 |
| Storage recommendation | Store timezone-aware ISO 8601 timestamps |
| Display recommendation in Hebrew docs | `DD/MM/YYYY HH:mm` |
| DST handling | Use an IANA timezone library such as Python `zoneinfo`; never hardcode offset |

### Example timestamp

```json
{
  "scheduled_at": "2026-06-08T08:30:00+03:00",
  "timezone": "Asia/Jerusalem",
  "display_he": "08/06/2026 08:30"
}
```

## Internal scheduler API

The included client is not a platform publisher. It creates validated, exportable plans that can feed an approved publishing workflow.

### Create schedule request

```json
{
  "business": {
    "name": "סטודיו נועה",
    "type": "beauty_salon",
    "city": "ראשון לציון",
    "audience": "נשים 25-45",
    "shabbat_policy": "avoid"
  },
  "platforms": ["facebook", "instagram"],
  "start_date": "2026-06-08",
  "days": 14,
  "timezone": "Asia/Jerusalem",
  "blackout_dates": ["2026-09-22"],
  "posts": [
    {
      "title": "טיפים לפני צבע",
      "platform": "instagram",
      "format": "reel",
      "caption": "לפני צבע? 3 דברים שכדאי לדעת ",
      "hashtags": ["#מספרה", "#ראשוןלציון"],
      "cta": "שלחי הודעה לקביעת תור"
    }
  ]
}
```

### Create schedule response

```json
{
  "timezone": "Asia/Jerusalem",
  "items": [
    {
      "platform": "instagram",
      "scheduled_at": "2026-06-08T08:30:00+03:00",
      "format": "reel",
      "caption": "לפני צבע? 3 דברים שכדאי לדעת ",
      "hashtags": ["#מספרה", "#ראשוןלציון"],
      "cta": "שלחי הודעה לקביעת תור",
      "approval_status": "pending_owner_review",
      "risk_flags": ["requires_asset_rights_check"]
    }
  ],
  "warnings": []
}
```

### Validation request

```json
{
  "platform": "instagram",
  "format": "reel",
  "caption": "לפני שמעלים Reel: בדקו שיש כתוביות בעברית ",
  "hashtags": ["#עסקיםקטנים", "#שיווקדיגיטלי"],
  "media_count": 1,
  "contains_customer_image": false,
  "contains_price": false
}
```

### Validation response

```json
{
  "valid": true,
  "issues": [],
  "normalized_caption": "לפני שמעלים Reel: בדקו שיש כתוביות בעברית ",
  "risk_flags": ["requires_subtitles_check"]
}
```

### Internal error table

| Code | Meaning | Common cause | Fix |
|---|---|---|---|
| `UNKNOWN_PLATFORM` | Platform is unsupported | Typo such as `insta` | Use `facebook`, `instagram`, `tiktok`, or `linkedin` |
| `INVALID_TIMEZONE` | Timezone cannot be loaded | Non-IANA timezone | Use `Asia/Jerusalem` |
| `CAPTION_TOO_LONG` | Caption exceeds platform limit | Reused long Facebook caption | Shorten or split into thread/carousel |
| `HASHTAG_LIMIT_EXCEEDED` | Too many hashtags | Instagram-style block reused everywhere | Reduce to focused tags |
| `MEDIA_REQUIRED` | Platform/format requires media | Instagram Reel without media | Attach approved image/video |
| `SHABBAT_WINDOW` | Requested slot falls in sensitive window | Friday afternoon or Saturday | Move to Sunday or Saturday night |
| `BLACKOUT_DATE` | Requested date blocked | Memorial day, Yom Kippur, emergency pause | Replace with respectful service update or skip |
| `CONSENT_REQUIRED` | Personal data or customer image appears | Testimonial, before/after, child image | Obtain documented consent |
| `TERMS_REQUIRED` | Offer lacks commercial terms | Discount without expiry | Add price, dates, exclusions, conditions |
| `PRO_REVIEW_REQUIRED` | Regulated claim detected | Health, finance, legal, insurance | Route to qualified reviewer |

## Meta Graph API: Facebook Page publishing

Use Meta Graph API only with authorized assets and approved permissions.

### Relevant documentation to verify

- Meta Graph API documentation.
- Facebook Pages API.
- Page access tokens and permissions.
- Content Publishing policy.
- Platform Terms and Developer Policies.

### Typical publish request

```http
POST https://graph.facebook.com/vXX.X/{page-id}/feed
Authorization: Bearer {page-access-token}
Content-Type: application/x-www-form-urlencoded

message=חדש השבוע: מדריך קצר לבחירת ספק בלי אותיות קטנות
&link=https://example.co.il/guide
&published=false
&scheduled_publish_time=1780900200
```

### Typical response

```json
{
  "id": "1234567890_9876543210"
}
```

### Facebook scheduling notes

| Topic | Guidance |
|---|---|
| Account type | Publish through a Page or authorized business asset |
| Groups | Group posting is heavily restricted; do not automate group spam |
| Scheduling | Use supported endpoints and platform rules for unpublished/scheduled posts |
| Links | Ensure Open Graph tags exist for clean previews |
| Local groups | Manual, rule-compliant posting often works better than automation |
| Consent | Customer photos, testimonials, and case studies require permission |

### Facebook API errors

| Error | Meaning | Fix |
|---|---|---|
| OAuthException | Token, permission, or app review issue | Refresh token, confirm scopes, complete review |
| Permission denied | User lacks Page role or asset access | Grant correct role in business settings |
| Invalid parameter | Bad timestamp, URL, or field | Validate payload and Unix timestamp |
| Rate limit | Too many requests | Queue posts and add backoff |
| Policy rejection | Content violates policy | Review content, claims, and destination URL |

## Instagram Graph API: content publishing

Use Instagram publishing only for Professional accounts connected to a Facebook Page.

### Relevant documentation to verify

- Instagram Graph API.
- Content Publishing API.
- Reels publishing requirements.
- Media container creation.
- Rate limits and account eligibility.

### Step 1: create media container

```http
POST https://graph.facebook.com/vXX.X/{ig-user-id}/media
Authorization: Bearer {access-token}
Content-Type: application/x-www-form-urlencoded

media_url=https://media.example.invalid/posts/post-001.jpg
&caption=לפני שמעלים Reel: בדקו שיש כתוביות בעברית %0A%0A#עסקיםקטנים #שיווקדיגיטלי
```

### Step 1 response

```json
{
  "id": "17900000000000001"
}
```

### Step 2: publish media

```http
POST https://graph.facebook.com/vXX.X/{ig-user-id}/media_publish
Authorization: Bearer {access-token}
Content-Type: application/x-www-form-urlencoded

creation_id=17900000000000001
```

### Step 2 response

```json
{
  "id": "18000000000000001"
}
```

### Instagram constraints

| Area | Practical check |
|---|---|
| Account | Business or Creator account |
| Media | Publicly reachable media URL, valid format and aspect ratio |
| Caption | Keep below platform limit and verify emoji rendering |
| Hashtags | Avoid irrelevant hashtag stuffing |
| Reels | Add Hebrew subtitles and verify audio rights |
| Stories | Some publishing capabilities differ from feed/Reels; verify current API support |
| Shopping | Product tagging requires additional setup and policy checks |

### Instagram API errors

| Error | Meaning | Fix |
|---|---|---|
| Media URL invalid | Platform cannot fetch the file | Use HTTPS, public URL, supported MIME type |
| Container not ready | Media still processing | Poll or retry after delay |
| Permission missing | Required scope absent | Request and approve proper permissions |
| Rate limit | Too many publish attempts | Backoff and queue |
| Caption rejected | Policy, length, or encoding problem | Normalize caption and reduce claims/hashtags |

## TikTok Content Posting API

Use TikTok publishing only with explicit authorization and current API approval.

### Relevant documentation to verify

- TikTok for Developers.
- Content Posting API.
- OAuth scopes for video upload and publish.
- Video specifications.
- Status polling and moderation behavior.

### Initialize upload request

```http
POST https://open.tiktokapis.com/v2/post/publish/video/init/
Authorization: Bearer {access-token}
Content-Type: application/json

{
  "post_info": {
    "title": "3 טעויות לפני שמזמינים שירות לבית",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "disable_duet": false,
    "disable_comment": false,
    "disable_stitch": false
  },
  "source_info": {
    "source": "PULL_FROM_URL",
    "video_url": "https://cdn.example.co.il/videos/tips-001.mp4"
  }
}
```

### Initialize upload response

```json
{
  "data": {
    "publish_id": "v_pub_123456789"
  },
  "error": {
    "code": "ok",
    "message": "",
    "log_id": "202606080000000000000000"
  }
}
```

### Status request

```http
POST https://open.tiktokapis.com/v2/post/publish/status/fetch/
Authorization: Bearer {access-token}
Content-Type: application/json

{
  "publish_id": "v_pub_123456789"
}
```

### Status response

```json
{
  "data": {
    "status": "PUBLISH_COMPLETE",
    "publicaly_available_post_id": ["7234567890123456789"]
  },
  "error": {
    "code": "ok",
    "message": "",
    "log_id": "202606080000000000000001"
  }
}
```

### TikTok constraints

| Area | Practical check |
|---|---|
| Video | Confirm duration, file size, aspect ratio, and audio rights |
| Caption | Keep hook clear; avoid legal claims that need review |
| Privacy | Set privacy level intentionally |
| Comments | Disable only when moderation burden or risk requires it |
| Moderation | Allow time for review and status polling |
| Trends | Avoid trends that conflict with business tone or vulnerable audiences |

### TikTok Content Posting webhook events

Use these event names when integrating TikTok Content Posting webhooks. Polling remains required for intermediate states.

| Event | Meaning | Operational response |
|---|---|---|
| `post.publish.failed` | Publishing action failed | Fetch failure reason, pause retry loops, request corrected media or metadata |
| `post.publish.complete` | User created a post from uploaded content | Mark export flow complete, then wait for public availability when needed |
| `post.publish.inbox_delivered` | Draft upload notification reached the creator inbox | Notify the owner to complete the post in TikTok |
| `post.publish.publicly_available` | Post associated with the publish ID is publicly viewable | Record post ID and enable reporting checks |
| `post.publish.no_longer_publicaly_available` | Previously public post stopped being publicly viewable | Alert owner and pause reuse of the asset or caption |

### TikTok API errors

| Error | Meaning | Fix |
|---|---|---|
| `access_token_invalid` | Token expired or wrong app | Refresh OAuth token |
| `scope_not_authorized` | Missing publish scope | Complete app review and reconnect |
| `video_url_invalid` | Video cannot be fetched | Use HTTPS public URL |
| `spam_risk_too_high` | Repeated or suspicious posting | Reduce frequency and vary content |
| `publish_failed` | Upload or moderation failed | Fetch status details and revise content |

## LinkedIn publishing

Use LinkedIn publishing for professional posts, organization updates, recruiting and B2B thought leadership.

### Relevant documentation to verify

- LinkedIn API documentation.
- Use `/rest/posts`, not legacy `/v2/ugcPosts`, for current Posts API examples.
- Community Management API or current post publishing endpoints.
- Organization access control.
- Marketing Developer Platform terms.
- OAuth scopes and product access.

### Organization post request

```http
POST https://api.linkedin.com/rest/posts
Authorization: Bearer {access-token}
X-Restli-Protocol-Version: 2.0.0
Linkedin-Version: 202605
Content-Type: application/json

{
  "author": "urn:li:organization:123456",
  "commentary": "רוב צוותי המכירות לא צריכים עוד דוח. הם צריכים פחות רעש בין ליד לפעולה הבאה.",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

### Organization post response

```http
HTTP/1.1 201 Created
x-restli-id: urn:li:share:7234567890123456789
```

### LinkedIn constraints

| Area | Practical check |
|---|---|
| Admin rights | Verify the publishing user can post as the organization |
| Tone | Keep professional, specific, and useful |
| Claims | Avoid inflated market claims |
| Confidentiality | Remove client-sensitive information |
| Links | Test previews and UTM parameters |
| Comments | Prepare professional responses |

### LinkedIn API errors

| Error | Meaning | Fix |
|---|---|---|
| 401 Unauthorized | OAuth token invalid | Refresh token |
| 403 Forbidden | Missing product/scope/admin role | Grant access or complete review |
| 422 Validation error | Bad payload structure | Validate URNs and content object |
| 429 Rate limit | Too many requests | Backoff and reduce automation |
| 409 Duplicate | Duplicate content or conflict | Vary content and retry safely |

## Israeli legal and regulatory references

Use the following as operational references. Confirm current law, regulations, and professional guidance before launch.

| Topic | Reference | Practical scheduling impact |
|---|---|---|
| Privacy | Protection of Privacy Law, 5741-1981 | Limit collection and use of personal data in leads, testimonials, customer lists |
| Data security | Protection of Privacy Regulations (Data Security), 5777-2017 | Secure exported schedules containing personal details |
| EEA data transfer | Protection of Privacy Regulations regarding data transferred to Israel from the European Economic Area, 5783-2023 | Check obligations when handling EU-origin data |
| Spam | Communications Law (Telecommunications and Broadcasting), Section 30A | Obtain consent for direct commercial messages; identify sender; provide opt-out |
| Consumer protection | Consumer Protection Law, 5741-1981 | Avoid misleading offers, hidden terms, fake urgency, unclear prices |
| Price display | Price indication rules under Israeli consumer protection framework | Show clear ₪ prices and terms for consumer offers |
| VAT | Israel Tax Authority VAT rate and history | When showing consumer prices in Israel, treat the standard VAT rate as 18% from 01/01/2025 unless a verified exemption or zero-rate applies |
| Accessibility | Equal Rights for Persons with Disabilities Law and Service Accessibility Regulations | Add captions, accessible alternatives, readable contrast where feasible |
| Defamation | Prohibition of Defamation Law, 5725-1965 | Avoid claims about competitors or individuals without review |
| Copyright | Copyright Law, 5768-2007 | Use licensed music, images, fonts, templates and creator content |
| Database registration/security | Israeli privacy framework | Review CRM, lead magnets, exported contact lists and remarketing audiences |
| Influencer disclosure | Consumer protection and advertising transparency principles | Disclose paid collaborations, gifts, affiliate links and material benefits |

### Anti-spam checklist

Apply before SMS, email, WhatsApp broadcast, Messenger automation, LinkedIn bulk outreach, or similar direct electronic marketing.

| Check | Required action |
|---|---|
| Consent | Document opt-in before sending promotional messages |
| Sender identity | Include clear business identity |
| Opt-out | Provide easy unsubscribe or removal mechanism |
| Content | Avoid misleading subject lines or hidden conditions |
| Records | Store consent and opt-out evidence |
| Exceptions | Escalate to legal review instead of assuming an exception applies |

### Consumer offer checklist

Use for discounts, coupons, bundles, giveaways, service packages, and limited-time offers.

| Check | Required action |
|---|---|
| Price | Show final or clearly explained price in ₪ |
| Date | Show start/end date in `DD/MM/YYYY` for Hebrew copy |
| Conditions | Explain eligibility, geographic area, quantity limits and exclusions |
| Scarcity | Use only real scarcity |
| Cancellation | Include relevant cancellation or booking terms |
| Evidence | Keep support for claims such as "50% off" or "best seller" |

### Privacy checklist for social content

| Data type | Risk | Required handling |
|---|---|---|
| Customer photo | Identification | Written consent and limited use |
| Testimonial | Personal data and advertising claim | Written approval of exact wording |
| Before/after image | Sensitive or misleading context | Consent, date, service details, no exaggerated claim |
| Phone or WhatsApp lead | Direct contact data | Purpose notice, secure storage, opt-out where marketing follows |
| Customer list upload | Platform matching | Consent/legal basis and minimization |
| Children | High sensitivity | Avoid unless clear guardian consent and strong purpose exist |

## Israeli data sources and APIs useful for workflows

These sources can support local scheduling and validation. Verify endpoints and terms before production use.

| Source | Use | Example |
|---|---|---|
| data.gov.il CKAN API | Find public datasets such as local authorities or public-service data | City/locality normalization for local hashtags |
| Central Bureau of Statistics public datasets | Validate locality names and demographic assumptions | Audience planning and service-area naming |
| Bank of Israel public exchange-rate data | Convert cross-border pricing when needed | Displaying ₪ equivalents for imported products |
| Gov.il services and regulator pages | Verify current consumer, privacy, accessibility guidance | Compliance review links in approval checklist |
| Public Hebrew calendar providers | Convert Hebrew dates to Gregorian dates | Blocking Yom Kippur, memorial days and holidays |

### Example: data.gov.il CKAN package search

```http
GET https://data.gov.il/api/3/action/package_search?q=יישובים
Accept: application/json
```

Response shape:

```json
{
  "success": true,
  "result": {
    "count": 12,
    "results": [
      {
        "name": "localities",
        "title": "רשימת יישובים",
        "resources": [
          {
            "name": "CSV",
            "format": "CSV",
            "url": "https://data.gov.il/..."
          }
        ]
      }
    ]
  }
}
```

### Example: locality normalization request

```json
{
  "input_city": "ראשלצ",
  "source": "locality_dataset",
  "language": "he"
}
```

### Example: locality normalization response

```json
{
  "normalized_city_he": "ראשון לציון",
  "normalized_city_en": "Rishon LeZion",
  "hashtags": ["#ראשוןלציון", "#עסקיםבראשוןלציון"],
  "confidence": 0.94
}
```

### Local data-source errors

| Code | Meaning | Fix |
|---|---|---|
| `DATASET_NOT_FOUND` | Dataset name changed or search failed | Search data.gov.il again and update mapping |
| `CSV_SCHEMA_CHANGED` | Column names changed | Validate schema before use |
| `LOW_CONFIDENCE_LOCALITY` | City nickname could not be mapped safely | Ask for city confirmation |
| `RATE_LIMITED` | Public API throttled | Cache results and retry later |
| `STALE_REGULATORY_LINK` | Regulator page moved | Re-verify source URL before client delivery |

## Request payload templates by use case

### Local service business

```json
{
  "business_type": "local_service",
  "city": "גבעתיים",
  "platforms": ["facebook", "instagram"],
  "cadence": "standard",
  "shabbat_policy": "avoid",
  "content_pillars": ["trust", "education", "local", "offer"],
  "currency": "ILS"
}
```

### Freelancer

```json
{
  "business_type": "freelancer",
  "profession": "מעצבת פנים",
  "platforms": ["instagram", "linkedin"],
  "cadence": "limited",
  "content_pillars": ["portfolio", "education", "behind_the_scenes"],
  "risk_review": ["testimonials", "before_after"]
}
```

### Consumer-facing shop

```json
{
  "business_type": "retail",
  "city": "באר שבע",
  "platforms": ["facebook", "instagram", "tiktok"],
  "cadence": "launch_week",
  "offers": [
    {
      "title": "פתיחת עונה",
      "price": "₪199",
      "valid_until": "30-06-2026",
      "terms": "עד גמר המלאי"
    }
  ]
}
```

## Response payload templates

### Calendar export item

```json
{
  "date": "08/06/2026",
  "time": "08:30",
  "timezone": "Asia/Jerusalem",
  "platform": "instagram",
  "content_type": "reel",
  "pillar": "education",
  "caption": "לפני שמעלים Reel: בדקו שיש כתוביות בעברית.",
  "hashtags": ["#עסקיםקטנים", "#שיווקדיגיטלי"],
  "cta": "שלחו הודעה לקבלת הצ'ק-ליסט",
  "assets_needed": ["vertical_video", "hebrew_subtitles"],
  "approval_status": "pending_owner_review",
  "risk_flags": ["asset_rights_check"]
}
```

### Approval response

```json
{
  "post_id": "local-20260608-instagram-001",
  "approved": true,
  "approved_by": "business_owner",
  "approved_at": "2026-06-07T14:20:00+03:00",
  "changes_requested": []
}
```

## Production integration recommendations

- Keep the planning tool separate from the publishing token store.
- Store OAuth tokens in a secrets manager.
- Store schedules in UTC plus original timezone.
- Log every generated caption version and owner approval.
- Require manual approval before external publish API calls.
- Add exponential backoff for API failures.
- Add platform-specific queues to avoid rate-limit bursts.
- Keep customer consent records outside the caption text.
- Treat exported CSV files as potentially sensitive if they include customer names or contact details.
- Re-verify all platform API versions before deploying.


## Web-validated source index

Use `references/verification-log.md` as the current source index. The log records the source URL, access date, short quote, second-pass source, status, and correction status for each regulatory/API claim that affects production use.
