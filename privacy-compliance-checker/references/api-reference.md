# API and Regulation Reference

## Scope

This package is a local decision-support tool. It does not call an official government API, does not submit forms, and does not replace regulator guidance or legal advice. Treat the interfaces below as the supported local API and command reference for generating consistent privacy checks.

## Cited Israeli legal and regulatory sources

| Source | Use in this package |
|---|---|
| Israeli Privacy Protection Law, 5741-1981 | Notice, database governance, direct mailing, data-subject access and correction, controller accountability |
| Protection of Privacy Regulations (Data Security), 5777-2017 | Database specification, access control, logging, supplier controls, incident response, security levels |
| Privacy Protection Authority guidance on database security | Practical evidence expectations for security controls and audits |
| Privacy Protection Authority guidance on severe security incidents | Incident triage, documentation, and notification decision process |
| Privacy Protection Authority guidance on outsourcing and suppliers | Processor contracts, subprocessor tracking, access control, return or deletion |
| Privacy Protection Authority guidance on direct mailing and marketing databases | Source tracking, opt-out, suppression, purpose separation |
| Privacy Protection Authority guidance on employee monitoring | Necessity, proportionality, transparency, access restriction, retention |
| Privacy Protection Authority guidance on minors and sensitive information | Enhanced transparency, minimization, guardian handling, restricted sharing |
| Current database filing or notification rules | Trigger review for sensitive, large, public-body, data-broker, and direct-mailing databases |

Verify current texts and thresholds before submitting a filing, notification, incident report, or legal response.

## GDPR references used by the checker

| GDPR topic | Articles and operational use |
|---|---|
| Principles | Article 5: fairness, transparency, minimization, accuracy, storage limitation, integrity and confidentiality |
| Lawful basis | Article 6 |
| Sensitive data | Article 9 where special categories are involved |
| Transparency and rights | Articles 12-23 |
| Processors | Article 28 |
| Records | Article 30 |
| Security | Article 32 |
| Breach reporting | Articles 33-34 |
| Impact assessment | Article 35 |
| International transfers | Articles 44-49 |

## Python interface

### Import

```python
from privacy_compliance_checker import PrivacyComplianceCheckerClient, AsyncPrivacyComplianceCheckerClient
```

### Create a sync client

```python
client = PrivacyComplianceCheckerClient(environment="sandbox", state_dir=".pcc-state")
```

### Create an async client

```python
client = AsyncPrivacyComplianceCheckerClient(environment="sandbox", state_dir=".pcc-state")
```

### Request schema

```json
{
  "business_name": "Neighborhood customer club",
  "country": "Israel",
  "record_count": 18000,
  "authorized_users": 4,
  "sensitive_categories": [],
  "sector": "retail",
  "purposes": ["loyalty benefits", "receipts", "direct marketing"],
  "data_subjects": ["customers"],
  "lawful_basis": "consent",
  "collects_children_data": false,
  "cross_border": true,
  "destinations": ["United States"],
  "processors": ["email delivery provider", "analytics provider"],
  "direct_marketing": true,
  "uses_tracking": true,
  "uses_ai_profiling": false,
  "data_broker": false,
  "public_body": false,
  "employee_monitoring": false,
  "breach_recent": false,
  "retention_months": 36,
  "privacy_notice_ready": false,
  "processor_contracts_ready": false,
  "rights_process_ready": false,
  "security_controls_ready": false,
  "eu_targeting": false,
  "eu_data_subjects": false,
  "automated_decisions": false
}
```

### Response schema excerpt

```json
{
  "id": "pcc-0123456789ab",
  "environment": "sandbox",
  "created_at": "2026-06-02T09:00:00+00:00",
  "security_level": "medium",
  "gdpr_applicable": false,
  "score": 63,
  "israel_obligations": [
    "Prepare a database specification and processing inventory.",
    "Apply medium security controls under a practical reading of the Data Security Regulations."
  ],
  "findings": [
    {
      "code": "DM-001",
      "title": "Direct marketing controls required",
      "severity": "warning",
      "description": "Marketing lists require source tracking, clear opt-out, suppression-list handling, and separation from service messages.",
      "actions": [
        "Store consent or permissible source details per recipient.",
        "Add an unsubscribe channel to each marketing message."
      ],
      "references": [
        "Israeli direct mailing rules",
        "Anti-spam obligations may also apply"
      ]
    }
  ],
  "checklist": [
    {
      "id": "INV-001",
      "area": "inventory",
      "task": "Document database name, controller, purposes, fields, sources, recipients, and retention.",
      "owner": "privacy owner",
      "due_days": 14,
      "evidence": "database specification",
      "status": "open"
    }
  ]
}
```

## Official form and endpoint reference

The helper is a local, non-network tool. It does not submit filings, reports, or webhook events. Use official services manually after review.

| Item | Official location | Notes |
|---|---|---|
| Serious data-security incident report | `https://mojforms.justice.gov.il/mojaemprivacyprotectionauthority/databreachupdate.html` | Initial immediate report form for serious security incidents. Do not automate submission. |
| Database registration service | `https://www.gov.il/he/service/registration_in_the_database` | Use only after verifying Amendment 13 registration duties and factual database details. |
| API hosts | Not applicable | No government API host is called by the package. |
| Webhook event names | Not applicable | The package has no inbound or outbound webhook contract. |

## Field dictionary

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `business_name` | string | No | Human-readable workflow name |
| `country` | string | No | Default is Israel |
| `record_count` | integer | No | Must be zero or greater |
| `authorized_users` | integer | No | Must be one or greater |
| `sensitive_categories` | string list | No | Use values such as `health`, `financial`, `national_id`, `children`, `biometric` |
| `sector` | string | No | Adds context for findings but does not replace statutory triggers |
| `purposes` | string list | No | Use concrete purposes, not generic labels |
| `data_subjects` | string list | No | Customers, employees, suppliers, minors, EU users |
| `lawful_basis` | string | No | `consent`, `contract`, `legal_obligation`, `vital_interests`, `public_task`, `legitimate_interests`, `unknown` |
| `collects_children_data` | boolean | No | Raises risk and checklist depth |
| `cross_border` | boolean | No | Adds transfer controls |
| `destinations` | string list | No | Required for complete transfer review |
| `processors` | string list | No | Adds processor-contract controls |
| `direct_marketing` | boolean | No | Adds direct-mailing controls |
| `uses_tracking` | boolean | No | Adds tracker controls |
| `uses_ai_profiling` | boolean | No | Adds profiling assessment |
| `data_broker` | boolean | No | Indicates activity that may trigger medium security, registration, and DPO review |
| `public_body` | boolean | No | Indicates public-body database duties, including registration and DPO review |
| `employee_monitoring` | boolean | No | Adds proportionality checks |
| `breach_recent` | boolean | No | Adds incident workflow |
| `retention_months` | integer or null | No | Must be zero or greater |
| `privacy_notice_ready` | boolean | No | Reduces notice findings |
| `processor_contracts_ready` | boolean | No | Reduces processor findings |
| `rights_process_ready` | boolean | No | Reduces rights findings |
| `security_controls_ready` | boolean | No | Reduces security findings |
| `eu_targeting` | boolean | No | Adds GDPR checks |
| `eu_data_subjects` | boolean | No | Adds GDPR checks |
| `automated_decisions` | boolean | No | Raises profiling severity |

## CLI commands

### Assess without saving

```bash
privacy-compliance-checker assess --scenario customer-club --format markdown
```

### Create and save

```bash
privacy-compliance-checker --env sandbox create --scenario customer-club --format json
```

Response:

```json
{
  "id": "pcc-0123456789ab",
  "path": ".pcc-state/pcc-0123456789ab.json",
  "environment": "sandbox",
  "score": 63
}
```

### Read a saved record

```bash
privacy-compliance-checker --env sandbox get pcc-0123456789ab --format json
```

### Update a saved record

```bash
privacy-compliance-checker --env sandbox update pcc-0123456789ab --json '{"privacy_notice_ready": true}'
```

### Generate checklist only

```bash
privacy-compliance-checker checklist clinic.json --format markdown
```

### Validate input

```bash
privacy-compliance-checker validate clinic.json
```

## Error table

| Error | Cause | Fix |
|---|---|---|
| `payload must be a mapping` | Python caller passed a list, string, or null | Pass a dictionary object |
| `Unknown assessment fields` | Request contains unsupported keys | Remove or map unsupported keys |
| `record_count must be zero or greater` | Negative count supplied | Use zero or a positive integer |
| `authorized_users must be one or greater` | Zero or negative user count supplied | Provide at least one authorized user |
| `lawful_basis must be one of` | Invalid basis supplied | Use one of the supported basis values |
| `environment must be sandbox or production` | Unsupported environment | Use `sandbox` or `production` |
| `Provide exactly one of --json, --file, or --scenario` | CLI input is ambiguous | Provide one input source |
| `assessment not found` | Saved ID does not exist in the state directory | Use `list` or set the correct `PCC_STATE_DIR` |
| `Invalid JSON` | Malformed JSON string or file | Validate JSON syntax |
| `fmt must be markdown or json` | Unsupported export format | Use `markdown` or `json` |

## Security and privacy of the tool

The package runs locally. It does not send assessment data to external services. Still avoid entering live secrets, full patient files, full customer exports, passwords, tokens, or production credentials into example payloads. Use representative categories and counts instead.
