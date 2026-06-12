# Israeli insurance official-source and structured data reference

This package is a document-analysis and workflow skill, not an official government API client. Many Israeli insurance sources are public portals, policy documents, calculators, laws, or regulated disclosures rather than open APIs.

Verify current rules and portal behavior before production use. Do not automate identity-bound services unless a documented public API and permission exist.

## Official-source matrix validated on 2026-06-02

| Source or regulation | Official URL | Use | Evidence to extract | Validation status |
|---|---|---|---|---|
| רשות שוק ההון, ביטוח וחיסכון | `https://www.gov.il/he/departments/capital_market_authority` | Insurance supervision, licensed entities, circulars, consumer guidance | regulated entity context, official terminology, publication dates | Double-confirmed in `verification-log.md` |
| הר הביטוח | `https://harb.cma.gov.il/` | Personal policy inventory | insurer, policy type, policy number, start date, premium indication | Manual user flow only |
| מדריך לכניסת מבוטחים להר הביטוח | `https://www.gov.il/he/pages/sign-in-resellers` | Authentication posture | confirms stronger identification for portal entry | Manual user flow only |
| מחשבון ביטוח בריאות | `https://briut.cma.gov.il/` | Health tariff comparison | product category, insurer tariff, user-selected parameters | Calculator aid; policy wording controls |
| מחשבון ביטוח דירה | `https://dira.cma.gov.il/` | Home tariff comparison | structure, contents, tariff assumptions | Calculator aid; policy wording controls |
| מחשבון ריסק | `https://life.cma.gov.il/` | Life/risk tariff comparison | death cover tariff, mortgage-life context | Calculator aid; policy wording controls |
| חוק חוזה הביטוח, התשמ״א-1981 | `https://main.knesset.gov.il/Activity/Legislation/Laws/pages/lawprimary.aspx?lawitemid=2000653&st=lawlaws&t=lawlaws` | Insurance contract framework | policy, disclosure, claim, cancellation context | Legal interpretation requires counsel |
| חוק הפיקוח על שירותים פיננסיים (ביטוח), התשמ״א-1981 | `https://main.knesset.gov.il/Activity/Legislation/Laws/pages/lawprimary.aspx?lawitemid=2000503&st=lawlaws&t=lawlaws` | Supervisory framework | licensing and regulated activity context | Use as regulatory context |
| פוליסה תקנית לביטוח דירה ותכולתה | `https://www.gov.il/BlobFolder/dynamiccollectorresultitem/notice-2005-1-12-1/he/regulation_2022-273_10052022_pdf.pdf` | Home policy baseline | structure, contents, exclusions, deductibles, extensions | Endorsements can change practical coverage |
| חוק ביטוח בריאות ממלכתי, התשנ״ד-1994 | `https://www.gov.il/he/pages/bituah01` | Public health basket context | distinction between basket, שב״ן, and private insurance | Does not replace private policy wording |
| עקרונות תוכנית השב״ן | `https://www.gov.il/he/pages/shaban_principles` | Supplementary health-plan context | voluntary additional services through health funds | Use for overlap analysis |
| שירות איתור בעלי רישיון | `https://www.gov.il/he/service/agents_and_consultants_search` | Professional review trigger | licensed insurance agents and pension professionals | Use for referral to licensed review |
| רשות המסים: היסטוריית שיעורי מע״מ | `https://www.gov.il/he/pages/vat-history` | General Israeli VAT context | general VAT rate and effective date | Tax treatment of insurance premiums still requires professional review |

## Public access posture

### Human portal or calculator

Use official portals and calculators manually when the service is designed for human access. Do not scrape identity-bound accounts or emulate a user login.

```json
{
  "flow": "manual_user_portal_lookup",
  "source_examples": ["har_habituach", "briut_calculator", "dira_calculator", "life_risk_calculator"],
  "authentication": "performed_by_user",
  "assistant_receives": "redacted facts, exported values, screenshots, or policy documents supplied by user",
  "forbidden": [
    "requesting one-time code",
    "storing credentials",
    "automating login",
    "scraping personal accounts"
  ]
}
```

### Official public API status

No official public API host, endpoint path, or webhook event set was confirmed for the intended health, home, and life policy-diff workflow. Do not present the local client as a government API wrapper.

| Item | Status | Handling |
|---|---|---|
| Official public policy inventory API | Not confirmed | Use manual Har HaBituach review and user-supplied data |
| Official calculator API endpoints | Not confirmed | Use calculator pages manually |
| Webhook event names | Not applicable | Keep local workflows file-based |
| Placeholder endpoint examples | Removed | Use local structured request and response examples only |

## Internal data models

### Policy record

```json
{
  "policy_id": "health-a-2026",
  "policy_type": "health",
  "insurer": "Example Insurance Ltd.",
  "policy_name": "Private Health Plus",
  "policy_number": "redacted-1234",
  "holder_type": "family",
  "start_date": "01/01/2024",
  "renewal_date": "31/12/2026",
  "premium_monthly_nis": 185.0,
  "premium_annual_nis": 2220.0,
  "coverages": {
    "private_surgery_israel": {
      "covered": true,
      "limit_nis": 1000000,
      "deductible_nis": 0,
      "notes": "Private provider list applies"
    }
  },
  "exclusions": ["left knee condition"],
  "waiting_period_days": 90,
  "index_linkage": "cpi",
  "source": {"document_name": "policy_schedule.pdf", "page": 3}
}
```

### Comparison request

```json
{
  "locale": "en-IL",
  "comparison_goal": "renewal_negotiation",
  "profile": {
    "segment": "freelancer",
    "home_office": true,
    "mortgage": true,
    "domestic_worker": false
  },
  "policies": []
}
```

### Comparison response

```json
{
  "summary": "Coverage gaps were found. Clarify them before deciding.",
  "diffs": [
    {
      "category": "earthquake",
      "policy_a": "covered, deductible 10%",
      "policy_b": "not listed",
      "practical_effect": "Policy B may leave a catastrophic gap.",
      "severity": "high"
    }
  ],
  "duplicates": [],
  "gaps": ["employer liability not found"],
  "risk_flags": ["Confirm mortgage lender clause before switching."],
  "actions": ["Ask insurer to confirm each listed gap in writing."]
}
```

## CLI input shapes

List form:

```json
[
  {
    "policy_id": "life-a",
    "policy_type": "life",
    "premium_monthly_nis": 95,
    "coverages": {
      "death_benefit": {"covered": true, "limit_nis": 1000000},
      "beneficiaries": {"covered": true, "notes": "spouse"}
    }
  }
]
```

Object form:

```json
{
  "profile": {"mortgage": true, "home_office": true},
  "policies": [
    {
      "policy_id": "home-a",
      "policy_type": "home",
      "premium_monthly_nis": 120,
      "coverages": {"structure": {"covered": true, "limit_nis": 1250000}}
    }
  ]
}
```

## Example responses by domain

### Health

```json
{
  "policy_level_diff": [
    {
      "category": "drugs_outside_basket",
      "policy_a": "covered up to ₪2,000,000",
      "policy_b": "not found",
      "severity": "high",
      "practical_effect": "Policy B may be weaker for expensive medication outside the basket."
    }
  ],
  "actions": [
    "Request the full medication chapter.",
    "Confirm whether medical exclusions apply."
  ]
}
```

### Home

```json
{
  "computed_exposures": [
    {
      "policy_id": "home-a",
      "item": "earthquake deductible",
      "basis_nis": 1200000,
      "percent": 10,
      "exposure_nis": 120000
    }
  ],
  "risk_flags": ["Confirm mortgage lender clause before switching."]
}
```

### Life

```json
{
  "policy_level_diff": [
    {
      "category": "death_benefit",
      "policy_a": "₪1,000,000",
      "policy_b": "₪750,000",
      "severity": "high",
      "practical_effect": "Policy A provides ₪250,000 more before assignment and beneficiary wording."
    }
  ],
  "risk_flags": ["Mortgage assignment may pay the bank before family."]
}
```

## Error table

| Code | Meaning | Cause | Handling |
|---|---|---|---|
| `INVALID_POLICY_TYPE` | Policy type cannot be normalized | Missing or unsupported product | Ask for product name or inspect coverages |
| `MISSING_PREMIUM` | No monthly or annual premium | Price not supplied | Continue coverage comparison and mark cost unknown |
| `MIXED_POLICY_TYPES` | Different policy types supplied | Health compared with home or life | Run overlap/gap analysis, not ranking |
| `MISSING_COVERAGE_MAP` | No structured coverages | Brochure or summary only | Request full policy schedule |
| `SENSITIVE_IDENTIFIER` | Full Israeli ID-like number detected | Unredacted input | Redact before analysis |
| `CURRENCY_AMBIGUOUS` | Amount lacks cadence or currency | `185` without month/year | Ask for billing frequency |
| `DATE_AMBIGUOUS` | Date cannot be parsed safely | `01/02/26` | Request `DD/MM/YYYY` for Hebrew workflows or four-digit year |
| `PORTAL_AUTH_REQUIRED` | Official service requires login | Identity-bound portal | Use manual user flow |
| `REGULATION_VERSION_UNKNOWN` | Rule may have changed | Stale or undated source | Check official publication |
| `REPLACEMENT_RISK` | Cancellation may harm user | Underwriting, waiting, mortgage, beneficiary issue | Add licensed review warning |

## Local HTTP wrapper examples

These examples describe a possible private service around this local package. They are not official Israeli government APIs.

### Validate

```http
POST /v1/policies/validate
Content-Type: application/json
```

```json
{"policies": [{"policy_id": "home-a", "policy_type": "home"}]}
```

```json
{"valid": true, "warnings": {"home-a": ["MISSING_PREMIUM", "MISSING_COVERAGE_MAP"]}}
```

### Compare

```http
POST /v1/policies/compare
Content-Type: application/json
```

```json
{
  "locale": "he-IL",
  "policies": [
    {"policy_id": "health-a", "policy_type": "health", "premium_monthly_nis": 180},
    {"policy_id": "health-b", "policy_type": "health", "premium_monthly_nis": 145}
  ]
}
```

## Practical verification rules

- Validate URLs and publication dates before using a regulatory statement.
- Treat examples such as 10% deductible or 90-day waiting period as scenario data unless the specific policy wording says otherwise.
- Never infer cancellation safety from lower price alone.
- Ask for policy wording, schedule, endorsements, exclusions, and renewal notices before a final recommendation.
- Refer tax, estate, legal, and medical questions to qualified professionals.
