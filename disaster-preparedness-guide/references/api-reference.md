# Israeli Emergency Channels, Regulations, and Integration Reference

This is an equivalent reference for a non-API skill. It lists official Israeli channels, regulation domains, safe internal schemas, examples, and error handling. Verify current operational details with the relevant authority before deployment.

## Channel and regulation index

| Domain | Israeli body/channel | Public interface | Use |
|---|---|---|---|
| Civil defense | Home Front Command / פיקוד העורף | Website, app, siren, Cell Broadcast, hotline 104 | Alert behavior and protected-space guidance |
| Police/security | Israel Police | 100 | Terrorist infiltration, suspicious object, security threat |
| Fire/rescue/hazmat | Israel Fire and Rescue | 102 | Fire, gas, trapped people, hazmat |
| Medical | Magen David Adom | 101 | Injury and medical emergency |
| Local authority | Municipality/regional council | 106/local hotline | Shelters, infrastructure, local evacuation, welfare |
| Emotional support | ERAN | 1201 | Emotional first aid |
| Civil defense law domain | Civil Defence Law and related instructions | Public law/regulation | Protected-space duties and emergency behavior |
| Planning/building | Planning and Building Law/regulations | Permits and professionals | Mamad construction, structural changes, permits |
| Hazardous substances | Hazardous Substances Law and environmental rules | Permits/enforcement | Chemical storage, spills, disposal |
| Business licensing | Business Licensing Law domain | Local licensing | Shops, food businesses, clinics/workshops where applicable |
| Accessibility | Equal Rights for Persons with Disabilities Law domain | Accessibility duties | Accessible routes and customer/staff support |
| Privacy | Protection of Privacy Law domain | Compliance duties | Emergency contact and health/accessibility notes |
| Workplace safety | Workplace-safety rules | Inspectors/guidance | Staff safety and shutdown routines |
| Tax/accounting | Israel Tax Authority/bookkeeping rules | Accountants/tax systems | Invoices, receipts, payroll, stock, ₪ loss evidence |

## API clarification

Do not claim that this package provides or consumes a stable public Home Front Command alert API. Community feeds and wrappers are not a substitute for official alerting. Life-safety systems require legal, operational, and technical review and should use official channels wherever available.

## Internal request/response examples

### Preparedness plan request

```json
{
  "profile_type": "small_business",
  "city": "Haifa",
  "site_type": "street-level shop",
  "people": {"employees": 4, "customers_peak": 12, "mobility_needs": true},
  "protected_space": {"type": "mamad", "reachable_seconds": 45, "capacity_people": 10},
  "business": {"stores_chemicals": true, "keeps_customer_property": true, "daily_revenue_nis": 3200}
}
```

```json
{
  "status": "ok",
  "risk_flags": ["capacity_exceeded", "hazmat_controls_required", "customer_property_chain_of_custody"],
  "priority_actions": [
    "mark overflow safe area",
    "train shift lead",
    "keep chemical inventory and safety sheets",
    "print customer property log"
  ],
  "records": ["invoices", "receipts", "inventory", "insurance", "incident log in ₪"]
}
```

### Active event request

```json
{"event_type":"earthquake","context":{"has_mamad":true,"near_coast":true,"can_exit_in_seconds":false}}
```

```json
{
  "immediate_actions": [
    "use mamad only as fallback",
    "keep mamad door and window open",
    "avoid elevators",
    "after shaking, watch for tsunami signs and official alerts"
  ],
  "do_not": ["do not seal mamad during shaking", "do not re-enter damaged structure"],
  "official_override": true
}
```

### Business disruption log

```json
{
  "date": "04/06/2026",
  "incident": "missile_alert",
  "closed_minutes": 90,
  "lost_revenue_nis": 850,
  "evidence": ["client cancellation", "invoice draft", "official instruction screenshot"]
}
```

```json
{
  "status": "recorded",
  "next_steps": [
    "save evidence in dated folder",
    "notify client when safe",
    "check insurance notice deadline",
    "ask accountant about bookkeeping classification"
  ]
}
```

## Error table

| Code | Meaning | Common cause | Safe handling |
|---|---|---|---|
| UNKNOWN_EVENT_TYPE | Hazard not recognized | Vague user request | Ask for hazard or provide generic life-safety triage |
| OFFICIAL_CONFLICT | Local plan conflicts with official instruction | Outdated checklist | Follow official instruction |
| NO_PROTECTED_SPACE | No safe area identified | Visitor/outdoor/new site | Use best immediate option and add planning task |
| CAPACITY_EXCEEDED | More people than space | Store/clinic peak load | Mark overflow area and roles |
| ACCESSIBILITY_GAP | Route not accessible | Stairs, narrow doors, clutter | Create accessible alternative and buddy plan |
| UNVERIFIED_ALERT_SOURCE | Source is unofficial | Social media/community bot | Confirm through official channel where possible |
| HAZMAT_BASEMENT_RISK | Basement may be unsafe | Chemical plume | Move indoors/upward unless officials say otherwise |
| EARTHQUAKE_MAMAD_CLOSED | Missile habit used for earthquake | Training gap | Keep door/window open during shaking |
| PRIVACY_OVEREXPOSURE | Too much personal data | Shared emergency sheet | Minimize and restrict access |
| BOOKKEEPING_GAP | Business loss unprovable | No receipts/photos | Start incident log immediately |

## Verification cadence

Emergency numbers quarterly; official guidance during escalations; staff roster monthly; protected-space access weekly for businesses and monthly for homes; first-aid/medication expiry monthly; backup restore quarterly; accessibility route after layout changes; insurance/lease contacts twice yearly.


## Web-validated rate and form notes

As of 04/06/2026, Israel Tax Authority and Knesset public pages state that the general Israeli VAT rate rose to 18% from 01/01/2025. This guide still avoids hard-coding VAT calculations in the CLI because rates, reporting rules, invoice-allocation rules, and sector-specific obligations can change. Verify the current rate with the Israel Tax Authority or an accountant before issuing tax guidance.

Businesses dealing with hazardous substances may require a poisons permit. The Ministry of Environmental Protection states that dealing with poisons under the Hazardous Substances Law requires a permit, and the permit request service states that the fee is determined by business classification. This guide therefore says to maintain inventories, safety data sheets, permit awareness, and official cleanup escalation, but it does not calculate permit fees.

No live external API endpoint, webhook event name, or Home Front Command alert-feed integration is used by this package. The included Python module is an offline preparedness helper only. Do not treat community alert feeds, scraped endpoints, or static content endpoints as an official life-safety API.
