# Test scenarios

Use these scenarios for manual evaluation, automated examples, and regression testing. Each scenario includes expected drafting behavior and key risk flags.

## Scenario list

### 1. Graphic design freelancer for cafe chain
- Provider: individual עוסק מורשה.
- Customer: company.
- Fee: ₪12,000 plus VAT.
- Deliverables: visual identity refresh, menus, social templates.
- Expected: Hebrew service agreement, IP assignment after full payment, portfolio carve-out, VAT plus wording.
- Flags: scope, IP, VAT.

### 2. Consumer refrigerator repair
- Provider: repair company.
- Customer: individual consumer.
- Fee: ₪650 including VAT.
- Expected: short consumer service terms, service date, parts/labor warranty, cancellation note.
- Flags: consumer cancellation, mandatory rights.

### 3. Software developer builds website
- Provider: freelancer.
- Customer: small business.
- Fee: ₪28,000 plus VAT in milestones.
- Expected: statement of work, acceptance tests, change requests, IP transfer after full payment, open-source disclosure.
- Flags: IP, OSS, scope creep.

### 4. Monthly social media retainer
- Provider: marketing consultant.
- Customer: restaurant.
- Fee: ₪4,500 plus VAT per month.
- Expected: recurring services, monthly deliverables, content approval, 30-day termination.
- Flags: vague scope, consumer not applicable.

### 5. Photographer for product catalog
- Provider: photographer.
- Customer: e-commerce store.
- Fee: ₪9,000 plus VAT.
- Expected: usage license or assignment, model/property releases, editing rounds, portfolio right.
- Flags: copyright, third-party rights.

### 6. Mutual NDA for joint tender
- Parties: two companies.
- Purpose: evaluate joint tender.
- Term: 2-year confidentiality.
- Expected: mutual NDA, permitted recipients, no license, return/destruction.
- Flags: avoid non-compete.

### 7. One-way NDA for investor deck
- Discloser: startup.
- Recipient: consultant.
- Expected: one-way confidentiality, purpose-limited use, no obligation to transact.
- Flags: personal data if deck contains customer data.

### 8. Supplier sells equipment to business
- Seller: equipment store.
- Buyer: company.
- Goods: 10 printers.
- Expected: sale agreement, delivery, inspection, warranty, risk/title.
- Flags: VAT, delivery acceptance.

### 9. Recurring office supplies framework
- Seller: supplier.
- Buyer: small business.
- Expected: master supply terms plus purchase orders, price changes with notice.
- Flags: unilateral changes.

### 10. Home renovation for consumer
- Contractor: renovation business.
- Customer: homeowner.
- Expected: detailed scope, permits, staged payments, changes, safety, cancellation review.
- Flags: consumer, permits, high value.

### 11. Yoga instructor studio rental
- Studio owner allows instructor to use room.
- Expected: license/use agreement, schedule, fees, insurance, no tenancy unless intended.
- Flags: real estate/lease review if possession resembles lease.

### 12. App subscription terms for consumers
- Operator: Israeli app.
- Users: consumers.
- Expected: terms of use, subscriptions, cancellation, privacy link, changes with notice.
- Flags: consumer, privacy, standard terms.

### 13. Consultant processes customer list
- Provider receives names, phones, purchase history.
- Expected: service agreement plus privacy/data security schedule.
- Flags: personal data.

### 14. Health coach collects sensitive information
- Provider: health coach.
- Customer: consumer.
- Expected: professional review note, privacy sensitivity, limited liability carefully drafted.
- Flags: health data, regulated/consumer.

### 15. Freelancer works full-time for one client
- Facts: fixed hours, manager approval, customer equipment, exclusivity.
- Expected: worker-classification warning; do not disguise employment.
- Flags: high.

### 16. Cross-border US customer
- Israeli developer sells services to US company.
- Expected: governing law choice, tax/VAT review, payment currency and exchange source.
- Flags: tax, jurisdiction, service of process.

### 17. Hebrew and English bilingual contract
- Parties request both languages.
- Expected: language precedence clause, consistent defined terms.
- Flags: conflicting versions.

### 18. Consumer cancellation says no refunds
- Existing clause: all payments non-refundable.
- Expected: replace with statutory-rights savings and fair cancellation.
- Flags: high consumer risk.

### 19. Unlimited liability requested
- Customer requires unlimited liability for all damages.
- Expected: propose direct-damages cap, carve-outs for fraud/willful misconduct/IP misuse where appropriate.
- Flags: liability.

### 20. Personal guarantee for business debt
- Owner guarantees company payment.
- Expected: separate guarantee review, clear guarantor identity, legal review.
- Flags: high.

### 21. Open-source software delivery
- Developer uses open-source libraries.
- Expected: OSS disclosure, compliance, excluded materials, warranty limited.
- Flags: IP/license.

### 22. Event vendor contract
- Provider supplies sound system for event.
- Expected: date/time/location, cancellation tiers, force majeure, equipment damage, insurance.
- Flags: safety, cancellation.

### 23. Catering for private consumer event
- Provider: caterer.
- Customer: individual.
- Expected: menu, guest count, allergens, payment schedule, cancellation, consumer note.
- Flags: consumer, food licensing.

### 24. Debt settlement between two businesses
- Debtor pays installments.
- Expected: settlement agreement, no admission if intended, default, releases after payment.
- Flags: tax/accounting, guarantees.

### 25. License of training materials
- Trainer licenses slides to company.
- Expected: non-exclusive license, no resale, attribution if required, confidentiality.
- Flags: copyright.

### 26. Website development with hosting
- Developer hosts customer website.
- Expected: SLA-lite, backups, access, domain ownership, termination migration.
- Flags: data, IP, operational exit.

### 27. Consumer online course
- Business sells course to individuals.
- Expected: consumer terms, cancellation/refund review, access period, IP restrictions.
- Flags: distance sale, standard terms.

### 28. Cleaning services for office
- Provider: cleaning company.
- Customer: small office.
- Expected: service schedule, materials, access, insurance, replacement staff, termination.
- Flags: labor subcontractor compliance.

### 29. Agency/referral commission
- Referrer introduces customers.
- Expected: agency/referral agreement, commission trigger, payment timing, anti-bribery.
- Flags: authority, indefinite commission tail.

### 30. Custom furniture order
- Carpenter builds table for consumer.
- Expected: specs, measurements, deposit, delivery, installation, cancellation review.
- Flags: consumer, custom goods exception review.

## Automated acceptance criteria

- At least 20 test scenarios exist.
- Hebrew drafts use ₪ and DD/MM/YYYY examples.
- Service agreements mention VAT treatment.
- Consumer service drafts include cancellation review.
- IP-producing services include assignment/license choice.
- Privacy schedule appears when personal data is processed.
- Worker-classification risk is high when employment-like facts appear.
- CLI can generate a sample draft.
- Tests cover sync and async helper flows.


### 31. Business contract after 2026 interpretation amendment

- Parties: two represented companies.
- Facts: signed after 07/01/2026 with schedules and technical appendices.
- Expected: include interpretation, schedule-priority, and entire-agreement checks.
- Flags: section 25 review, inconsistency between body and appendix.

### 32. VAT rate verification before signing

- Parties: Israeli service provider and business customer.
- Fee: ₪18,000 plus VAT.
- Expected: helper calculation uses 18% as of 02/06/2026, contract clause says "VAT at the lawful rate".
- Flags: accountant confirmation if signing date is later.
