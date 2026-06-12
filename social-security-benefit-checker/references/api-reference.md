# Reference: official sources and local interfaces

This skill does not integrate with a public government entitlement service. Use it as a local screening interface, then verify every conclusion against official Israeli sources.

## Official source map

| Domain | Official source to verify | What to verify |
| --- | --- | --- |
| National Insurance benefits | National Insurance Institute website and personal service area | eligibility pages, claim forms, amount tables, payment routing, document requirements |
| Primary legislation | National Insurance Law [Consolidated Version], 5755-1995 | entitlement framework, insured status, benefit families, appeal routes |
| Unemployment | National Insurance Institute unemployment guidance and Israel Employment Service instructions | qualifying period, registration rules, separation reason, waiting period, reporting duties |
| Employment registration | Israel Employment Service systems and local bureau instructions | registration date, attendance, work-test status, availability for work |
| General disability | National Insurance Institute general disability guidance and medical committee instructions | medical disability percent, degree of incapacity, income effect, appeal deadline |
| Income supplement | Income Support Law, 5741-1980 and National Insurance Institute income supplement guidance | household status, means test, assets, vehicle rules, work-test exemptions |
| Child allowance | National Insurance Institute child allowance guidance and Population and Immigration Authority registry data | child registration, age, custody, guardianship, bank account routing |
| Privacy and data security | Protection of Privacy Law, 5741-1981 and applicable privacy regulations | lawful basis, minimization, retention, access control, medical confidentiality |
| Accounting evidence | Israel Tax Authority records, bookkeeping documents, accountant confirmations | self-employed profit, wage slips, advance payments, business closure evidence |

## Verified official URLs

Record access date `02/06/2026` when relying on the bundled constants.

| Area | Official URL | Verified item |
| --- | --- | --- |
| VAT | https://www.gov.il/he/pages/vat-history | VAT changed to 18% on 01/01/2025. |
| VAT interpretation | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf | Tax Authority transition instruction for 17% to 18%. |
| Unemployment conditions | https://www.btl.gov.il/benefits/Unemployment/Pages/zakaut.aspx | age, residency, work separation, registration, qualifying period. |
| Unemployment calculation | https://www.btl.gov.il/benefits/Unemployment/Pages/hisuv.aspx | 2026 daily base amount and daily ceilings. |
| Employment Service registration | https://www.taasuka.gov.il/applicants/registertolishkaguide/ | unemployment calculation starts from registration date. |
| General disability eligibility | https://www.btl.gov.il/benefits/Disability/Pages/%D7%94%D7%96%D7%9B%D7%90%D7%99%D7%9D%20%D7%9C%D7%A7%D7%A6%D7%91%D7%AA%20%D7%A0%D7%9B%D7%95%D7%AA%20%D7%97%D7%95%D7%93%D7%A9%D7%99%D7%AA.aspx | medical disability and incapacity thresholds. |
| General disability amounts | https://www.btl.gov.il/benefits/Disability/Pages/%D7%A9%D7%99%D7%A2%D7%95%D7%A8%D7%99%20%D7%94%D7%A7%D7%A6%D7%91%D7%94.aspx | 2026 monthly amounts by incapacity degree. |
| Child allowance rates | https://www.btl.gov.il/benefits/children/Pages/%D7%A9%D7%99%D7%A2%D7%95%D7%A8%D7%99%20%D7%94%D7%A7%D7%A6%D7%91%D7%94.aspx | 2026 rates by birth order. |
| Child allowance eligibility | https://www.btl.gov.il/benefits/children/Pages/default.aspx | families living in Israel with children up to age 18. |
| Income support eligibility | https://www.btl.gov.il/benefits/Income_support/Pages/zacautnew.aspx | residency, low income, assets and vehicle review. |
| Income support amounts | https://www.btl.gov.il/benefits/Income_support/Pages/%D7%A1%D7%9B%D7%95%D7%9E%D7%99%20%D7%94%D7%A7%D7%A6%D7%91%D7%94.aspx | 2026 amount and work-income cap table. |
| Income support form | https://www.btl.gov.il/%D7%98%D7%A4%D7%A1%D7%99%D7%9D%20%D7%95%D7%90%D7%99%D7%A9%D7%95%D7%A8%D7%99%D7%9D/forms/Income_Support_forms/Pages/5619%20-%20%D7%98%D7%95%D7%A4%D7%A1%20%D7%9E%D7%99%D7%9C%D7%95%D7%99%20%D7%A2%D7%A6%D7%9E%D7%99-%D7%AA%D7%91%D7%99%D7%A2%D7%94%20%D7%9C%D7%92%D7%9E%D7%9C%D7%AA%20%D7%94%D7%91%D7%98%D7%97%D7%AA%20%D7%94%D7%9B%D7%A0%D7%A1%D7%94.aspx | form 5619 and 2026 blocker values. |
| Privacy | https://www.gov.il/en/departments/the_privacy_protection_authority | personal information protection authority. |

No public entitlement API, endpoint host, or webhook event is used by this package. Keep integrations local unless an official authenticated service is separately contracted and documented.

## Regulation and policy citation practice

For each operational deployment, record the following in the case file:

```json
{
  "source_name": "National Insurance Institute unemployment guidance",
  "source_date_checked": "02/06/2026",
  "rule_area": "qualifying period and Employment Service registration",
  "operator": "caseworker",
  "notes": "Verify against current official page before final advice."
}
```

Use DD/MM/YYYY dates in Israeli-facing records.

## Local Python request and response

Request:

```python
from social_security_benefit_checker import ApplicantProfile, SocialSecurityBenefitChecker

profile = ApplicantProfile.from_mapping(
    {
        "age": 42,
        "resident": True,
        "employment_status": "unemployed",
        "monthly_income": 8500,
        "children_count": 2,
        "qualifying_months": 14,
        "termination_reason": "laid_off",
        "registered_employment_service": True,
        "birth_dates": ["12/04/2018", "30/09/2021"],
    }
)

checker = SocialSecurityBenefitChecker(environment="sandbox")
created = checker.create_profile(profile)
result = checker.check_profile_id(created["profile_id"], benefit="all")
```

Response shape:

```json
{
  "profile_id": "prof_4f7b73c39c18",
  "environment": "sandbox",
  "results": [
    {
      "benefit": "unemployment",
      "status": "likely_eligible",
      "eligible": true,
      "confidence": "medium",
      "estimated_monthly_ils_min": 4675.0,
      "estimated_monthly_ils_max": 5500.0,
      "reasons": ["Employment ended for a recognized unemployment pathway."],
      "missing_info": [],
      "documents": ["Employment Service registration confirmation"],
      "next_steps": ["Register with the Employment Service immediately."],
      "warnings": [],
      "reference_notes": ["Estimated amount is a conservative planning range and is not an official calculation."]
    }
  ]
}
```

## Local CLI request and response

Create request:

```bash
social-security-benefit-checker create-profile --file profile.json --env sandbox
```

Create response:

```json
{
  "created": true,
  "profile_id": "prof_4f7b73c39c18",
  "created_at": "2026-06-02T10:00:00Z",
  "environment": "sandbox"
}
```

Check request using the identifier from the create response:

```bash
social-security-benefit-checker check --profile-id prof_4f7b73c39c18 --benefit income_supplement --env sandbox
```

Check response:

```json
{
  "profile_id": "prof_4f7b73c39c18",
  "environment": "sandbox",
  "results": [
    {
      "benefit": "income_supplement",
      "status": "likely_eligible",
      "eligible": true,
      "confidence": "medium",
      "estimated_monthly_ils_min": null,
      "estimated_monthly_ils_max": null,
      "reasons": ["Household income ₪8,500 is at or below the 2026 screening income cap ₪9,865."],
      "missing_info": [],
      "documents": ["income documentation for all adults in the household"],
      "next_steps": ["Calculate household income after allowed deductions."],
      "warnings": [],
      "reference_notes": ["Retest after income changes, separation, birth of a child, rent change, or asset change."]
    }
  ]
}
```

## Benefit keys

| Key | Meaning |
| --- | --- |
| `unemployment` | דמי אבטלה |
| `general_disability` | קצבת נכות כללית |
| `child_allowance` | קצבת ילדים |
| `income_supplement` | הבטחת הכנסה |

## Status values

| Status | Meaning | Required action |
| --- | --- | --- |
| `likely_eligible` | Preliminary data supports a claim path | Verify official rules, prepare documents, submit or advise with human review |
| `possibly_eligible` | A path may exist but a warning or exception applies | Collect evidence and review the exception |
| `not_likely` | A gate check failed | Check whether an official exception exists before closing the case |
| `insufficient_information` | Required fields are missing | Add each item listed in `missing_info` |

## Input field reference

| Field | Type | Used by | Notes |
| --- | --- | --- | --- |
| `age` | integer | all | Use age at claim date where possible |
| `resident` | boolean | all | Israeli residency is a common gate check |
| `employment_status` | string | unemployment, income supplement | Use normalized values from README |
| `monthly_income` | number | unemployment, disability, income supplement | For self-employed users, use current profit rather than turnover |
| `spouse_income` | number | income supplement | Include household income when relevant |
| `children_count` | integer | child allowance, income supplement | Combine with birth dates for child allowance |
| `household_type` | string | income supplement | `single`, `couple`, or `single_parent` |
| `qualifying_months` | integer | unemployment | Count recognized work months |
| `termination_reason` | string | unemployment | Use `resigned_justified` only with supporting evidence |
| `registered_employment_service` | boolean | unemployment, income supplement | Distinguish between registration and exemption |
| `birth_dates` | list of strings | child allowance | Prefer DD/MM/YYYY |
| `medical_disability_percent` | number or null | general disability | Use official or expected committee percent only for screening |
| `work_capacity_loss_percent` | number or null | general disability | Use official or expected incapacity degree only for screening |
| `assets_exceed_limit` | boolean | income supplement | Use current official asset rules |
| `vehicle_value_exceeds_limit` | boolean | income supplement | Flag possible blocker or exception review |
| `receives_other_benefit` | boolean | income supplement | Concurrent benefits can affect eligibility |

## Error table

| Error | Cause | Correction |
| --- | --- | --- |
| `AGE_OUT_OF_RANGE` | Age is missing, negative, or above 120 | Enter a realistic age |
| `RESIDENT_MUST_BE_BOOLEAN` | Residency was not provided as true or false | Use `true` or `false` |
| `MONTHLY_INCOME_NEGATIVE` | Income was entered as a negative number | Enter zero or a positive amount |
| `SPOUSE_INCOME_NEGATIVE` | Spouse income was negative | Enter zero or a positive amount |
| `CHILDREN_COUNT_NEGATIVE` | Child count was negative | Enter zero or a positive integer |
| `QUALIFYING_MONTHS_NEGATIVE` | Qualifying months were negative | Enter zero or a positive integer |
| `MEDICAL_DISABILITY_PERCENT_OUT_OF_RANGE` | Medical percent outside 0 to 100 | Enter a value from 0 to 100 |
| `WORK_CAPACITY_LOSS_PERCENT_OUT_OF_RANGE` | Capacity-loss percent outside 0 to 100 | Enter a value from 0 to 100 |
| `CLAIM_DATE_INVALID` | Claim date format was unsupported | Use DD/MM/YYYY, DD-MM-YYYY, or ISO YYYY-MM-DD |
| `Profile not found` | Unknown local profile identifier | Use the identifier from `create-profile` response or list saved profiles |

## Non-goals

The package does not:

- submit claims
- retrieve official personal data
- decide entitlement
- calculate official payment amounts
- store identity numbers or medical files
- replace legal, accounting, medical, or government review

## Implementation notes

Use the installable package for production code:

```python
from social_security_benefit_checker import SocialSecurityBenefitChecker
```

Use `scripts/social_security_benefit_checker_client.py` for direct inspection, examples, or copy-based integration. Avoid importing a hyphenated file name.
