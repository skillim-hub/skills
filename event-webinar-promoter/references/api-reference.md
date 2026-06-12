# Israeli API and Regulation Reference

This skill does not require a government API to operate. It produces structured plans, copy, schedules, and checklists. Use this reference to keep Israeli event and webinar campaigns practical, traceable, and safer to publish.

Always verify current legal wording before launch. Regulations change, and the campaign owner is responsible for legal review.


## Web-validated current values

Checked on 2026-06-03. Re-check before publishing paid events or tax-sensitive copy.

| Value | Current checked value | Operational use |
|---|---:|---|
| Standard VAT rate | 18%, effective from 01/01/2025 | Use for VAT wording and paid-event pricing checks |
| Exempt dealer turnover ceiling for 2026 | ₪122,833 | Do not infer tax status automatically; use only as a reminder to verify status with the Tax Authority |
| Israel timezone data source | IANA Time Zone Database, latest checked release 2026b | Use `Asia/Jerusalem` and timezone-aware datetimes |
| Web accessibility reference | Israeli Standard 5568, based on WCAG 2.0 level AA for websites | Use for landing-page accessibility checks |
| Tax Authority API topic | חשבוניות ישראל / מספר הקצאה | Do not call from this package; link users to official services if invoice allocation is needed |

## Official Hebrew and English terminology

| Hebrew term | English working term | Use |
|---|---|---|
| דבר פרסומת | Advertisement / marketing message | Direct marketing consent and unsubscribe checks |
| הסרה | Unsubscribe / opt-out | Footer and direct-message handling |
| מאגר מידע | Database | Registration data and privacy checks |
| מסמך הגדרות מאגר | Database definitions document | Privacy data-security governance |
| הודעה לרשות | Notice to the Privacy Protection Authority | Large/sensitive database governance |
| התאמות נגישות | Accessibility accommodations | Event, venue, and landing-page accessibility |
| נגישות אתרי אינטרנט | Website accessibility | Landing-page QA |
| מע״מ | VAT | Paid event pricing |
| מספר הקצאה | Invoice allocation number | Israeli invoice operations where applicable |


## Reference status

| Item | Type | Use in this skill | Citation / source to verify |
|---|---|---|---|
| `Asia/Jerusalem` timezone | Technical standard | Schedule events, reminders, ICS files, and cross-timezone copy | IANA Time Zone Database: `Asia/Jerusalem` |
| Communications Law (Telecommunications and Broadcasts), 1982, Section 30A | Regulation | Direct marketing by email, SMS, fax, automated calls, and similar messages | Israeli law databases; commonly known as the Israeli “Spam Law” |
| Protection of Privacy Law, 1981 | Regulation | Registration data, mailing lists, partner sharing, privacy notices | Israeli law databases and Privacy Protection Authority publications |
| Protection of Privacy Regulations (Data Security), 2017 | Regulation | Security of registration exports and contact lists | Privacy Protection Authority |
| Privacy Protection Law Amendment 13 | Regulation | Modern privacy compliance risk, database governance, enforcement exposure | Official Israeli legislation and Privacy Protection Authority updates |
| Consumer Protection Law, 1981 | Regulation | Paid event details, cancellation/refund terms, consumer-facing claims | Consumer Protection and Fair Trade Authority |
| Consumer Protection Regulations (Cancellation of a Transaction), 2010 | Regulation | Cancellation handling for paid consumer events where applicable | Consumer Protection and Fair Trade Authority |
| Equal Rights for Persons with Disabilities Law, 1998 | Regulation | Accessible service, participation, and accommodation handling | Commission for Equal Rights of Persons with Disabilities |
| Service Accessibility Regulations, 2013 | Regulation | Venue/service accessibility and accommodation contact | Commission for Equal Rights of Persons with Disabilities |
| Israeli Standard 5568 / WCAG 2.0 AA alignment | Standard | Web accessibility checks for landing pages and digital assets | Commission for Equal Rights for Persons with Disabilities guidance |
| Value Added Tax Law, 1975 | Regulation | Price/VAT wording and receipts for paid events | Israel Tax Authority |
| Bookkeeping Instructions / tax documentation rules | Regulation | Invoice/receipt workflow after paid registration; invoice allocation may be relevant for some transactions | Israel Tax Authority |
| Copyright Law, 2007 | Regulation | Images, music, slides, recordings, and speaker materials | Israeli law databases |
| Defamation Prohibition Law, 1965 | Regulation | Claims about competitors, testimonials, and case studies | Israeli law databases |
| Platform policies | Contractual rules | Meta, Google, LinkedIn, Zoom, WhatsApp, payment providers | Provider documentation |


## Machine interface versus Hebrew display

The JSON interface accepts dates as `DD-MM-YYYY` for strict validation. Hebrew-facing public copy and Hebrew documentation display dates as `DD/MM/YYYY`.

## Technical schemas

Use these schemas for structured planning. They are not external APIs; they are stable input/output contracts for automation, CLI use, and testing.

### Event intake schema

Request:

```json
{
  "event_name": "סדנת צילום מוצרים בסמארטפון",
  "format": "workshop",
  "audience": "בעלי חנויות אונליין קטנות",
  "date": "15-07-2026",
  "time": "10:00",
  "duration_minutes": 180,
  "price_nis": 290,
  "city": "חיפה",
  "capacity": 18,
  "goal": "registrations",
  "language": "he",
  "consent_status": "opt_in",
  "registration_url": "https://example.co.il/register"
}
```

Required fields:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `event_name` | string | Yes | Use a descriptive title |
| `format` | string | Yes | `webinar`, `workshop`, `meetup`, `course_preview`, `launch`, `clinic`, `live_stream` |
| `audience` | string | Yes | Prefer one primary audience |
| `date` | string | Yes | `DD-MM-YYYY` |
| `time` | string | Yes | `HH:MM`, 24-hour clock |
| `duration_minutes` | integer | Yes | 15–480 |
| `price_nis` | number | No | `0` means free |
| `city` | string | No | Required for offline/local events |
| `capacity` | integer | No | Required for honest scarcity/capacity copy |
| `goal` | string | No | `registrations`, `qualified_leads`, `sales`, `community`, `education` |
| `language` | string | No | `he`, `en`, `bilingual` |
| `consent_status` | string | No | `opt_in`, `unknown`, `partner_owned`, `transactional_only` |
| `registration_url` | string | No | Used for CTAs and UTM links |

Response:

```json
{
  "event_name": "סדנת צילום מוצרים בסמארטפון",
  "timezone": "Asia/Jerusalem",
  "starts_at": "2026-07-15T10:00:00+03:00",
  "ends_at": "2026-07-15T13:00:00+03:00",
  "recommended_channels": ["instagram", "facebook_groups", "google_business_profile", "partners"],
  "reminders": [
    {"label": "launch", "send_at": "2026-06-15T10:00:00+03:00", "channel": "social"},
    {"label": "72h", "send_at": "2026-07-12T10:00:00+03:00", "channel": "email"},
    {"label": "24h", "send_at": "2026-07-14T10:00:00+03:00", "channel": "email"},
    {"label": "2h", "send_at": "2026-07-15T08:00:00+03:00", "channel": "whatsapp"}
  ],
  "compliance_flags": [
    "Include cancellation/refund terms before publishing paid event",
    "State whether ₪290 includes VAT",
    "Use WhatsApp only for contacts with opt-in"
  ]
}
```

## Validation errors

| Code | Meaning | Example | Recommended fix |
|---|---|---|---|
| `INVALID_DATE_FORMAT` | Date is not `DD-MM-YYYY` | `2026-07-15` | Use `15-07-2026` |
| `INVALID_TIME_FORMAT` | Time is not `HH:MM` | `8pm` | Use `20:00` |
| `INVALID_DURATION` | Duration is outside expected range | `0` | Use 15–480 minutes |
| `MISSING_AUDIENCE` | Audience is empty | `""` | Define one primary audience |
| `MISSING_EVENT_NAME` | Event title is empty | `""` | Add a clear event name |
| `SATURDAY_EVENT` | Event falls on Saturday | `18-07-2026` | Move to Sunday–Thursday unless intentional |
| `FRIDAY_AFTERNOON` | Friday afternoon may underperform | Friday 15:00 | Move to Friday morning or Sunday evening |
| `NO_CONSENT_FOR_DIRECT_MARKETING` | Direct marketing requested without opt-in | SMS blast to imported list | Use organic/partner channels |
| `PAID_WITHOUT_TERMS` | Paid event lacks cancellation terms | ₪290 workshop | Add refund/cancellation wording |
| `CAPACITY_CLAIM_UNVERIFIED` | Scarcity copy lacks capacity data | “last seats” without number | Remove claim or add real capacity |
| `MISSING_ACCESSIBILITY_CONTACT` | Accessibility info is absent | Offline venue page | Add contact and venue access notes |
| `MISSING_PRIVACY_NOTE` | Form collects data without explanation | Registration form | Add short privacy note |

## Optional platform API patterns

The skill can prepare data for external systems, but it does not call them by default.

### Calendar ICS output

Use an `.ics` calendar invite for webinars and workshops.

Request-like object:

```json
{
  "summary": "איך לתמחר שירותים בלי להפסיד לקוחות",
  "dtstart": "20260624T200000",
  "dtend": "20260624T210000",
  "tzid": "Asia/Jerusalem",
  "description": "קישור כניסה יישלח לנרשמים.",
  "location": "Online"
}
```

Expected ICS fragment:

```ics
BEGIN:VEVENT
SUMMARY:איך לתמחר שירותים בלי להפסיד לקוחות
DTSTART;TZID=Asia/Jerusalem:20260624T200000
DTEND;TZID=Asia/Jerusalem:20260624T210000
LOCATION:Online
DESCRIPTION:קישור כניסה יישלח לנרשמים.
END:VEVENT
```

Errors:

| Error | Cause | Fix |
|---|---|---|
| `ICS_TZ_MISSING` | No `TZID` supplied | Use `Asia/Jerusalem` |
| `ICS_END_BEFORE_START` | Duration invalid | Recalculate from duration |
| `ICS_UNSAFE_DESCRIPTION` | Description includes unescaped newline or comma | Escape per RFC 5545 |

### UTM link builder

Request:

```json
{
  "base_url": "https://example.co.il/register",
  "source": "facebook",
  "medium": "social",
  "campaign": "pricing_webinar_24-06-2026",
  "content": "launch_post"
}
```

Response:

```json
{
  "url": "https://example.co.il/register?utm_source=facebook&utm_medium=social&utm_campaign=pricing_webinar_24-06-2026&utm_content=launch_post"
}
```

Errors:

| Error | Cause | Fix |
|---|---|---|
| `INVALID_URL` | URL has no scheme or host | Use `https://...` |
| `MISSING_UTM_SOURCE` | Source omitted | Add channel name |
| `UNSAFE_UTM_VALUE` | Spaces or Hebrew in UTM values | Use lowercase ASCII with underscores |

### WhatsApp deep link

Use only for manual opt-in flows or one-to-one messages. Do not use to bypass consent.

Request:

```json
{
  "phone_e164": "+972501234567",
  "message": "שלום, אפשר לקבל פרטים על הסדנה?"
}
```

Response:

```json
{
  "url": "https://wa.me/972501234567?text=%D7%A9%D7%9C%D7%95%D7%9D..."
}
```

Errors:

| Error | Cause | Fix |
|---|---|---|
| `INVALID_PHONE` | Phone is not E.164 | Use `+972...` |
| `CONSENT_REQUIRED` | Bulk promotional use requested | Use opt-in messaging only |
| `MESSAGE_TOO_LONG` | Message is too long for practical use | Shorten to one clear ask |

## Regulatory implementation notes

### Section 30A direct marketing checks

Before promotional email/SMS/WhatsApp-style campaign execution:

1. Confirm recipient consent or another permitted basis.
2. Identify the advertiser.
3. Make the message clearly promotional where required.
4. Include a simple unsubscribe method.
5. Suppress opted-out contacts.
6. Keep evidence of consent source, date, and scope.

Practical message footer:

```text
נשלח אליך כי נרשמת לקבלת עדכונים מ-[שם העסק].
להסרה: [קישור הסרה] או השב/י "הסר".
```

### Privacy and registration forms

Collect only what is needed:

Minimal webinar form:

```json
{
  "full_name": "string",
  "email": "string",
  "phone": "optional string only when reminders are needed and consent is explicit",
  "consent_marketing": "boolean",
  "privacy_notice_accepted": "boolean"
}
```

Short privacy note:

```text
הפרטים ישמשו להרשמה, תזכורות ועדכונים לגבי האירוע. ניתן לבקש הסרה בכל עת. לא יועברו פרטים לצד שלישי ללא צורך תפעולי או הרשאה מתאימה.
```

### Paid event consumer wording

Include:

- Price in ₪.
- Whether VAT is included where relevant.
- What is included.
- Cancellation/refund terms.
- How confirmation is sent.
- Contact details.
- Accessibility contact.

Example:

```text
מחיר: ₪290. יש לוודא לפני הפרסום האם המחיר כולל מע״מ.
ביטול עד 7 ימים לפני הסדנה: החזר מלא. ביטול לאחר מכן: לפי תנאי העסק המפורטים בעמוד ההרשמה.
```

### Accessibility wording

For online event:

```text
האירוע יתקיים בזום. להתאמות נגישות, כתוביות או שאלות לוגיסטיות, ניתן לפנות עד 48 שעות לפני האירוע ל-[אימייל/טלפון].
```

For venue:

```text
המפגש מתקיים ב-[כתובת]. יש לציין נגישות כניסה, מעלית, חניה נגישה ושירותים נגישים לפי נתוני המקום. להתאמות נוספות ניתן לפנות עד 48 שעות לפני האירוע.
```

## Campaign data retention

Recommended operational retention:

| Data | Suggested handling |
|---|---|
| Registration list | Store in a restricted folder or CRM |
| Consent logs | Keep as long as marketing permission is relied upon |
| Unsubscribe list | Keep suppression data to avoid re-contact |
| Attendance export | Keep only as long as needed for follow-up and analysis |
| Chat transcript | Review before sharing; remove sensitive personal details |
| Recording | Notify participants if recording; avoid publishing private Q&A without review |

## Error handling table for campaign operations

| Operation | Risk | Preventive check | Recovery |
|---|---|---|---|
| Email launch | Missing unsubscribe | Validate footer | Send correction only if necessary and suppress opt-outs |
| SMS reminder | No consent | Require `consent_status=opt_in` | Do not send; use email/organic |
| Paid landing page | Missing terms | Require cancellation placeholder | Pause publication |
| Venue event | Accessibility missing | Require contact line | Add venue access details |
| Partner campaign | Ambiguous list ownership | Confirm partner sends to its own opted-in list | Avoid sharing raw lists |
| Replay email | Recording includes personal info | Review and edit recording | Share edited version or slides only |
| Scarcity post | Capacity not real | Check capacity and seats left | Remove scarcity language |
