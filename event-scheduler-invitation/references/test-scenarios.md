# Test Scenarios

Use these scenarios to verify documentation, scripts, RSVP workflows, and planning logic. Expected outputs can be adapted to the user’s exact context, but the risk flags must appear.

## Wedding scenarios

1. **Standard wedding, 250 guests**  
   Input: 320 invited, 250 expected, ₪330 per plate, Rehovot, 18/06/2026.  
   Expected: venue total ₪82,500, RSVP deadline, seating freeze, licensing checklist, capacity buffer.

2. **Thursday summer wedding budget pressure**  
   Input: Thursday in June, 300 guests, premium venue, budget ₪150,000.  
   Expected: flag peak pricing; suggest Sunday-Wednesday, winter date, lower minimum, menu negotiation.

3. **Outdoor winter garden wedding**  
   Input: garden venue in January.  
   Expected: rain plan, indoor chuppah, heating, covered photography, supplier setup protection.

4. **Separated parents seating conflict**  
   Input: bride’s parents cannot sit together.  
   Expected: conflict groups, separate family tables, private notes, no public exposure.

5. **Wheelchair guest**  
   Input: grandmother needs wheelchair access.  
   Expected: verify step-free route, accessible toilet, parking, table placement, venue confirmation.

6. **Mixed-language family**  
   Input: Israeli and French guests.  
   Expected: Hebrew and French/English message variants, single guest ID, language field.

7. **Civil ceremony celebration**  
   Input: celebration in Israel after civil marriage abroad.  
   Expected: separate celebration logistics from legal recognition; avoid legal assumptions.

8. **Late marriage-registration discovery**  
   Input: wedding 18 days away, traditional ceremony.  
   Expected: urgent authority contact; document risk; avoid guaranteeing resolution.

## Bar/Bat mitzvah scenarios

9. **Synagogue plus evening party**  
   Input: Shabbat synagogue and Sunday party.  
   Expected: two linked events, separate RSVP counts, honors list, party supervision plan.

10. **Classmates without parents**  
    Input: 35 classmates invited to party.  
    Expected: pickup time, adult supervision, allergies, emergency contact.

11. **Allergy in school group**  
    Input: parent reports nut allergy.  
    Expected: specific follow-up, caterer confirmation, avoid broad medical history.

12. **Torah portion conflict**  
    Input: family travel on target Shabbat.  
    Expected: alternate synagogue date or separate party date.

13. **Shabbat observant guests**  
    Input: many guests do not drive on Shabbat.  
    Expected: accommodation/hosting notes, walking distance, Friday setup constraints.

## Brit milah and naming scenarios

14. **Birth before sunset**  
    Input: birth 03/03/2026 before sunset.  
    Expected: target ceremony 10/03/2026, subject to medical/rabbinic confirmation.

15. **Birth after sunset**  
    Input: birth 03/03/2026 after sunset.  
    Expected: target date shifts by one day in helper logic; flag confirmation.

16. **Medical postponement**  
    Input: baby not cleared.  
    Expected: postpone; medical clearance overrides schedule.

17. **Home event in apartment**  
    Input: 35 guests in Givatayim apartment.  
    Expected: elevator, stroller area, chairs, neighbor notice, parking, waste plan.

18. **Last-minute naming ceremony**  
    Input: event tomorrow.  
    Expected: minimal guest list, phone/WhatsApp notice, limited catering risk.

## Small business and consumer scenarios

19. **Customer appreciation event**  
    Input: freelancer invites 80 customers.  
    Expected: consent/opt-out check, invoice tracking, minimal RSVP data.

20. **Workshop with paid tickets**  
    Input: small business sells 40 tickets.  
    Expected: receipts/invoices, cancellation policy, accessibility, attendee privacy.

21. **Community fundraiser**  
    Input: synagogue/community center fundraiser.  
    Expected: donation/payment separation, seating, accessibility, opt-out for future messages.

22. **Private birthday at rented venue**  
    Input: 70 guests, DJ, food.  
    Expected: music license checkpoint, noise cutoff, parking, dietary list.

## Data and tooling scenarios

23. **Duplicate phone numbers**  
    Input: two records with 050-1234567 and +972501234567.  
    Expected: duplicate detection and merge recommendation.

24. **Invalid phone number**  
    Input: 12345.  
    Expected: validation warning and manual follow-up.

25. **Confirmed exceeds invited**  
    Input: invited 2, confirmed 4.  
    Expected: party-size warning and explicit approval requirement.

26. **No-response sweep**  
    Input: 40 no-response guests one week before event.  
    Expected: segmentation, caller assignment, deadline message.

27. **Transport manifest**  
    Input: 48 guests need shuttle.  
    Expected: bus size recommendation and pickup list.

28. **Venue minimum mismatch**  
    Input: venue minimum 220, expected 180.  
    Expected: negotiate or select alternative; budget impact shown.

29. **Supplier VAT unclear**  
    Input: quote ₪10,000 without VAT note.  
    Expected: request itemized quote and invoice terms.

30. **Data cleanup after event**  
    Input: event closed.  
    Expected: delete dietary/accessibility/conflict notes unless still required; retain accounting documents.


31. **Invoice allocation threshold after 01/06/2026**
    Input: supplier invoice ₪6,000 before VAT dated 02/06/2026.
    Expected: flag allocation-number follow-up and show ₪5,000 threshold.

32. **Invoice allocation threshold before 01/06/2026**
    Input: supplier invoice ₪6,000 before VAT dated 31/05/2026.
    Expected: no allocation-number follow-up under the ₪10,000 threshold, but still require itemized VAT.

33. **ACUM family-event fee**
    Input: wedding with DJ on 18/06/2026.
    Expected: add ACUM checkpoint, 72-hour buffer, and current family-event fee reference ₪395.30.

34. **ACUM business-event separation**
    Input: small business customer evening with background music for 120 people.
    Expected: do not use family-event fee; direct to business-event tariff check.

35. **Noise-monitor venue question**
    Input: outdoor garden event with late music.
    Expected: ask about business license, noise monitor, 95 dB threshold handling, closing hour, and neighbors.
