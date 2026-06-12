# Workflow Guide

Use these workflows to run the skill consistently for Israeli consumers, freelancers, and small businesses.

## Workflow 1: Consumer comparing private clinic and HMO-affiliated route

### Input
```json
{
  "context": {
    "provider": "private",
    "region": "center",
    "start_date": "10/07/2026",
    "insurance": {"name": "self_pay", "discount_pct": 0}
  },
  "treatments": [
    {"code": "exam"},
    {"code": "xray_bitewing"},
    {"code": "cleaning"},
    {"code": "filling_large", "tooth": "26"}
  ]
}
```

### Steps
1. Validate the plan.
2. Add missing diagnostics if the clinic quote does not include them.
3. Estimate private route.
4. Compare against `maccabident` and `clalit_smile`.
5. Build a question list for the clinic.

### Expected output
- Cost table in ₪.
- Provider comparison table.
- Warning if the quote lacks written scope.
- Request for itemized quote with exclusions.

## Workflow 2: Urgent pain and suspected root canal

### Trigger
The user reports pain, swelling, fever, trauma, or uncontrolled bleeding.

### Steps
1. Do not optimize first for cost.
2. Classify as urgent or emergency.
3. Add `emergency_visit`, `exam`, and relevant X-ray.
4. Estimate root-canal scenario and crown uncertainty.
5. Output same-day triage instruction and questions.

### Example treatment list
```json
[
  {"code": "emergency_visit", "urgency": "emergency"},
  {"code": "exam", "urgency": "urgent"},
  {"code": "xray_bitewing", "urgency": "urgent"},
  {"code": "root_canal_molar", "tooth": "46", "urgency": "urgent"},
  {"code": "crown_porcelain", "tooth": "46"}
]
```

### Clinic questions
- Is drainage, antibiotics, or pain control required before definitive treatment?
- Is the tooth restorable?
- Is the crown included or quoted separately?
- What is the earliest appointment?

## Workflow 3: Freelancer cash-flow planning

### Goal
Plan treatment without ignoring medical priority.

### Steps
1. Split treatments into urgent, necessary, preventive, and elective.
2. Estimate each phase.
3. Set `max_visits_per_month` based on income and availability.
4. Use the generated schedule to map payments by month.
5. Add accountant questions without giving tax advice.

### Output table
| Month | Medical priority | Visits | Estimated payment | Notes |
|---|---|---:|---:|---|
| 07-2026 | urgent/restorative | 2 | ₪... | Do not defer active infection |
| 08-2026 | rehabilitation | 2 | ₪... | Confirm lab milestone |
| 09-2026 | elective | 1 | ₪... | Delay if cash flow is tight |

## Workflow 4: Implant quote review

### Steps
1. Check whether imaging exists.
2. Identify whether extraction, bone graft, sinus lift, temporary tooth, implant crown, and follow-up are included.
3. Estimate staged payments.
4. Compare private and HMO-affiliated routes.
5. Highlight uncertainties that can materially change price.

### Required written quote fields
- Tooth number.
- Implant brand or system if disclosed by clinic.
- Surgical stage price.
- Prosthetic crown price.
- Imaging and surgical guide.
- Temporary tooth.
- Bone graft or sinus lift if applicable.
- Medication and follow-up.
- Validity period.

## Workflow 5: Child prevention and routine care

### Steps
1. Confirm child age and plan route.
2. Add examination before fluoride or sealants.
3. Estimate preventive bundle.
4. Ask provider about age-based eligibility and covered treatments.
5. Schedule around school availability.

### Output warning
Do not assume free or subsidized care without current plan verification.

## Workflow 6: Small business assisting an employee

### Steps
1. Keep clinical details minimal.
2. Estimate total support amount without storing unnecessary medical information.
3. Separate employer reimbursement policy from medical plan.
4. Recommend accountant review for tax treatment.
5. Use written quote and receipt tracking.

### Privacy guardrail
Avoid collecting diagnosis, full dental chart, ID number, or sensitive clinical notes unless necessary and protected.

## Workflow 7: Second-opinion preparation

### Steps
1. Convert the first quote into structured treatment codes.
2. Mark unknowns and missing dependencies.
3. Generate questions for the second clinic.
4. Compare apples to apples: same tooth, same material, same lab inclusion, same imaging.
5. Do not frame the first quote as wrong; ask for clinical explanation.

## Workflow 8: Monthly budget cap

### Input extension
```json
{"context": {"max_visits_per_month": 2}}
```

### Steps
1. Keep urgent care in the earliest month.
2. Move elective and cosmetic work later.
3. Ask whether the clinic allows installments or staged payments.
4. Show the medical risk of delaying non-elective treatment.

## Workflow 9: Quote translation from Hebrew clinic text

| Hebrew wording | Code |
|---|---|
| בדיקה | `exam` |
| צילום נשך | `xray_bitewing` |
| צילום פנורמי | `panoramic_xray` |
| שיננית / ניקוי אבנית | `cleaning` |
| סתימה קטנה | `filling_small` |
| סתימה גדולה | `filling_large` |
| טיפול שורש טוחנת | `root_canal_molar` |
| כתר חרסינה | `crown_porcelain` |
| שתל | `implant` |
| עקירה כירורגית | `extraction_surgical` |

## Workflow 10: Final handoff checklist

Before the user calls the clinic, provide:

- Structured treatment list.
- Estimated total and low-confidence items.
- Provider comparison.
- Schedule and cash-flow view.
- Questions about coverage, exclusions, materials, lab, and specialist identity.
- Emergency warning when applicable.
