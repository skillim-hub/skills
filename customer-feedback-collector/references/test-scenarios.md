# Test Scenarios

Use these scenarios for QA, acceptance testing, and regression tests.

## Core message generation

1. **Google WhatsApp happy path**  
   Input: Hebrew business name, customer name, `050-123-4567`, Google Place ID.  
   Expected: phone normalizes to `+972501234567`, body contains Hebrew, Google review URL, and opt-out text.

2. **Facebook email happy path**  
   Input: Facebook page URL and email contact.  
   Expected: subject exists, body contains page `/reviews/` URL and testimonial alternative.

3. **Zap SMS happy path**  
   Input: Zap profile URL and Israeli mobile.  
   Expected: compact SMS, Hebrew first, opt-out text, URL present.

4. **Easy destination**  
   Input: Easy profile URL.  
   Expected: generated link equals configured Easy URL.

5. **Custom first-party form**  
   Input: custom review URL.  
   Expected: body uses custom link and validation passes.

## Phone and contact handling

6. **Local mobile normalization**  
   Input: `050-123-4567`.  
   Expected: `+972501234567`.

7. **Already normalized phone**  
   Input: `+972501234567`.  
   Expected: unchanged.

8. **Invalid landline for SMS**  
   Input: `03-1234567` for SMS-only campaign.  
   Expected: warning or rejection depending configuration.

9. **Missing phone for WhatsApp**  
   Input: contact has email only.  
   Expected: contact skipped for WhatsApp plan.

10. **Missing email for email channel**  
    Input: contact has phone only.  
    Expected: contact skipped for email plan.

## Consent and suppression

11. **Consent false**  
    Input: contact consent is false.  
    Expected: `ConsentRequired` issue and no send.

12. **Suppression list match**  
    Input: customer appears in suppression list.  
    Expected: contact skipped.

13. **Customer replied הסר**  
    Input: inbound text `הסר`.  
    Expected: opt-out detected.

14. **Customer replied stop**  
    Input: inbound text `STOP`.  
    Expected: opt-out detected.

## Routing and satisfaction

15. **Known low rating**  
    Input: rating 2/5 and private feedback URL.  
    Expected: private recovery link, no public review URL.

16. **Rating 5**  
    Input: rating 5/5.  
    Expected: public review prompt.

17. **Rating 4**  
    Input: rating 4/5.  
    Expected: private improvement prompt or neutral route.

18. **Open complaint tag**  
    Input: contact tag `open_complaint`.  
    Expected: no public review send.

## Timing

19. **Friday afternoon**  
    Input: Friday 14:00 Asia/Jerusalem.  
    Expected: quiet-time block and next safe time Sunday morning.

20. **Saturday morning**  
    Input: Saturday 10:00.  
    Expected: quiet-time block.

21. **Sunday morning**  
    Input: Sunday 10:00.  
    Expected: safe send.

22. **Late night**  
    Input: Wednesday 22:00.  
    Expected: next safe time Thursday 09:30.

## Content quality

23. **No Hebrew characters**  
    Input: English-only body.  
    Expected: Hebrew validation warning.

24. **No opt-out**  
    Input: message without `הסר` or equivalent.  
    Expected: unsubscribe warning.

25. **Incentive wording**  
    Input: `קבלו 10 ₪ הנחה על דירוג 5 כוכבים`.  
    Expected: incentive/manipulation warning.

26. **URL-first message**  
    Input: body begins with `https://`.  
    Expected: RTL warning.

27. **Sensitive-service detail**  
    Input: body includes diagnosis or therapy details.  
    Expected: privacy warning in review prompt QA.

## API and CLI

28. **Dry-run send**  
    Input: delivery plan with `dry_run=true`.  
    Expected: no network call, status `dry_run`.

29. **Mock provider success**  
    Input: fake transport returns message ID.  
    Expected: result status `queued`.

30. **Mock provider failure**  
    Input: fake transport returns 429.  
    Expected: retryable failure classification.

31. **CLI sample-message**  
    Input: `sample-message --channel whatsapp`.  
    Expected: prints Hebrew message.

32. **CLI plan CSV**  
    Input: CSV with 3 contacts, one missing phone.  
    Expected: two planned messages and one skipped issue.

33. **JSON export**  
    Input: plan output path.  
    Expected: valid UTF-8 JSON with Hebrew preserved.

34. **Example scripts**  
    Input: run each file under `scripts/examples`.  
    Expected: each exits 0 and prints a plan or message.

## Production acceptance

35. **Branch-specific Google profile**  
    Input: two branches with separate Place IDs.  
    Expected: each contact receives correct branch link.

36. **Duplicate customer in campaign**  
    Input: same phone appears twice.  
    Expected: deduplicate or warn.

37. **Old transaction**  
    Input: last interaction older than 180 days.  
    Expected: relationship/opt-in review rather than transactional follow-up.

38. **Bounced email**  
    Input: email previously bounced.  
    Expected: contact suppressed.

39. **Holiday pause**  
    Input: campaign date falls in configured holiday list.  
    Expected: no non-urgent sends.

40. **Testimonial publication**  
    Input: approved text, display name preference, approval date 03/06/2026.  
    Expected: approval record complete and publishable.
