# Migration Checklist

Use this checklist when moving from manual lead assignment, spreadsheet tracking, email forwarding, or simple CRM round-robin to rule-based routing.

## Phase 1: Inventory

- [ ] List every lead source: website form, WhatsApp, phone notes, email, Meta lead ads, partner portals, and CSV imports.
- [ ] List every recipient: salespeople, support agents, installers, billing staff, regional managers, and call centers.
- [ ] Map every product and service category used today.
- [ ] Map every region and branch responsibility.
- [ ] List languages supported by each recipient.
- [ ] Capture current SLA expectations.
- [ ] Identify sensitive lead categories requiring restricted access.
- [ ] Identify marketing consent fields and campaign enrollment rules.

## Phase 2: Data cleanup

- [ ] Standardize phone fields.
- [ ] Standardize email fields.
- [ ] Export a sample of at least 100 historical leads, or all leads if volume is lower.
- [ ] Preserve original message text in UTF-8.
- [ ] Add missing city or product columns where possible.
- [ ] Split service request fields from marketing consent.
- [ ] Remove unnecessary personal data from routing inputs.
- [ ] Create allowed values for language, region, product, channel, priority, and status.

## Phase 3: Rule design

- [ ] Define default fallback route.
- [ ] Define data-quality route for missing contact details.
- [ ] Define language-specific queues for Hebrew, English, Russian, and Arabic.
- [ ] Define region-specific owners.
- [ ] Define product-specific owners.
- [ ] Define urgent path and emergency wording.
- [ ] Define billing path.
- [ ] Define enterprise path.
- [ ] Define outside-hours path.
- [ ] Define manual override process.
- [ ] Define owner and backup for every route.

## Phase 4: Backtesting

- [ ] Run historical leads through the router.
- [ ] Compare automatic routes to actual successful owners.
- [ ] Mark false positives and false negatives.
- [ ] Count unknown region, unknown product, and low-confidence results.
- [ ] Add missing aliases.
- [ ] Adjust rule ordering.
- [ ] Document expected exceptions.
- [ ] Re-run until acceptance criteria are met.

Suggested acceptance criteria:

| Metric | Target |
|---|---:|
| Valid leads routed to a specific queue | 90%+ |
| Missing-contact leads caught | 99%+ |
| Low-confidence leads | Under 10% after cleanup |
| Critical support misroutes | 0 known cases in test set |
| Consent warnings on no-consent leads | 100% |
| Manual override rate after launch | Under 15% in first month |

## Phase 5: Pilot

- [ ] Run router in shadow mode for 3-7 business days.
- [ ] Show suggested route without changing actual owner.
- [ ] Collect staff feedback.
- [ ] Review missed SLA and manual disagreement.
- [ ] Confirm CRM fields display correctly in Hebrew, Arabic, Russian, and English.
- [ ] Confirm mobile and desktop CRM views.
- [ ] Confirm CSV export/import keeps UTF-8.
- [ ] Confirm no campaigns use leads without consent.

## Phase 6: Production rollout

- [ ] Freeze initial rule version.
- [ ] Back up old routing rules and spreadsheet formulas.
- [ ] Enable automatic route assignment for low-risk sources first.
- [ ] Keep manual override visible.
- [ ] Monitor every route for the first day.
- [ ] Review warnings daily during the first week.
- [ ] Add alerts for unrouted leads and missed urgent SLA.
- [ ] Train staff on route reasons and override reasons.
- [ ] Document who can edit rules.

## Phase 7: Governance

- [ ] Review rule performance weekly for the first month.
- [ ] Review alias gaps monthly.
- [ ] Review permissions quarterly.
- [ ] Review retention and privacy settings quarterly.
- [ ] Review holiday and working-hours settings before every holiday period.
- [ ] Keep a changelog for rule and package versions.
- [ ] Run `pytest` before deploying rule updates.
- [ ] Run all scenarios in `references/test-scenarios.md` before major changes.

## Rollback plan

- [ ] Keep the previous assignment method available.
- [ ] Keep a list of active queues and owners.
- [ ] Store incoming leads even if routing fails.
- [ ] Allow manual assignment from CRM.
- [ ] Disable campaign triggers independently from service routing.
- [ ] Document the exact switch needed to stop automatic assignment.
- [ ] Preserve audit logs for routes already made.

## Migration risks

| Risk | Mitigation |
|---|---|
| Staff distrust automatic routing | Show reason codes and allow overrides |
| Too many fallback routes | Improve form fields and aliases |
| Consent mistakes | Keep marketing consent as explicit field |
| Wrong region from phone | Treat area code as weak evidence |
| Broken Unicode | Test real Hebrew, Arabic, and Russian text |
| Holiday SLA misses | Add business calendar handling |
| One person becomes bottleneck | Route to queues, not individuals |
| Rule drift | Use versioning and changelog |
