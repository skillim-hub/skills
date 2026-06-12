# Test Scenarios

Use these scenarios to validate the workflow, client, CLI, and internal procedure.

| # | Scenario | Expected result |
|---:|---|---|
| 1 | Municipal fine found and unpaid | Status `verified_unpaid`; payment checklist created. |
| 2 | Municipal fine already paid | Status `verified_paid`; payment blocked; receipt requested. |
| 3 | Hyphenated plate not found at first | Normalized plate succeeds. |
| 4 | Correct portal still returns not found | Status `lookup_not_found`; issuer contact task created. |
| 5 | Amount increased after due date | Discrepancy flagged; breakdown required. |
| 6 | Parking app covers enforcement time | Contest checklist created. |
| 7 | Parking app used wrong plate | Contest weakness flagged; payment review. |
| 8 | Resident permit valid but wrong zone | Zone mismatch warning. |
| 9 | Disabled parking card expired | Evidence insufficient unless renewal proof exists. |
| 10 | Company vehicle driver known | Transfer review created. |
| 11 | Company vehicle driver unknown | Investigation checklist created. |
| 12 | Leasing company paid automatically | Duplicate payment risk flagged. |
| 13 | Employee paid personally | Reimbursement workflow triggered. |
| 14 | Road 6 toll principal only | Business toll classification suggested. |
| 15 | Road 6 toll plus enforcement fee | Split accounting categories. |
| 16 | Toll notice for sold vehicle | Transfer/cancellation evidence checklist created. |
| 17 | Collection letter without breakdown | Payment blocked; breakdown required. |
| 18 | Collection letter with verified original fine | Reconcile and approve or escalate. |
| 19 | Police traffic ticket with points | Legal escalation required. |
| 20 | Court summons | Legal escalation required; payment-only flow disabled. |
| 21 | Payment failed but card authorized | Duplicate risk status; no immediate retry. |
| 22 | Receipt missing after payment | Receipt retrieval workflow. |
| 23 | Appeal pending near due date | Follow-up reminder and status check. |
| 24 | Hebrew date DD/MM/YYYY | Internal ISO date created correctly. |
| 25 | CSV duplicate notice number | Duplicate flagged. |
| 26 | OCR misreads notice number | Manual verification required. |
| 27 | SMS payment link received | Official-domain verification required. |
| 28 | Former employee fine | Transfer deadline and HR/payroll review. |

## Detailed scenarios

### 1. Municipal fine found and unpaid

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Status `verified_unpaid`; payment checklist created. Evidence is saved, status is updated, and the next action is recorded.

### 2. Municipal fine already paid

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Status `verified_paid`; payment blocked; receipt requested. Evidence is saved, status is updated, and the next action is recorded.

### 3. Hyphenated plate not found at first

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Normalized plate succeeds. Evidence is saved, status is updated, and the next action is recorded.

### 4. Correct portal still returns not found

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Status `lookup_not_found`; issuer contact task created. Evidence is saved, status is updated, and the next action is recorded.

### 5. Amount increased after due date

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Discrepancy flagged; breakdown required. Evidence is saved, status is updated, and the next action is recorded.

### 6. Parking app covers enforcement time

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Contest checklist created. Evidence is saved, status is updated, and the next action is recorded.

### 7. Parking app used wrong plate

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Contest weakness flagged; payment review. Evidence is saved, status is updated, and the next action is recorded.

### 8. Resident permit valid but wrong zone

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Zone mismatch warning. Evidence is saved, status is updated, and the next action is recorded.

### 9. Disabled parking card expired

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Evidence insufficient unless renewal proof exists. Evidence is saved, status is updated, and the next action is recorded.

### 10. Company vehicle driver known

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Transfer review created. Evidence is saved, status is updated, and the next action is recorded.

### 11. Company vehicle driver unknown

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Investigation checklist created. Evidence is saved, status is updated, and the next action is recorded.

### 12. Leasing company paid automatically

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Duplicate payment risk flagged. Evidence is saved, status is updated, and the next action is recorded.

### 13. Employee paid personally

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Reimbursement workflow triggered. Evidence is saved, status is updated, and the next action is recorded.

### 14. Road 6 toll principal only

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Business toll classification suggested. Evidence is saved, status is updated, and the next action is recorded.

### 15. Road 6 toll plus enforcement fee

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Split accounting categories. Evidence is saved, status is updated, and the next action is recorded.

### 16. Toll notice for sold vehicle

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Transfer/cancellation evidence checklist created. Evidence is saved, status is updated, and the next action is recorded.

### 17. Collection letter without breakdown

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Payment blocked; breakdown required. Evidence is saved, status is updated, and the next action is recorded.

### 18. Collection letter with verified original fine

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Reconcile and approve or escalate. Evidence is saved, status is updated, and the next action is recorded.

### 19. Police traffic ticket with points

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Legal escalation required. Evidence is saved, status is updated, and the next action is recorded.

### 20. Court summons

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Legal escalation required; payment-only flow disabled. Evidence is saved, status is updated, and the next action is recorded.

### 21. Payment failed but card authorized

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Duplicate risk status; no immediate retry. Evidence is saved, status is updated, and the next action is recorded.

### 22. Receipt missing after payment

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Receipt retrieval workflow. Evidence is saved, status is updated, and the next action is recorded.

### 23. Appeal pending near due date

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Follow-up reminder and status check. Evidence is saved, status is updated, and the next action is recorded.

### 24. Hebrew date DD/MM/YYYY

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Internal ISO date created correctly. Evidence is saved, status is updated, and the next action is recorded.

### 25. CSV duplicate notice number

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Duplicate flagged. Evidence is saved, status is updated, and the next action is recorded.

### 26. OCR misreads notice number

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Manual verification required. Evidence is saved, status is updated, and the next action is recorded.

### 27. SMS payment link received

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Official-domain verification required. Evidence is saved, status is updated, and the next action is recorded.

### 28. Former employee fine

Input: representative notice data with issuer, vehicle number, notice number, amount, and due date.

Expected: Transfer deadline and HR/payroll review. Evidence is saved, status is updated, and the next action is recorded.




## Web-validated scenarios

### 29. Official portal only, no public API

Expected:

- Workflow uses official portal/manual confirmation or authorized middleware.
- Public endpoint paths are not labeled as official Israeli APIs.
- Webhook event names are internal only.

### 30. VAT treatment check

Expected:

- System records the official VAT rate as 18% for context.
- System does not assume the fine or penalty includes recoverable VAT.
- Accountant review is required for deductibility or input-tax treatment.

### 31. Source-specific deadline

Expected:

- Tel Aviv, Road 6, Fast Lane, and other issuers each use their own current notice or official page.
- Deadline from one issuer is not reused for another issuer.
