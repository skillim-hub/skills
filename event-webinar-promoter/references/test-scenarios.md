# Test Scenarios

Use these scenarios for manual QA, model evaluation, CLI checks, and regression testing. Each scenario includes inputs and expected behavior.

## 1. Free Hebrew webinar for freelancers

Input: webinar, Hebrew, 24/06/2026, 20:00, free, freelancers.

Expected:

- Use `Asia/Jerusalem`.
- Recommend 14-day runway.
- Create Hebrew landing copy.
- Include email/social/partner channels.
- Include no paid-event cancellation warning unless terms are requested.

## 2. Paid workshop in Haifa

Input: workshop, חיפה, 15/07/2026, 10:00, ₪290, 18 seats.

Expected:

- Recommend 30-day runway.
- Flag VAT and cancellation wording.
- Include venue/accessibility checklist.
- Use “עד 18 משתתפים” only because capacity exists.

## 3. Saturday B2B webinar

Input: B2B webinar on Saturday at 10:00.

Expected:

- Flag Saturday risk.
- Recommend Sunday–Thursday at 10:00 or 14:00.
- Do not silently accept the timing.

## 4. Friday afternoon consumer event

Input: local consumer event Friday at 15:00.

Expected:

- Warn about Friday afternoon response.
- Suggest Friday morning or Sunday evening.

## 5. Unknown consent for WhatsApp blast

Input: “send WhatsApp blast to all contacts”, consent unknown.

Expected:

- Do not create bulk direct promotion.
- Suggest organic posts, partner posts, and consent-building form.

## 6. Partner newsletter

Input: partner wants to invite its audience.

Expected:

- Partner sends to own opted-in list.
- Use partner UTM link.
- Do not exchange raw lists by default.

## 7. Paid event without refund terms

Input: paid webinar with no cancellation policy.

Expected:

- Flag missing cancellation/refund terms.
- Add placeholder and recommend review before publishing.

## 8. Event with unclear recording

Input: webinar, recording unknown.

Expected:

- Do not promise replay.
- Use conditional wording or omit recording.

## 9. Low registrations 72h before

Input: 8 registrations out of 50 target, event in 3 days.

Expected:

- Diagnose title, CTA, channel, page.
- Produce rescue post.
- Suggest partner reposts and one opted-in reminder.

## 10. Sold-out workshop

Input: capacity 20, sold out.

Expected:

- Create waitlist copy.
- Remove “register now”.
- Avoid fake scarcity.

## 11. International audience

Input: Israeli host, attendees in New York and London.

Expected:

- Use Israel as source timezone.
- Display additional timezones.
- Keep Israel date/time clear.

## 12. Accessibility missing

Input: offline event, venue but no access notes.

Expected:

- Add accessibility contact.
- Ask for entrance, elevator, accessible parking/restrooms where available.
- Avoid claiming accessible venue without verification.

## 13. Hebrew gender-neutral copy

Input: mixed-gender audience.

Expected:

- Use neutral plural or inclusive phrasing.
- Avoid masculine-only singular calls to action.

## 14. Local retail launch

Input: store launch in Rishon LeZion.

Expected:

- Recommend Google Business Profile, local groups, Instagram, QR in store.
- Include address, parking, arrival time, children policy if relevant.

## 15. B2B lunchtime micro-session

Input: 30-minute session for operations managers.

Expected:

- Recommend 12:00 or 10:00.
- Keep agenda tight.
- Use LinkedIn and partner newsletter.

## 16. Course preview

Input: free preview for paid course.

Expected:

- Clarify what is taught versus what is sold.
- Include transparent next step.
- Avoid bait-and-switch.

## 17. Medical topic

Input: health webinar with treatment claims.

Expected:

- Flag sensitive claims.
- Avoid guaranteed outcomes.
- Recommend professional/legal review.

## 18. Financial topic

Input: investment webinar.

Expected:

- Avoid guaranteed returns.
- Add disclaimer placeholder.
- Recommend qualified review and careful compliance.

## 19. Children or minors

Input: event for teens.

Expected:

- Flag parental consent/privacy sensitivity.
- Minimize data collection.
- Use clear guardian communication.

## 20. Existing English-speaking audience in Israel

Input: English-speaking olim entrepreneurs.

Expected:

- Permit English or bilingual copy.
- Keep Israel timezone and ₪.
- Include Hebrew fallback if relevant.

## 21. No registration URL yet

Input: event details but no URL.

Expected:

- Use `[registration_url]` placeholder.
- Produce copy that can be pasted later.
- Add registration-page checklist.

## 22. Imported mailing list

Input: contacts purchased from vendor.

Expected:

- Reject direct marketing use.
- Suggest ads, organic posts, partner-owned channels, and opt-in acquisition.

## 23. Hybrid event

Input: venue plus Zoom stream.

Expected:

- Include both location and online link logistics.
- Clarify which parts are recorded.
- Add accessibility details for both modes.

## 24. Replay expiration claim

Input: “replay available for 48 hours”.

Expected:

- Treat as acceptable only if technically enforced.
- Use real deadline wording.
- Avoid fake urgency.

## 25. Capacity not known

Input: “limited seats” but no capacity.

Expected:

- Remove scarcity claim.
- Ask for capacity or use neutral CTA.

## 26. Event tomorrow

Input: webinar tomorrow at 20:00.

Expected:

- Use compressed promotion plan.
- Prioritize warm opted-in audience and organic posts.
- Avoid overbuilding a long funnel.

## 27. High-ticket consultation event

Input: free webinar selling expensive consulting package.

Expected:

- Use qualified-lead messaging.
- Avoid manipulative urgency.
- Segment follow-up by engagement.

## 28. Municipality/community event

Input: public community session.

Expected:

- Use accessible language.
- Include venue access, public transport, and community notice channels.
- Avoid commercial opt-in assumptions.

## 29. Hebrew typo-heavy input

Input: rough Hebrew with spelling mistakes.

Expected:

- Normalize into professional Hebrew.
- Preserve meaning.
- Do not shame the user.

## 30. Postponement

Input: speaker sick, event postponed.

Expected:

- Produce clear postponement message.
- Include options for paid participants.
- Avoid excessive excuses.
