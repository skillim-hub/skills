# Test scenarios

Use these scenarios for manual QA, demonstrations, and regression tests.

## Arnona

1. **Residential bill sanity check**  
   Apartment in Jerusalem, 78 sqm, Zone B, residential, two-month bill. Expected: formula uses sqm × annual rate × 2/12.

2. **Senior discount with area below cap**  
   80 sqm apartment, eligible senior discount, two-month period. Expected: discount applies to all 80 sqm for the period.

3. **Senior discount with area above cap**  
   130 sqm apartment, senior discount capped at 100 sqm. Expected: discount applies only to 100 sqm.

4. **New immigrant discount for partial year**  
   95 sqm apartment, 90% discount for 6 eligible months. Expected: discount months control period; warning to verify municipal rules.

5. **Low-income discount requiring committee**  
   Residential property, low-income discount. Expected: output flags document and committee dependency.

6. **Home office charged as full office**  
   72 sqm apartment, 10 sqm work room. Expected: scenario comparison shows all-residential, all-office, and split treatment.

7. **Wrong prior-tenant classification**  
   Retail phone store billed as restaurant. Expected: evidence checklist includes lease, photos, business license, handover date.

8. **Warehouse behind store**  
   30 sqm retail + 70 sqm storage. Expected: request split only if physically distinct and local order allows it.

9. **Vacant apartment**  
   Empty apartment after tenant left. Expected: check local vacancy exemption, photos, utility readings, prior use of exemption.

10. **Area exceeds Tabu**  
    Bill shows 105 sqm, Tabu shows 87 sqm. Expected: do not assume error; inspect measurement clause and common-area inclusion.

11. **Duplicate asset account**  
    Same office charged under two property numbers. Expected: request ledger, maps, cancellation of duplicate account.

12. **Holder changed late**  
    Tenant moved out on 31/05/2026; municipality bills through 31/12/2026. Expected: provide handover proof and request correction.

13. **Zone mismatch**  
    Street appears in Zone B table, bill uses Zone A. Expected: attach street table and request zone correction.

14. **Business sign charge**  
    Small illuminated sign charged for full year despite installation on 01/09/2026. Expected: verify bylaw and pro-rate if available.

## Purchase tax and sale taxes

15. **Single-home purchase**  
    Buyer owns no other apartment, price ₪1,900,000. Expected: likely low or zero tax under sample brackets, but current brackets required.

16. **Additional-home purchase**  
    Buyer keeps existing apartment, price ₪2,400,000. Expected: additional-home bracket path; replacement-home facts requested.

17. **Replacement home**  
    Buyer owns apartment and intends sale within permitted period. Expected: flag deadline and evidence for replacement treatment.

18. **Foreign resident buyer**  
    Buyer is not Israeli resident. Expected: current law and professional review required.

19. **Sale with potential land appreciation tax**  
    Seller bought many years ago and sells investment apartment. Expected: route to Mas Shevach, not Arnona.

20. **Gift transfer inside family**  
    Apartment transferred to child. Expected: special relief/exemption rules, lawyer review.

## Betterment levy

21. **Sale after plan improvement**  
    Plan added rights; committee claims uplift ₪300,000. Expected: rough levy ₪150,000 before exemptions and disputes.

22. **Permit triggers levy**  
    Owner requests building permit before sale. Expected: realization event may occur before sale.

23. **Partial ownership**  
    Owner has 50% of property. Expected: levy estimate uses ownership share.

24. **Exemption claim**  
    Homeowner claims residential exemption. Expected: verify strict statutory conditions and supporting documents.

## Mas Rechush and compensation

25. **Direct rocket damage**  
    Apartment windows broken during recognized event. Expected: photos, incident date, ownership/tenancy proof, claim route.

26. **Business equipment damage**  
    Shop inventory damaged by hostile act. Expected: itemized list, invoices, photos, claim number, insurer coordination.

27. **No damage, user asks about annual Mas Rechush**  
    Expected: explain historic tax versus current compensation framework; check if notice is actually Arnona or purchase tax.

## CLI and helper

28. **Unknown municipality**  
    Input municipality not in sample table. Expected: `UNKNOWN_MUNICIPALITY` with rate verification instruction.

29. **Invalid date**  
    Contract date `2026/03/15`. Expected: `DATE_FORMAT`; use `DD/MM/YYYY`.

30. **Negative area**  
    Area `-50`. Expected: `INVALID_AREA`.

31. **Async helper parity**  
    Async Arnona calculation equals sync calculation for same input.

32. **Appeal packet generation**  
    Wrong area and wrong classification issues selected. Expected: evidence list and objection outline.
