# API and Regulation Reference

This package is offline-first. Israeli health funds and private insurers do not expose one unified public claim API for all claim submissions. Use this reference to model local records, CLI payloads, and compliance checks while submitting actual claims through the relevant insurer, health fund, agent, branch, or official portal.

## Official Israeli sources verified for this package

This package is non-API software. It keeps local operational records and does not submit claims to insurers, health funds, the Ministry of Health, the Tax Authority, or the Capital Market Authority. Use payer portals, branches, agents, or official channels for the binding submission.

| Area | Official source | URL | Package use | Verification status |
|---|---|---|---|---|
| National health framework | Ministry of Health, National Health Insurance Law information | `https://www.gov.il/he/departments/general/health-insurance-law-info` | Distinguish statutory health coverage from supplementary and private claims. | Double-confirmed in `references/verification-log.md`. |
| Supplementary health services | Ministry of Health SHABAN principles | `https://www.gov.il/he/pages/shaban_principles` | Map `supplementary` to שירותי בריאות נוספים (שב"ן). | Double-confirmed. |
| Public rights comparison | Kol HaBriut comparison pages | `https://call.gov.il/page/compare-page` | Use for rights and plan comparison only, not claim submission. | Double-confirmed. |
| Private-policy overlap | Ministry of Health health-insurance reform | `https://www.gov.il/he/pages/reform-health-insurance` | Support separate payer records and double-coverage checks. | Double-confirmed. |
| Policy lookup | Har HaBituach | `https://harb.cma.gov.il/` | Discover policy existence; avoid storing login credentials. | Double-confirmed. |
| Insurance tariff comparison | Capital Market health-insurance calculator | `https://briut.cma.gov.il/` | Review policy context; no claim API is used. | Double-confirmed. |
| Claim handling | Capital Market claim-settlement instructions | `https://www.gov.il/he/pages/settling-consumer-complaints` | Track statuses without hard-coded statutory response deadlines. | Double-confirmed. |
| Patient documentation | Ministry of Health and Patient's Rights Law materials | `https://www.gov.il/he/pages/medical-information` | Request medical summaries and records when needed. | Double-confirmed. |
| Privacy | Privacy Protection Authority materials | `https://www.gov.il/he/departments/the_privacy_protection_authority` | Apply minimization, restricted access, redaction, and incident escalation. | Double-confirmed. |
| Data security | Privacy Protection Regulations (Data Security) | `https://www.gov.il/he/pages/data_security_regulation` | Production checklist for access control, backup, and incident handling. | Double-confirmed. |
| Electronic records | Electronic Signature Law and regulations | `https://www.gov.il/he/pages/electronic_signature_law2` | Keep electronic-document guidance generic. | Double-confirmed. |
| VAT and bookkeeping | Israel Tax Authority VAT glossary and Israel Invoice notices | `https://www.gov.il/en/pages/taxes-glossary` | Record gross amounts; do not calculate VAT or validate allocations. | Double-confirmed. |

### API hosts, endpoints, and webhooks

No official external API host, endpoint path, or webhook event name is implemented by this package. The executable interface is the local Python package and the local `hict` CLI. The JSON and CSV structures in this document are local payloads, not official Israeli government or insurer API contracts.

### VAT and invoice cautions

The standard Israeli VAT rate was verified as 18% from 01/01/2025. This tracker stores claim and reimbursement amounts only. Do not use it to determine whether VAT applies to a medical service, whether input VAT is deductible, or whether an Israel Invoice allocation number is required. Store source documents and consult the accounting workflow.

## Local data schema

### Claim object

```json
{
  "id": "HICT-20260604-AB12CD34",
  "claimant_reference": "client-7788",
  "policy_type": "private",
  "provider": "Example Insurance",
  "service_date": "2026-04-15",
  "submission_date": "2026-04-20",
  "amount_claimed_ils": "850.00",
  "description": "Private specialist consultation",
  "status": "submitted",
  "channel": "portal",
  "policy_number_last4": "7788",
  "service_kind": "consultation",
  "documents": [],
  "reimbursements": [],
  "timeline": [],
  "follow_up_date": "2026-05-20",
  "notes": "",
  "tags": ["private", "consultation"]
}
```

### Field reference

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Generated | Stable local identifier. |
| `claimant_reference` | string | Yes | Prefer internal reference, not full identity number. |
| `policy_type` | enum | Yes | `supplementary`, `private`, `national`, or `other`. |
| `provider` | string | Yes | Health fund, insurer, or payer name. |
| `service_date` | date | Yes | Accepts `YYYY-MM-DD`, `DD/MM/YYYY`, or `DD-MM-YYYY`. |
| `submission_date` | date | Yes | Cannot be before service date. |
| `amount_claimed_ils` | decimal string | Yes | Positive amount, rounded to two decimals. |
| `description` | string | Yes | Short service and claim description. |
| `status` | enum | Yes | See status table in `SKILL.md`. |
| `channel` | string | No | Portal, branch, email, agent, or other route. |
| `policy_number_last4` | string | No | Last four digits only. |
| `service_kind` | string | No | Used to build document checklist. |
| `documents` | array | No | Each document has name, type, received flag, and notes. |
| `reimbursements` | array | No | Record each payment separately. |
| `follow_up_date` | date or null | No | Use for overdue tracking. |

## CLI request and response examples

### Create claim

Request:

```bash
hict --env production create \
  --claimant-reference client-7788 \
  --policy-type private \
  --provider "Example Insurance" \
  --service-date 15/04/2026 \
  --submission-date 20/04/2026 \
  --amount 850.00 \
  --description "Private specialist consultation" \
  --channel portal \
  --service-kind consultation \
  --follow-up-date 20/05/2026
```

Response:

```json
{
  "id": "HICT-20260604-AB12CD34",
  "claimant_reference": "client-7788",
  "policy_type": "private",
  "provider": "Example Insurance",
  "service_date": "2026-04-15",
  "submission_date": "2026-04-20",
  "amount_claimed_ils": "850.00",
  "status": "submitted",
  "total_reimbursed_ils": "0.00",
  "reimbursement_gap_ils": "850.00"
}
```

### Add reimbursement

Request:

```bash
hict --env production reimburse HICT-20260604-AB12CD34 \
  --amount 300.00 \
  --paid-date 10/05/2026 \
  --payer "Example Insurance" \
  --reference "bank deposit 5510"
```

Response:

```json
{
  "id": "HICT-20260604-AB12CD34",
  "status": "submitted",
  "total_reimbursed_ils": "300.00",
  "reimbursement_gap_ils": "550.00"
}
```

### Export CSV

Request:

```bash
hict --env production export-csv ./claims-export.csv
```

Response:

```json
{
  "path": "claims-export.csv"
}
```

## Python client examples

### Synchronous use

```python
from health_insurance_claim_tracker import HealthInsuranceClaimTrackerClient

client = HealthInsuranceClaimTrackerClient("claims.json")
claim = client.create_claim(
    claimant_reference="client-7788",
    policy_type="private",
    provider="Example Insurance",
    service_date="15/04/2026",
    submission_date="20/04/2026",
    amount_claimed_ils="850.00",
    description="Private specialist consultation",
)
print(claim.id)
```

### Asynchronous use

```python
import asyncio
from health_insurance_claim_tracker import AsyncHealthInsuranceClaimTrackerClient

async def main():
    client = AsyncHealthInsuranceClaimTrackerClient("claims.json")
    claim = await client.create_claim(
        claimant_reference="client-7788",
        policy_type="private",
        provider="Example Insurance",
        service_date="15/04/2026",
        submission_date="20/04/2026",
        amount_claimed_ils="850.00",
        description="Private specialist consultation",
    )
    print(claim.id)

asyncio.run(main())
```

## Error table

| Error | Trigger | Fix |
|---|---|---|
| `ValidationError: claimant_reference is required` | Empty claimant reference. | Use an internal reference or short masked identifier. |
| `ValidationError: amount_claimed_ils must be positive` | Zero or negative claim amount. | Enter a positive ₪ amount. |
| `ValidationError: submission_date cannot be before service_date` | Date order is impossible. | Correct the service or submission date. |
| `ValidationError: service_date cannot be in the future` | Service date is later than the configured clock date. | Use the actual past service date. |
| `ValidationError: policy_number_last4 must contain only digits` | Non-digit characters in last four digits. | Store four digits only. |
| `ClaimNotFoundError` | Unknown claim id. | Confirm storage path and claim id. |
| `ClaimTrackerError: Storage file is not valid JSON` | JSON store is corrupted or not a tracker file. | Restore backup or repair the JSON file. |

## Integration notes for Israeli systems

- Treat insurer portals as systems of record for official submission, but keep a local operational copy.
- Avoid storing passwords, portal cookies, or full identity numbers in the tracker.
- If a business stores medical information for employees or customers, review privacy classification, access control, and retention obligations before production use.
- For claim submission through an agent, record the agent channel, sent date, and confirmation evidence.
- For paper branch submissions, scan stamped confirmations and link the document filename to the local claim id.
