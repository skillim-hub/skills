# Official-Service and Adapter Reference

This is a non-public-API workflow reference. Israeli driving-license renewal, Licensing Bureau appointments, payments, and practical-test coordination are handled through official services and regulated actors. Treat every automated step as a preparation or handoff unless an approved organizational gateway is available.

## Official service inventory

| Area | Official source type | Validated URL or host | Use in this package | Automation boundary |
| --- | --- | --- | --- | --- |
| License renewal | Ministry of Transport and Road Safety service page on gov.il | `https://www.gov.il/he/service/driving_license_renewal` | Handoff link and readiness checklist | Do not automate identity verification or final submission. |
| License fee payment | Government payment service | `https://ecom.gov.il/voucherspa/input/209` | Payment handoff and receipt capture | Do not store card data. Record only receipt metadata. |
| Practical-test fee payment | Government payment service | `https://ecom.gov.il/voucherspa/input/427` | Payment handoff for practical-test fee | Confirm mutable amounts at payment time. |
| Licensing Bureau appointments | Ministry appointment page and GoVisit | `https://www.gov.il/he/service/summoning-turn-transport`, `https://govisit.gov.il/he/authorities/authority/29` | Appointment handoff and reminder tracking | Do not scrape queues or bypass identity checks. |
| Driver application and medical declaration | Driver-license application service and medical declaration flow | `https://www.gov.il/he/service/apply_for_new_driver_drivers_license` | Medical blocker and new-license checklist | Do not collect unnecessary medical details. |
| Practical driving test | Authorized driving teacher, school, and official test process | `https://www.gov.il/he/service/apply_for_new_driver_drivers_license`, `https://driverstudent.mot.gov.il` | Teacher message, candidate windows, reminder tracking | Do not mark test confirmed before teacher or school confirmation. |
| Fees table | Official fee board | `https://www.gov.il/he/pages/drivers-car-license-fee-boards?chapterIndex=4` | Fee awareness and escalation | Do not hard-code mutable fees into business promises. |
| Privacy and records | Israeli privacy obligations for personal data | Business policy and customer consent records | Data minimization and retention checklist | Keep only necessary personal data and consent records. |

## Public API and webhook status

No official public API contract, endpoint schema, or webhook event catalog was confirmed for driver-license renewal, Licensing Bureau appointment booking, or practical-test scheduling. Treat the URLs above as browser handoff targets. Use the adapter protocol only for an approved organizational gateway under explicit permission.

Public hosts used by the workflow: `www.gov.il`, `ecom.gov.il`, `govisit.gov.il`, `govforms.gov.il`, `my.gov.il`, and `driverstudent.mot.gov.il`.

## Validated service link example

```json
{
  "license_renewal": "https://www.gov.il/he/service/driving_license_renewal",
  "license_payment": "https://ecom.gov.il/voucherspa/input/209",
  "practical_test_payment": "https://ecom.gov.il/voucherspa/input/427",
  "transport_appointment_info": "https://www.gov.il/he/service/summoning-turn-transport",
  "licensing_bureau_appointment": "https://govisit.gov.il/he/authorities/authority/29",
  "driver_application_and_medical_declaration": "https://www.gov.il/he/service/apply_for_new_driver_drivers_license",
  "driver_student_area": "https://driverstudent.mot.gov.il"
}
```

## Client request objects

### Renewal payload

```json
{
  "kind": "license_renewal",
  "workflow": "license_renewal",
  "environment": "sandbox",
  "applicant": {
    "full_name": "Dana Levi",
    "national_id": "039456785",
    "phone": "0501234567",
    "license_number": "1234567",
    "email": null,
    "date_of_birth": null,
    "license_class": "B"
  },
  "expiry_date": "2026-08-31",
  "include_payment_step": true,
  "notes": "Customer wants SMS reminder"
}
```

### Bureau appointment payload

```json
{
  "kind": "bureau_appointment",
  "workflow": "bureau_appointment",
  "environment": "sandbox",
  "applicant": {
    "full_name": "Moshe Cohen",
    "national_id": "123456782",
    "phone": "0527654321",
    "license_number": "7654321",
    "email": null,
    "date_of_birth": null,
    "license_class": "B"
  },
  "windows": [
    {
      "date": "2026-07-15",
      "start_time": null,
      "end_time": null,
      "city": "Haifa",
      "branch": null
    }
  ],
  "service_city": "Haifa",
  "reason": "license renewal assistance",
  "accessibility_needed": true
}
```

### Practical-test payload

```json
{
  "kind": "practical_test",
  "workflow": "practical_test",
  "environment": "sandbox",
  "applicant": {
    "full_name": "Noa Israeli",
    "national_id": "039456785",
    "phone": "0501234567",
    "license_number": null,
    "email": null,
    "date_of_birth": null,
    "license_class": "B"
  },
  "windows": [
    {
      "date": "2026-07-20",
      "start_time": null,
      "end_time": null,
      "city": "Rishon LeZion",
      "branch": null
    }
  ],
  "teacher": {
    "name": "Avi",
    "phone": "0521111111"
  },
  "pickup_city": "Rishon LeZion",
  "vehicle_class": "B"
}
```

## Client response object

```json
{
  "request_id": "f5f94e74-d6b7-4033-9f73-4b03a1d80303",
  "status": "ready_for_handoff",
  "kind": "license_renewal",
  "created_at": "2026-06-04T10:00:00+00:00",
  "next_steps": [
    "Verify identity and license details on the official service.",
    "Pay the renewal fee only through an official payment page.",
    "Save the confirmation number and receipt in the customer record."
  ],
  "payload": {},
  "confirmation_number": null,
  "appointment_reference": null
}
```

## Error table

| Code | Trigger | Resolution |
| --- | --- | --- |
| `INVALID_ID_CHECKSUM` | Israeli ID has invalid checksum | Re-enter ID, normalize to nine digits, and retry validation. |
| `INVALID_PHONE` | Phone is not a valid Israeli 0-prefixed number | Convert +972 to local format or request corrected number. |
| `MISSING_WINDOW` | Appointment or practical-test request has no date window | Add at least one preferred date. |
| `MISSING_TEACHER` | Practical-test request lacks teacher name | Add authorized teacher name before handoff. |
| `PAYMENT_BLOCKED` | Renewal fee not paid or not confirmed | Use the official driver-license payment route `/voucherspa/input/209` and wait for receipt. |
| `WRONG_PAYMENT_ROUTE` | Vehicle-license payment route used for driver-license renewal | Stop and restart with `/voucherspa/input/209`; do not reuse a vehicle-license route. |
| `MEDICAL_DECLARATION_REQUIRED` | Medical declaration is required and incomplete | Complete official declaration before renewal completion. |
| `NO_APPOINTMENTS` | Preferred city has no available slots | Search nearby cities and later dates. |
| `OFFICIAL_SERVICE_DOWN` | Official website unavailable | Retry later and keep local record in draft. |
| `DATA_MISMATCH` | Name, ID, or license details do not match official records | Prepare bureau appointment and document mismatch. |
| `ACCESSIBILITY_UNCONFIRMED` | Accessibility request not reflected in appointment | Contact official appointment channel and record response. |

## Adapter protocol

Organizations with an approved internal gateway may inject a transport object implementing `create`, `get`, and `cancel` methods. The adapter must return the same response fields as the local client. Do not connect an adapter to protected public portals unless the organization has explicit permission.

```python
from typing import Mapping, Any

class ApprovedGateway:
    def create(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "request_id": "internal-123",
            "status": "submitted",
            "confirmation_number": "CN-55555"
        }

    def get(self, request_id: str) -> Mapping[str, Any]:
        return {
            "request_id": request_id,
            "status": "confirmed",
            "kind": "license_renewal",
            "created_at": "2026-06-04T10:00:00+00:00",
            "payload": {}
        }

    def cancel(self, request_id: str, reason: str | None = None) -> Mapping[str, Any]:
        return {
            "request_id": request_id,
            "status": "cancelled",
            "kind": "license_renewal",
            "created_at": "2026-06-04T10:00:00+00:00",
            "payload": {},
            "cancellation_reason": reason
        }
```

## Data retention guidance

Keep only the fields needed to complete the service. Prefer request id, official confirmation number, ₪ amount, VAT treatment for private service fees where applicable, receipt date, and reminder status over copies of identity documents. Delete temporary documents once the official service no longer requires them for the business record.
