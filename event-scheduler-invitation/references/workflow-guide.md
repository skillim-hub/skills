# Workflow Guide

Use these workflows as end-to-end operating procedures. Adjust dates, budget, religious requirements, and supplier dependencies to the specific event.

## Workflow 1: Wedding from inquiry to closeout

### Intake

Collect the following in one structured record:

| Field | Example |
|---|---|
| Event title | חתונת מאיה ויונתן |
| Date | 18/06/2026 |
| City/region | רחובות, מרכז |
| Invited households | 160 |
| Estimated guests | 250 |
| Venue status | 3 options under review |
| Ceremony path | Traditional Jewish ceremony |
| Main constraints | Grandmother needs wheelchair access; many guests from Jerusalem |

### Step-by-step

1. **Build the guest model**  
   Create stable guest IDs. Add household name, contact person, phone, invited count, side, language, children, dietary, accessibility, and transport fields.

2. **Create a venue shortlist**  
   Compare capacity, minimum guests, price per plate, parking, accessibility, rain plan, kashrut certificate, cancellation terms, and supplier restrictions.

3. **Model the budget**  
   Calculate venue total as expected guests times price per plate. Add fixed supplier costs, contingency, licensing, transport, and tips.

4. **Lock critical suppliers**  
   Close venue first, then photographer, music, ceremony lead, design, makeup/hair, transport, and event manager.

5. **Prepare RSVP wording**  
   Use Hebrew default wording with a response deadline. Create a phone-call path for guests unlikely to answer digitally.

6. **Send invitations in waves**  
   Send family and VIPs first to catch errors. Send the full list only after testing links, date, map, and phone formatting.

7. **Track responses daily**  
   Merge duplicates. Flag missing party size, missing children count, dietary notes, accessibility, and transport requests.

8. **Finalize counts and seating**  
   Freeze seating 10-14 days before the event. Keep a reserve table or reserve seats if venue allows.

9. **Run supplier confirmation**  
   Confirm arrival times, loading, payment, VAT documents, insurance, music license, generator, weather backup, and emergency contact.

10. **Execute day-of run sheet**  
    Print the run sheet, seating chart, transport list, vendor contacts, family VIP list, and emergency contacts.

11. **Close out**  
    Pay balances against invoices, collect receipts, send thank-you messages, delete unnecessary guest data, and archive final records.

### Wedding deliverables

- Event brief
- Budget table
- Venue comparison table
- Guest master sheet
- RSVP message set
- Supplier call sheet
- Seating plan
- Transport manifest
- Ceremony checklist
- Day-of run sheet
- Closeout checklist

## Workflow 2: Bar/Bat mitzvah with two-part event

### Scenario

A family holds a synagogue event on Shabbat morning and a separate party on Sunday evening.

### Steps

1. Create two linked events: `synagogue_kiddush` and `evening_party`.
2. Track attendance separately for each guest.
3. Confirm synagogue customs, aliyah honors, photographer rules, and kiddush timing.
4. Confirm party venue, DJ/activity, menu, security, school-friend supervision, pickup policy, and noise limits.
5. Send invitations with two RSVP questions:
   - "מגיעים לקידוש?"
   - "מגיעים למסיבה?"
6. Build separate counts:
   - Synagogue adults
   - Synagogue children
   - Party adults
   - Party classmates
   - Vegetarian/vegan/gluten-free
   - Accessibility
   - Transport
7. Prepare an honors list for synagogue and a seating/activity map for the party.
8. Confirm final counts with each venue/supplier.

### Message example

> שלום {name}, נשמח לראותך בבר המצווה של {child_name}.  
> נא לאשר הגעה בנפרד: קידוש בבית הכנסת ב-{synagogue_date}, ומסיבה ב-{party_date}.  
> ציינו מספר מגיעים, ילדים, רגישויות למזון וצורך בנגישות או הסעה.

### Risk controls

- Do not assume every synagogue guest attends the party.
- Do not invite an entire class without pickup and supervision instructions.
- Do not publish photos of minors without checking family expectations.
- Do not schedule supplier setup during Shabbat where observance or venue rules prohibit it.

## Workflow 3: Brit milah or naming ceremony under uncertainty

### Scenario

A baby is born on 03/03/2026. The family wants an intimate home event.

### Steps

1. Record date and time of birth, including whether birth was before or after sunset.
2. Ask parents to confirm medical status through appropriate professionals.
3. Contact mohel/ceremony lead with flexible timing.
4. Choose small location options: home, synagogue hall, small café room, grandparents' building lounge.
5. Send conditional notice only to close family:
   - "האירוע מתוכנן ל-{date}, בכפוף לאישור רפואי. נעדכן סופית."
6. Delay large catering commitments until 24-48 hours before.
7. Prepare home logistics: chairs, table, baby supplies, quiet room, parking, elevator, stroller area, trash bags, neighbor notice.
8. Assign one logistics contact who is not a parent.
9. After ceremony, send thank-you note and remove unnecessary health notes.

### Risk controls

- Medical clearance overrides schedule.
- Avoid definitive wording before confirmation.
- Keep guest list small when timing is uncertain.
- Verify Shabbat/holiday implications with qualified guidance.

## Workflow 4: Small-business customer event

### Scenario

A freelancer or small business hosts a customer appreciation evening for 80 clients in Tel Aviv.

### Steps

1. Define purpose: retention, product demo, community, training, or celebration.
2. Separate event invitation from marketing promotion.
3. Use opt-in customer lists where possible.
4. Include clear sender identity and opt-out text in bulk messages.
5. Collect minimal RSVP data: name, phone/email, company, attendance, dietary/accessibility.
6. Choose venue based on accessibility, public transport, parking, projector/sound, invoice terms, and cancellation policy.
7. Confirm VAT invoice and supplier identity for every paid supplier.
8. Prepare attendee check-in list and privacy notice.
9. Avoid adding guests to future marketing without consent.
10. Delete no-show notes and unnecessary dietary/accessibility data after closeout.

### Message example

> שלום {name}, נשמח להזמינך לערב לקוחות של {business_name} בתאריך {date}.  
> מספר המקומות מוגבל. לאישור הגעה נא להשיב "מגיע/ה". להסרה מהודעות אירוע כתבו "הסר".

## Workflow 5: Venue comparison and negotiation

### Inputs

- Expected guests
- Maximum budget
- Preferred cities
- Event type
- Date flexibility
- Accessibility needs
- Kashrut requirements
- Parking/transport needs
- Weather exposure
- Music/noise expectations

### Comparison table

| Factor | Weight | Ask the venue | Red flag |
|---|---:|---|---|
| Capacity | 20% | "What is seated capacity with dance floor?" | Capacity stated without layout |
| Minimum guests | 15% | "What is the minimum and final-count deadline?" | Final count locked too early |
| Price | 15% | "Is VAT included? What is excluded?" | Unclear service/security cost |
| Accessibility | 15% | "Is there step-free access and accessible toilet?" | Generic "accessible" answer |
| Parking | 10% | "How many spaces and where are overflow lots?" | No written parking plan |
| Weather | 10% | "What happens in rain/heat/wind?" | Outdoor-only plan |
| Contract | 10% | "What are cancellation and postponement terms?" | Deposit terms unclear |
| Operations | 5% | "When can suppliers enter?" | Setup time too short |

### Negotiation levers

- Move from Thursday to Sunday-Wednesday.
- Pick winter or low-demand dates.
- Reduce guaranteed minimum.
- Add upgrade option instead of high starting menu.
- Ask for included extras: projector, basic design, parking signage, soft drinks, late-night snack.
- Request written final-count deadline.
- Clarify VAT, service, security, overtime, and cancellation.

## Workflow 6: Final 72-hour control room

### 72 hours before

- Confirm guest count and table count.
- Confirm no-response list and last phone-call sweep.
- Confirm dietary/accessibility list with venue.
- Confirm transport pickups and passenger count.
- Confirm supplier arrival times.
- Verify music licensing where applicable.
- Print seating chart and vendor call sheet.

### 24 hours before

- Send final logistics to guests.
- Send supplier call sheet.
- Prepare payment envelopes or transfer confirmations where appropriate.
- Export offline guest list.
- Charge phones and backup battery packs.
- Confirm emergency contacts.

### Event day

- Check venue setup before guests arrive.
- Place printed seating list at entrance.
- Keep accessibility seats reserved.
- Track no-shows only for operational purposes.
- Escalate vendor delays through one coordinator.
- Log incidents for post-event follow-up.

## Workflow 7: Post-event data cleanup

1. Reconcile supplier invoices and payment confirmations.
2. Save accounting documents in the business archive.
3. Delete unnecessary dietary, accessibility, and family-conflict notes.
4. Keep only records needed for accounting, disputes, or consent logs.
5. Send thank-you messages without promotional upsell unless consent exists.
6. Record lessons learned: guest response rate, venue issues, supplier performance, budget variance.


## Web-validated tax and licensing workflow

Use this workflow for a freelancer, family organizer, or small business that pays Israeli suppliers or runs a customer event.

1. Capture quote amount before VAT, VAT amount, supplier ID, invoice number, invoice date, and payment method.
2. Use the 18% VAT planning rate only for estimates; rely on the supplier invoice for the final VAT amount.
3. If the invoice is dated 01/01/2026-31/05/2026 and exceeds ₪10,000 before VAT, flag allocation-number follow-up.
4. If the invoice is dated 01/06/2026 or later and exceeds ₪5,000 before VAT, flag allocation-number follow-up.
5. For family events using protected music, add an ACUM checkpoint up to 72 hours before the event and budget ₪395.30 including VAT unless the portal states otherwise.
6. For customer or company events, use the ACUM business-event tariff instead of the family-event fee.
7. For venue due diligence, ask for business-license status, accessibility arrangements, kashrut certificate scope, insurance, closing hour, and noise-monitor handling.
8. Store receipts, allocation numbers, and license confirmations in the closeout folder.
