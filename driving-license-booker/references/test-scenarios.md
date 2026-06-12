# Test Scenarios

Use these scenarios for acceptance testing, manual QA, and regression checks.

| # | Scenario | Given | Expected |
| --- | --- | --- | --- |
| 1 | Valid renewal | valid ID, mobile phone, expiry 31/08/2026 | record is ready for official handoff |
| 2 | Invalid ID | ID checksum fails | validation stops before handoff |
| 3 | Phone with +972 | +972501234567 | phone normalizes to 0501234567 |
| 4 | Expired license | expiry date before today | warning is added |
| 5 | Unpaid fee | fee not marked paid | readiness has blocker |
| 6 | Medical declaration missing | declaration required but not completed | readiness has blocker |
| 7 | License number missing | renewal without license number | warning is added |
| 8 | Bureau appointment no windows | empty preferred date list | client raises validation error |
| 9 | Bureau appointment with accessibility | accessibility flag true | payload stores operational flag |
| 10 | Practical test missing teacher | blank teacher name | client raises validation error |
| 11 | Practical test pickup city | pickup city supplied | payload and message include city |
| 12 | Teacher phone invalid | teacher phone too short | client raises validation error |
| 13 | State persistence | create record with state file | get returns same record |
| 14 | Cancel record | cancel existing record | status becomes cancelled |
| 15 | List by status | two records, one cancelled | filter returns matching status |
| 16 | Request id extraction | create response object | request id is extracted |
| 17 | Request id from JSON | create response JSON | request id is extracted |
| 18 | Invalid response id | response without id | client raises validation error |
| 19 | Local date formatting | 2026-08-31 | format is 31/08/2026 |
| 20 | Business day deadline | Thursday plus two business days | deadline skips weekend |
| 21 | Service links | client link map | official handoff links exist |
| 22 | Roster export | two applicants | both normalize correctly |
| 23 | Async create and get | async client with state file | get returns created record |
| 24 | CLI renewal chain | create command then get command | request id from create works in get |

## Acceptance rules

- Run every validation scenario before production use.
- Keep tests deterministic; do not depend on live government systems.
- Use sandbox records for staff training.
- Verify Hebrew customer messages separately from JSON payloads.
- Confirm that every create command returns a `request_id` and every follow-up command uses that exact value.


## Web-validation regression scenarios

| ID | Scenario | Input | Expected result |
| --- | --- | --- | --- |
| 21 | Driver-license payment link | `build_service_links()` | `license_payment` equals `https://ecom.gov.il/voucherspa/input/209`. |
| 22 | Deprecated vehicle-payment route | link set contains a vehicle-license payment route | validation flags route as wrong for driver-license renewal. |
| 23 | GoVisit appointment link | `build_service_links()` | appointment link uses `govisit.gov.il`, not a deprecated host. |
| 24 | Practical-test fee link | `build_service_links()` | `practical_test_payment` equals `https://ecom.gov.il/voucherspa/input/427`. |
| 25 | Practical-test confirmation | teacher has not confirmed | local record remains coordination draft or ready for handoff, not confirmed. |
| 26 | Private service VAT check | service fee invoice prepared | VAT rate is verified before invoicing; 18% is used only after current-rate confirmation. |
