# Troubleshooting

## WhatsApp delivery failures

### Symptom: provider returns 400

Likely causes:

- Phone number is not E.164.
- Israeli local number still starts with `05`.
- Template name does not exist.
- Template language is not `he`.
- Body parameters do not match the approved template.

Fix:

1. Normalize `050-123-4567` to `+972501234567`.
2. Remove spaces, dashes, and leading zero after country code.
3. Confirm template name in Meta Business Manager.
4. Confirm the number belongs to the approved WhatsApp Business phone ID.
5. Retry one test contact before batch sending.

## SMS arrives as gibberish

Cause: provider sent Hebrew in GSM-7 or wrong encoding.

Fix:

- Set `encoding=unicode` or provider equivalent.
- Send a test to Partner, Cellcom, Pelephone, HOT Mobile, and Golan Telecom when scale matters.
- Keep messages short because Unicode SMS uses fewer characters per segment.

## SMS link breaks

Cause: long URL split by SMS client or carrier.

Fix:

- Use a short HTTPS link.
- Avoid punctuation immediately after the URL.
- Put the link before `להסרה` if the URL is the main action.
- Test on iOS and Android.

## Hebrew direction is wrong

Cause: message starts with URL, number, English brand, or punctuation.

Fix:

- Start with Hebrew text.
- Put URL on its own line.
- Avoid wrapping the whole message in English punctuation.
- Preview in the exact channel.

Bad:

```text
https://x.co/rev שלום דנה נשמח...
```

Good:

```text
שלום דנה,
אפשר להשאיר חוות דעת קצרה כאן?
https://x.co/rev
```

## Google review link opens the wrong business

Cause:

- Wrong Place ID.
- Duplicate Google listing.
- Old location profile.
- Branch-specific link missing.

Fix:

1. Search the exact business in Google Maps.
2. Confirm address and branch.
3. Retrieve the correct Place ID.
4. Open the official Google Maps URL `https://www.google.com/maps/search/?api=1&query={BUSINESS_NAME}&query_place_id=...` on mobile and desktop.
5. Store Place ID per branch, not per brand.

## Review link opens but review box does not appear

Cause:

- User is not signed in.
- Device-specific Google flow changed.
- Place ID points to a non-reviewable entity.
- Business profile is suspended or merged.

Fix:

- Test from an incognito browser and logged-in account.
- Add fallback text: `אם הקישור לא נפתח, אפשר לחפש את שם העסק ב-Google ולבחור "כתיבת ביקורת".`
- Check Google Business Profile status.

## Email lands in spam

Cause:

- Sender domain not authenticated.
- Too many links.
- HTML-heavy content.
- No text/plain version.
- Sending to stale list.

Fix:

- Configure SPF, DKIM, and DMARC.
- Send plain-text or simple multipart email.
- Use one main CTA link.
- Remove bounced addresses.
- Keep complaint and opt-out rates low.

## Customers complain about unsolicited messages

Cause:

- Consent basis is missing, unclear, or poorly documented.
- Campaign imported old contacts.
- Opt-outs not synchronized.
- Message reads like advertising rather than service follow-up.

Fix:

1. Pause campaign.
2. Export recipients and consent evidence.
3. Suppress complainants immediately.
4. Remove contacts without a valid basis.
5. Update copy and opt-out handling.
6. Document corrective action.

## Low response rate

Common causes:

- Message too long.
- Weak CTA.
- Bad timing: Friday, holiday week, evening.
- Platform requires login.
- Customer did not remember the transaction.
- No personal context.

Fix:

- Use 2-4 lines for WhatsApp.
- Send Sunday-Wednesday 09:30-11:30.
- Mention the business name, not private details.
- Use direct review link.
- Ask one action only.

## Too many negative public reviews after campaign

Cause:

- Public link sent to unresolved or unhappy customers.
- No private-first route for uncertain satisfaction.
- Campaign triggered after delays, refunds, or disputes.

Fix:

- Pause public-review requests.
- Add exclusion rules for complaints/refunds.
- Use private rating first.
- Escalate low scores to service recovery.

## Testimonials cannot be used on the website

Cause:

- No explicit approval.
- Approval did not specify wording.
- Attribution preference missing.
- Testimonial was edited too aggressively.

Fix:

- Send the exact text for approval.
- Capture `approved_at`, approver, display name, and location.
- Keep original customer wording.
- Re-approve after material edits.

## Directory URL changed

Cause: platform profile migrated, listing merged, or page slug changed.

Fix:

- Verify Google, Zap, Easy, Midrag, B144, and Facebook links monthly.
- Store last verified date.
- Use fallback first-party form when directory link becomes unstable.

## API credentials leak risk

Cause:

- `.env` committed.
- Delivery logs include tokens.
- Support screenshots show credentials.

Fix:

- Rotate keys immediately.
- Move secrets to environment variables or secret manager.
- Add `.env` to `.gitignore`.
- Redact logs.
- Restrict dashboard access.

## Rate limits

Cause:

- Too many sends in short window.
- Provider throughput tier is low.
- WhatsApp quality rating dropped.

Fix:

- Queue messages.
- Use exponential backoff.
- Cap sends per minute.
- Segment campaigns by time window.
- Monitor provider quality dashboards.

## Holiday timing issue

Cause: campaign scheduled during Rosh Hashanah, Yom Kippur, Sukkot, Pesach, Shavuot, Memorial Day, or Independence Day.

Fix:

- Pause non-urgent feedback campaigns.
- Resume after normal business activity.
- Use manual review for urgent service messages only.
