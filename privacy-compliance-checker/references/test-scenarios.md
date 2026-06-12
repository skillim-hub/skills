# Test Scenarios

Use these scenarios for manual review, examples, and regression tests. Each scenario includes expected focus areas rather than legal conclusions.

| ID | Scenario | Key facts | Expected checks |
|---:|---|---|---|
| 1 | Freelancer lead list | 350 leads, names, phones, project notes, cloud spreadsheet | Basic security, retention, notice, access restriction |
| 2 | Online customer club | 18,000 customers, coupons, purchases, overseas email provider | Medium security, direct marketing, transfer, unsubscribe |
| 3 | Private clinic | 12,000 patients, health data, ID numbers, appointment platform | Medium security under statutory thresholds, sensitive notice, processors, logging, incident procedure |
| 4 | Wrong-recipient export | 4,200 customer records sent to wrong recipient | Breach log, containment, notification decision, remediation |
| 5 | Cloud service with EU users | EU users, hosting in Germany, support in United States | GDPR, processing record, transfer review, processor terms |
| 6 | Accountant office | 1,100 client files, tax records, ID numbers, cloud backup | Sensitive financial data, retention, supplier controls |
| 7 | Hair salon reminders | 2,500 customers, appointments, birthday coupons | Marketing consent, suppression, basic security |
| 8 | Youth sports club | 900 minors, health declarations, parent contacts | Children data, health data, guardian notice, medium security with enhanced safeguards |
| 9 | Employee monitoring | 70 employees, laptop monitoring, screenshots possible | Necessity, proportionality, notice, retention, access restriction |
| 10 | Job applicants | 3,000 CVs, interview notes, diversity information | Sensitive categories, retention, access restriction, deletion requests |
| 11 | Building access control | 1,500 residents, entry logs, license plates, cameras | Surveillance notice, retention, security, access limitation |
| 12 | Donation platform | 8,000 donors, payment references, political causes | Sensitive inference, processor terms, retention, transparency |
| 13 | School parent portal | 2,200 students, grades, parent contacts | Minors, education data, access logs, enhanced safeguards |
| 14 | Dental clinic marketing | Patient list reused for implants campaign | Purpose compatibility, consent, direct marketing, special-category sensitivity |
| 15 | Loyalty app analytics | Device identifiers, purchase prediction, overseas analytics | Tracking, profiling, transfer, consent controls |
| 16 | Consumer deletion request | Former customer asks deletion, invoices remain | Rights workflow, legal hold, partial deletion, response evidence |
| 17 | Supplier onboarding | Support provider receives ticket access and attachments | Processor contract, subprocessor list, transfer, access limitation |
| 18 | Data enrichment vendor | Marketing list enriched with external demographic data | Source, transparency, direct mailing, profiling, opt-out |
| 19 | Public-body contractor | Vendor processes municipal resident records | Medium or high security by scale, public-body controls, processor terms, audit evidence |
| 20 | Ransomware event | Encrypted files, uncertain exfiltration, sensitive records | Incident response, evidence preservation, notification assessment |
| 21 | Payment provider switch | Online store adds new payment gateway and fraud tool | Processor terms, notice update, transfer, minimization |
| 22 | Community mailing list | 600 subscribers, events and donations, unsubscribe complaints | Consent/source, suppression, direct marketing, deletion |
| 23 | Fitness studio app | Health goals, attendance, body metrics, push notifications | Health-related data, direct marketing, retention, security |
| 24 | Marketplace seller dashboard | Buyers, sellers, disputes, tax documents, EU sellers | Role mapping, GDPR, rights, retention, processor terms |
| 25 | AI support triage | Tickets classified by model, possible sensitive free text | Profiling, minimization, human review, processor and transfer review |
| 26 | Archive migration | Old spreadsheets imported into managed system | Inventory, deduplication, stale-data deletion, access review |
| 27 | Survey prize draw | Consumer survey, optional marketing, prize delivery | Purpose separation, consent, retention after draw, notice |
| 28 | CCTV in retail store | Cameras, workers, customers, theft prevention | Surveillance notice, proportionality, retention, access controls |
| 29 | Cross-border contractor | Contractor abroad can access production records | Transfer, processor access, confidentiality, least privilege |
| 30 | Biometric attendance | Fingerprint attendance for small employer | Special-sensitivity data, necessity, alternative methods, legal review |
| 31 | Medical appointment reminders | SMS reminder provider receives names and appointment dates | Processor terms, health context, minimization, transfer |
| 32 | Breach false alarm | Alert triggered, logs show no access to personal data | Incident log, decision rationale, close-out evidence |
| 33 | Data subject access request | Customer asks for all records and source | Identity check, system search, response deadline, redaction |
| 34 | Consent repermission | Old newsletter list lacks proof | Repermission, suppression, source tracking, deletion of stale records |
| 35 | Support recordings | Calls recorded for quality with payment details | Notice, minimization, redaction, retention, access restriction |
| 36 | Overseas backup | Local system backs up encrypted database abroad | Transfer, encryption, key control, processor terms |

## Scenario payload examples

### Customer club

```json
{
  "business_name": "Neighborhood customer club",
  "record_count": 18000,
  "authorized_users": 4,
  "sector": "retail",
  "purposes": ["loyalty benefits", "receipts", "direct marketing"],
  "lawful_basis": "consent",
  "direct_marketing": true,
  "uses_tracking": true,
  "cross_border": true,
  "destinations": ["United States"],
  "processors": ["email delivery provider", "analytics provider"],
  "retention_months": 36
}
```

### Clinic

```json
{
  "business_name": "Private clinic patient system",
  "record_count": 12000,
  "authorized_users": 9,
  "sensitive_categories": ["health", "national_id"],
  "sector": "clinic",
  "purposes": ["treatment", "billing", "appointment reminders"],
  "lawful_basis": "legal_obligation",
  "processors": ["appointment platform", "billing provider"],
  "retention_months": 120
}
```

### Breach

```json
{
  "business_name": "Misdirected customer export",
  "record_count": 4200,
  "authorized_users": 3,
  "sensitive_categories": ["financial"],
  "sector": "retail",
  "purposes": ["support"],
  "lawful_basis": "contract",
  "breach_recent": true,
  "security_controls_ready": false
}
```

### Cloud transfer

```json
{
  "business_name": "Cloud workflow service",
  "record_count": 65000,
  "authorized_users": 25,
  "sensitive_categories": ["employment"],
  "sector": "software",
  "purposes": ["account management", "support", "product analytics"],
  "lawful_basis": "legitimate_interests",
  "cross_border": true,
  "destinations": ["Germany", "United States"],
  "processors": ["hosting provider", "support system", "log processor"],
  "eu_targeting": true,
  "eu_data_subjects": true,
  "uses_ai_profiling": true
}
```

## Regression checklist

For every scenario, verify:

- Security level is explainable.
- Israeli obligations are present.
- GDPR is applied only when facts support it.
- Findings include concrete actions.
- Checklist contains owner, due date, evidence, and status.
- JSON output preserves Hebrew and special characters.
- Markdown output contains no public decorative icons.
- CLI and Python client produce equivalent findings.
