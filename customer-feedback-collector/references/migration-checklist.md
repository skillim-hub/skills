# Migration Checklist

Use this checklist when replacing manual review collection, spreadsheet tracking, generic survey tools, or ad hoc WhatsApp follow-ups with a structured feedback collector.

## 1. Inventory current sources

- [ ] Export current customer contact list.
- [ ] Identify source of each contact: booking system, ecommerce platform, CRM, invoice system, manual WhatsApp.
- [ ] Mark contacts with consent evidence.
- [ ] Export existing opt-out/suppression lists.
- [ ] List active review destinations: Google, Facebook, Zap, Easy, Midrag, B144, website testimonials.
- [ ] Identify branch-specific profiles.
- [ ] Collect current message templates.

## 2. Clean data

- [ ] Normalize Israeli mobile numbers to `+972`.
- [ ] Remove duplicate phones and emails.
- [ ] Remove customers with open complaints, refunds, chargebacks, or unresolved disputes.
- [ ] Remove bounced emails.
- [ ] Suppress `הסר`, `STOP`, unsubscribe, and do-not-contact records.
- [ ] Separate consumers, business customers, suppliers, family, employees, and test contacts.
- [ ] Delete stale campaign exports beyond retention policy.

## 3. Map review destinations

| Existing destination | Migration action |
|---|---|
| Google short link | Replace with Place ID review URL where possible. |
| Facebook page | Verify `/reviews/` is available. |
| Zap profile | Store verified profile URL and last checked date. |
| Easy profile | Store verified profile URL and fallback. |
| Midrag profile | Confirm platform rules before inviting reviews. |
| B144 profile | Store verified profile URL and fallback. |
| Website quote | Add explicit approval workflow. |
| Generic form | Add private-first routing and testimonial approval fields. |

## 4. Replace templates

- [ ] Replace literal translated text with short Israeli Hebrew.
- [ ] Start messages with Hebrew, not a URL.
- [ ] Include opt-out text.
- [ ] Remove pressure for 5 stars.
- [ ] Remove incentives linked to positive ratings.
- [ ] Remove unnecessary personal or sensitive details.
- [ ] Create separate templates for WhatsApp, email, and SMS.
- [ ] Create private-recovery template for low ratings.

## 5. Implement routing

- [ ] Happy path routes to public review link.
- [ ] Unknown satisfaction routes to private rating first for sensitive services.
- [ ] Low rating routes to service recovery.
- [ ] Open complaint suppresses public review request.
- [ ] Refund/chargeback suppresses public review request.
- [ ] Testimonial requests require explicit approval before publication.

## 6. Configure timing

- [ ] Set default send window to Sunday-Thursday 09:30-18:30.
- [ ] Block Friday after 13:00.
- [ ] Block Shabbat.
- [ ] Block configured holidays and memorial days.
- [ ] Send post-appointment requests 1-3 hours after completion.
- [ ] Send ecommerce requests 24-48 hours after delivery.
- [ ] Send at most one reminder unless explicit consent supports a different cadence.

## 7. Configure APIs and secrets

- [ ] Store API keys in environment variables or a secret manager.
- [ ] Verify WhatsApp templates and language code `he`.
- [ ] Verify SMS sender ID.
- [ ] Authenticate email sender domain with SPF, DKIM, and DMARC.
- [ ] Set provider rate limits.
- [ ] Create dry-run mode.
- [ ] Log provider message IDs without storing tokens.

## 8. Compliance and governance

- [ ] Document lawful basis for each send category.
- [ ] Define data retention period.
- [ ] Restrict access to campaign files.
- [ ] Add deletion and correction handling.
- [ ] Add opt-out handling across all channels.
- [ ] Check current Israeli Privacy Protection Authority guidance.
- [ ] Check current Section 30A requirements for commercial messages.
- [ ] Check platform-specific review policies.
- [ ] Prepare negative-review response policy.

## 9. Test before launch

- [ ] Run pytest suite.
- [ ] Run CLI sample message.
- [ ] Send internal WhatsApp test.
- [ ] Send internal SMS test.
- [ ] Send internal email test.
- [ ] Test review links on iOS, Android, and desktop.
- [ ] Test Hebrew RTL rendering.
- [ ] Test suppression.
- [ ] Test low-rating private route.
- [ ] Test bounced/failed provider responses.
- [ ] Review logs for sensitive data leakage.

## 10. Launch gradually

- [ ] Start with 10-20 recent customers.
- [ ] Monitor opt-outs and complaints.
- [ ] Monitor delivery failures.
- [ ] Check public reviews for quality and unexpected issues.
- [ ] Adjust copy and timing.
- [ ] Expand only after clean results.

## 11. Retire old workflow

- [ ] Disable old automations.
- [ ] Archive old templates.
- [ ] Remove duplicate scheduled campaigns.
- [ ] Merge suppression lists.
- [ ] Document new owner and maintenance schedule.
- [ ] Set monthly link verification.
