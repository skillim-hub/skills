# Israeli Appointment Booking Reference

This skill uses official-channel workflows because the Israeli Kupot Cholim do not expose one universal public appointment-booking API for all members and services. Treat the examples below as internal workflow schemas unless a signed, authorized integration agreement exists.

## Official-channel sources

| Source | Public URL | Use |
|---|---|---|
| Clalit | `https://www.clalit.co.il/` | Member app/site, clinic desk, service center, specialist and clinic information. |
| Maccabi | `https://www.maccabi4u.co.il/` | Member app/site, call center, clinic services, digital appointment flows. |
| Meuhedet | `https://www.meuhedet.co.il/` | Member app/site, service center, clinic and district workflows. |
| Leumit | `https://www.leumit.co.il/` | Member app/site, service center, clinic and regional services. |
| Ministry of Health | `https://www.gov.il/he/departments/ministry_of_health` | Public health policy and regulatory information. |
| Kol HaBriut | `https://www.gov.il/he/departments/units/kol-habriut` | Health rights and Ministry of Health service-center route. |
| Magen David Adom | `https://www.mdais.org/` | Emergency medical service; call 101 in emergencies. |

Verify current phone numbers, portal names, and requirements before production use.

## Israeli law and regulation anchors

| Area | Source | Practical impact |
|---|---|---|
| Health entitlement | National Health Insurance Law, 5754-1994 | Members receive basket services through Kupot Cholim; booking must respect HMO procedures. |
| Patient rights | Patient Rights Law, 5756-1996 | Respect dignity, consent, access, and medical confidentiality. |
| Privacy | Protection of Privacy Law, 5741-1981 | Health details are sensitive personal information; minimize and secure data. |
| Database security | Protection of Privacy Regulations (Data Security), 5777-2017 | Apply access control, logging, retention limits, and data-security controls. |
| Accessibility | Equal Rights for Persons with Disabilities Law, 5758-1998 | Capture accessibility needs and confirm accessible clinics. |
| Consumer disclosure | Consumer Protection Law, 5741-1981 | Paid administrative booking help must disclose price, scope, and limitations. |
| Business records | VAT Law and Israeli bookkeeping requirements | Issue receipt/invoice when legally required for paid services. |

## Data classification

| Data | Classification | Store? | Handling |
|---|---|---:|---|
| HMO | Operational | Yes | Needed for routing. |
| Service category | Health-related operational | Minimal | Use broad category, not diagnosis details. |
| City and time window | Operational | Yes | Needed for availability. |
| Referral exists | Health-related operational | Minimal | Store status only. |
| Full Israeli ID number | Sensitive identifier | Avoid | User enters directly in official channel. |
| HMO password | Secret | Never | Do not request or store. |
| SMS/OTP code | Secret | Never | Do not request or store. |
| Medical files/results | Sensitive health data | Avoid | Use official secure upload only. |
| Confirmation number | Operational | Yes | Protect if tied to a person. |

## Workflow request example

```json
{
  "hmo": "maccabi",
  "service": "dermatology",
  "city": "Rishon LeZion",
  "date_from": "2026-07-01",
  "date_to": "2026-07-31",
  "language": "he",
  "accessibility": ["wheelchair"],
  "referral_status": "unknown",
  "urgency": "routine"
}
```

## Workflow response example

```json
{
  "status": "manual_action_required",
  "recommended_channels": ["official_app", "official_website", "call_center", "clinic_desk"],
  "specialty": "dermatology",
  "referral_required": "unknown_check_official_channel",
  "instructions": [
    "Use the official HMO app or website first.",
    "Search by Hebrew service name and city.",
    "If blocked, book family doctor or request referral.",
    "Save confirmation number and cancellation deadline."
  ],
  "privacy_notice": "Do not send ID number, HMO password, SMS code, or medical files through this helper."
}
```

## Confirmation record example

```json
{
  "appointment_id": "local-20260718-0940",
  "hmo": "maccabi",
  "service": "dermatology",
  "clinic_city": "Rishon LeZion",
  "appointment_date": "2026-07-18",
  "appointment_time": "09:40",
  "confirmation_number": "entered_by_user",
  "preparation_required": false,
  "retention_delete_after": "2026-08-18"
}
```

## Error table

| Code | Meaning | Action |
|---|---|---|
| `HMO_UNSUPPORTED` | HMO is outside Clalit/Maccabi/Meuhedet/Leumit | Ask user to choose supported HMO or switch to manual insurer workflow. |
| `URGENCY_EMERGENCY` | Emergency red flags detected | Stop routine booking; route to 101/ER/urgent hotline. |
| `REFERRAL_REQUIRED` | Specialist requires referral | Book family doctor or digital referral workflow. |
| `ORDER_REQUIRED` | Test requires order | Ask doctor/clinic for order through official channel. |
| `APPROVAL_REQUIRED` | Form 17/commitment/district approval needed | Use HMO administrative approvals workflow. |
| `NO_SLOTS` | No availability in selected search | Expand area, remove provider preference, call clinic/HMO center. |
| `ACCESSIBILITY_UNKNOWN` | Clinic accessibility not confirmed | Call clinic and confirm entrance, elevator, restroom, and exam room. |
| `LANGUAGE_UNAVAILABLE` | Preferred provider language unavailable | Search broader area or ask for support/alternate provider. |
| `PORTAL_AUTH_REQUIRED` | Portal requires member login | User logs in directly; do not collect credentials. |
| `PRIVACY_RISK` | Unnecessary sensitive data appears | Redact/delete if possible and continue with minimal data. |
| `SERVICE_TAXONOMY_UNKNOWN` | Service name not recognized | Search Hebrew synonyms or ask official channel. |

## HTTP-style adapter table for authorized integrations

| Status | Code | Meaning | Retry |
|---:|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid request payload | Fix request. |
| 401 | `AUTH_REQUIRED` | User authentication required | No credential handling by helper. |
| 403 | `NOT_ALLOWED` | Member/service not eligible | Route to official service center. |
| 404 | `SERVICE_NOT_FOUND` | Service taxonomy mismatch | Search synonyms. |
| 409 | `SLOT_TAKEN` | Slot disappeared | Search again. |
| 422 | `REFERRAL_OR_ORDER_MISSING` | Missing prerequisite | Resolve referral/order/approval. |
| 429 | `TOO_MANY_REQUESTS` | Too many attempts | Stop automation; use official channel. |
| 503 | `PROVIDER_UNAVAILABLE` | Channel down | Retry later or call center. |

## Specialty taxonomy

| Key | Hebrew terms | Requirement tendency |
|---|---|---|
| family_medicine | רופא משפחה, רפואת משפחה | Usually direct. |
| pediatrics | רופא ילדים, ילדים | Usually direct; urgent route for severe child symptoms. |
| dermatology | עור ומין, רופא עור | Varies. |
| orthopedics | אורתופדיה, אורתופד | Varies. |
| ophthalmology | עיניים, רופא עיניים | Varies; sudden vision loss urgent. |
| ent | אף-אוזן-גרון, אא״ג | Varies. |
| gynecology | נשים, גינקולוגיה | Often direct. |
| gastroenterology | גסטרו, גסטרואנטרולוגיה | Often referral. |
| cardiology | קרדיולוגיה | Often referral; chest pain urgent. |
| neurology | נוירולוגיה | Often referral. |
| endocrinology | אנדוקרינולוגיה, סוכרת | Often referral. |
| psychiatry | פסיכיאטריה, בריאות הנפש | Varies; self-harm urgent. |
| imaging | דימות, MRI, CT, אולטרסאונד, רנטגן | Order and approval often needed. |
| lab | בדיקות דם, בדיקות שתן, מעבדה | Active order usually needed. |
| admin | טופס 17, התחייבות, אישור | Administrative approval channel. |

## Security requirements

- Obtain explicit permission for caregiver/client assistance.
- Use official delegated authorization only where offered.
- Never collect passwords or OTP codes.
- Encrypt stored appointment records.
- Log operational metadata only.
- Delete notes after the retention period.
- Keep an access log and incident-response process.
- Provide export/delete process for stored user data.
