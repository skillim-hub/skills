# API and Local Contract Reference

## Status

This package is local-first. It does not require a remote service. Treat the JSON profile, Python package, and command-line interface as the integration contract.

## Israeli operational references to verify before production

| Area | Operational source | Typical value | Use |
|---|---|---:|---|
| Medical emergency | Magen David Adom dispatch | 101 | Ambulance, CPR, chest pain, stroke, severe injury |
| Police | Israel Police emergency dispatch | 100 | Violence, crime, immediate security threat |
| Fire and rescue | Fire and Rescue Authority | 102 | Fire, smoke, trapped person, rescue |
| Electric hazard | Electric infrastructure emergency line | 103 | Fallen wires or dangerous electrical infrastructure |
| Civil defense | Home Front Command | 104 | Shelter and civil defense guidance |
| Municipal incident | Local authority hotline | 106 or 107 | Local hazards and municipal access issues |
| Volunteer responder | United Hatzalah and local Hatzalah coverage | 1221 where covered | Rapid volunteer response; not a replacement for 101 |
| MDA text/WhatsApp access | MDA accessibility/contact channel | 052-7000-101 | Text-based emergency access where available |

Always verify current numbers, local coverage, and site procedures before printing.

## Israeli legal and regulatory checklist

This checklist is not legal advice. Use qualified advice for formal obligations.

| Topic | Israeli reference area | Practical implication |
|---|---|---|
| Privacy and personal data | Protection of Privacy Law | Store only necessary data and define purpose |
| Database security | Privacy data security regulations | Restrict access, control copies, and manage incidents |
| Medical confidentiality | Patient rights and medical confidentiality duties | Treat medical notes as sensitive |
| Accessibility | Equal rights and service accessibility duties | Make emergency instructions accessible |
| Workplace safety | Workplace safety and labor guidance | Match kit, training, and procedures to workplace risk |
| Fire safety | Fire and rescue requirements | Maintain exits, extinguishers, access paths, and drills |
| Food business | Health and business licensing conditions | Add allergen and contamination workflows |
| Child-facing activity | Child safety and licensing conditions | Add guardian escalation and documentation rules |

## Profile data contract

```json
{
  "id": "generated-local-id",
  "environment": "sandbox",
  "profile_name": "Dizengoff Studio - Front Desk",
  "last_reviewed": "04-06-2026",
  "site": {
    "address_line": "Dizengoff 100, entrance B, floor 2",
    "locality": "Tel Aviv-Yafo",
    "access_notes": "Intercom 22; AED near pharmacy downstairs",
    "aed_location": "Ground floor pharmacy",
    "first_aid_kit_location": "Reception cabinet"
  },
  "emergency_services": {
    "medical": "101",
    "police": "100",
    "fire_rescue": "102",
    "electric": "103",
    "home_front": "104",
    "municipal": "106",
    "united_hatzalah": "1221",
    "mda_sms_whatsapp": "052-7000-101"
  },
  "contacts": [
    {
      "name": "Dana Cohen",
      "role": "Owner",
      "relationship": "business owner",
      "phone": "050-123-4567",
      "priority": 1,
      "can_receive_medical_info": true
    }
  ],
  "medical_notes": {
    "known_allergies": ["latex"],
    "regular_medications": [],
    "conditions_relevant_to_emergency": [],
    "mobility_needs": ["stairs difficult"]
  },
  "consent": {
    "basis": "explicit consent",
    "granted_on": "01-06-2026",
    "review_due": "01-09-2026"
  }
}
```

## Required fields

| Field | Type | Required | Validation |
|---|---|---:|---|
| `profile_name` | string | yes | 2 to 120 characters |
| `last_reviewed` | string | yes | `DD-MM-YYYY` or `DD/MM/YYYY` |
| `site.address_line` | string | yes | Dispatch-ready address |
| `site.locality` | string | yes | City, town, kibbutz, moshav, or locality |
| `contacts` | array | yes | At least one contact |
| `contacts[].name` | string | yes | 2 to 100 characters |
| `contacts[].phone` | string | yes | Israeli phone or supported short code |
| `contacts[].priority` | integer | yes | 1 to 99, unique |

## Command examples

### Create profile

```bash
emergency-contact-first-aid create-profile   --profile-name "North Workshop"   --address "HaTaasiya 4, entrance A"   --locality "Haifa"   --contact-name "Noa Amir"   --contact-phone "050-111-2222"   --store-dir ./.ecfa-sandbox   --env sandbox
```

Response:

```json
{
  "ok": true,
  "id": "local-generated-id",
  "path": ".ecfa-sandbox/local-generated-id.json",
  "environment": "sandbox"
}
```

### Validate by id

```bash
emergency-contact-first-aid validate --profile-id "$PROFILE_ID" --store-dir ./.ecfa-sandbox --env sandbox
```

Response:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "contacts_count": 1
}
```

### Triage prompt

```bash
emergency-contact-first-aid triage --scenario choking --age-group adult --env sandbox
```

Response:

```json
{
  "scenario": "choking",
  "emergency_call": "101",
  "priority": "red",
  "actions": [
    "Call 101 now",
    "Encourage effective coughing",
    "Use abdominal thrusts if trained and airway is blocked",
    "Start CPR if collapse occurs"
  ],
  "do_not": [
    "Do not perform blind finger sweeps"
  ]
}
```

## Error table

| Code | Message | Cause | Fix |
|---|---|---|---|
| `INVALID_DATE` | Review date must use local date format | Date entered as free text or unsupported order | Use `04-06-2026` or `04/06/2026` |
| `MISSING_CONTACT` | At least one emergency contact is required | Contact list is empty | Add primary and secondary contacts |
| `INVALID_PHONE` | Phone must be Israeli phone or supported short code | Typo, extension only, or unsupported number | Use a valid mobile, landline, or emergency short code |
| `DUPLICATE_PRIORITY` | Contact priorities must be unique | Two contacts share the same escalation order | Assign 1, 2, 3 |
| `ID_NUMBER_DETECTED` | Possible Israeli ID number detected | Strict privacy scan found a 9-digit value | Remove unless formally required |
| `STALE_REVIEW` | Review date is more than 90 days old | Contact or access data may be stale | Reconfirm and update date |
| `NO_ACCESS_NOTES` | Access notes are missing | Responders may not find the entrance | Add entrance, floor, gate, and landmark |
| `PUBLIC_PRIVATE_MIX` | Sensitive fields in public export | Full profile used as a public sheet | Use redacted export |

## Internal application equivalents

### Validate profile

Request:

```json
{
  "profile": {
    "profile_name": "North Workshop",
    "last_reviewed": "04-06-2026",
    "site": {
      "address_line": "HaTaasiya 4, entrance A",
      "locality": "Haifa"
    },
    "contacts": [
      {
        "name": "Noa Amir",
        "phone": "050-111-2222",
        "priority": 1
      }
    ]
  },
  "strict_privacy": true
}
```

Response:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [
    "Access notes are missing"
  ],
  "contacts_count": 1
}
```

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Success |
| 1 | Validation failed |
| 2 | File or JSON read failure |
| 3 | Invalid command or unexpected local error |


## Web validation notes

| Item | Result |
|---|---|
| Remote API hosts | Not applicable. The package is local-first and uses no remote emergency-service API. |
| Endpoint paths | Not applicable. CLI commands and Python methods are the only integration surface. |
| Webhook event names | Not applicable. No webhook receiver or sender exists. |
| Official forms | Not applicable for core use. Incident logs are local templates, not official submissions. |
| Fees and fee schedules | Not used. MDA ambulance fees and other service costs are outside this package. |
| VAT | Verified as 18% from 01/01/2025 in official/secondary sources, but not used for calculations. |
| Hatzalah protocols | Public-facing package text uses 101-first public first-aid workflows and records United Hatzalah 1221 as volunteer dispatch. It does not reproduce restricted responder protocols. |
