# Test Scenarios

Use these scenarios for manual QA, unit tests, integration tests, and regression testing.

## Core Scenarios

1. **Residential bill, due in 45 days**  
   Expected: status `upcoming`; all default reminders remain.

2. **Residential bill, due in 6 days**  
   Expected: status `due_soon`; only reminders from 7 days onward remain unless past events are included.

3. **Bill due today**  
   Expected: status `due_today`; due-today event generated.

4. **Bill overdue by 3 days**  
   Expected: status `overdue`; immediate overdue task generated when no future overdue follow-up is available.

5. **Bill overdue by 2 days with 7-day overdue follow-up enabled**  
   Expected: future follow-up event on due date + 7 days.

6. **Paid bill**  
   Expected: status `paid`; no reminders.

7. **Missing bill number**  
   Expected: validation error.

8. **Negative amount**  
   Expected: validation error.

9. **Zero amount**  
   Expected: validation error unless separate zero-balance workflow is implemented.

10. **Issue date after due date**  
    Expected: validation error.

11. **Period start after period end**  
    Expected: validation error.

12. **Short account reference**  
    Expected: warning, not automatic failure.

13. **Short bill number**  
    Expected: warning, not automatic failure.

14. **Invalid Israeli ID checksum**  
    Expected: warning, not automatic failure unless payment provider requires it.

15. **Hebrew output**  
    Expected: `₪` amounts and `DD/MM/YYYY` dates in user-facing text.

16. **English output**  
    Expected: `₪` amounts and ISO dates in JSON.

17. **Standing order note present**  
    Expected: payment instructions warn against duplicate manual payment when workflow marks direct debit.

18. **Payment URL missing**  
    Expected: instructions tell the user to use official municipality page or printed link.

19. **Payment URL malformed**  
    Expected: validation warning.

20. **Corrected bill replaces old bill**  
    Expected: older reminders cancelled after explicit replacement confirmation.

21. **Two properties under one taxpayer**  
    Expected: separate reminder plans by property and period.

22. **Tenant reimbursement workflow**  
    Expected: receipt request generated after payment.

23. **Small business branch workflow**  
    Expected: approval reminder before payment reminder.

24. **Overdue collection notice**  
    Expected: current balance check required; no stale-amount payment instruction.

25. **Discount pending**  
    Expected: status-check reminder before full payment.

26. **Partial payment recorded**  
    Expected: bill remains not fully paid unless settlement exists.

27. **Receipt missing after card authorization**  
    Expected: status remains pending.

28. **Date input as DD/MM/YYYY**  
    Expected: parsed successfully.

29. **Date input as invalid ambiguous short year**  
    Expected: validation error.

30. **ICS export**  
    Expected: valid VCALENDAR with one VEVENT per reminder.

31. **Async client plan generation**  
    Expected: async output matches sync output for the same bill.

32. **CLI plan JSON**  
    Expected: valid JSON with status, events, instructions, and warnings.

33. **CLI due-date series**  
    Expected: bimonthly dates preserve day where possible and clamp month end.

34. **Leap year start date 29-02-2024**  
    Expected: future dates clamp correctly when needed.

35. **Regional council profile**  
    Expected: generic instructions without guessed payment URL.

## Acceptance Criteria

- At least 20 automated tests pass.
- Hebrew strings use natural professional terms.
- No reminder is generated after a bill is marked paid.
- Overdue flows require current-balance verification.
- Payment instructions never rely on unofficial links.
- Receipt is required before closing the bill.
- Sensitive identifiers can be masked in surrounding systems.


26. **VAT is mentioned by business user**
   Input: business asks to add 18% VAT to an Arnona bill.
   Expected: system refuses to alter the Arnona amount and instructs using the municipal bill/current balance.

27. **Official payment page updated**
   Input: stored municipal payment URL differs from a newly verified official page.
   Expected: mark profile for review, update source URL, and regenerate instructions only after verification.
