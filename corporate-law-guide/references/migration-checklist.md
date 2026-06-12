# Migration and Upgrade Checklist

## Package migration

- [ ] Remove branding, visual assets, contributor names, and distribution callouts.
- [ ] Remove creator/contributor field from metadata.
- [ ] Confirm the MIT license holder line uses The Authors.
- [ ] Replace promotional voice with imperative neutral voice.
- [ ] Add English and Hebrew guides of comparable depth.
- [ ] Add decision trees, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- [ ] Add references, workflow guide, troubleshooting guide, test scenarios, migration checklist, client, CLI, tests, examples, README, CHANGELOG, LICENSE, pyproject, and dev requirements.
- [ ] Use ₪ and DD/MM/YYYY localization.

## Corporate records migration

- [ ] Save certificate of incorporation.
- [ ] Save articles and amendments.
- [ ] Save shareholder agreement and deeds of adherence.
- [ ] Save board and shareholder resolutions.
- [ ] Save shareholders register.
- [ ] Save directors register.
- [ ] Save allotment and transfer documents.
- [ ] Save option plan and grants.
- [ ] Save IP assignments.
- [ ] Save material contracts.
- [ ] Save annual report confirmations and fee receipts.
- [ ] Save tax-registration confirmations.
- [ ] Save bank signing-rights resolution.
- [ ] Save insurance policies.
- [ ] Save charge documents.
- [ ] Save consumer, privacy, employment, and contractor documents.

## Data migration

- [ ] Store company number as string.
- [ ] Normalize dates to DD/MM/YYYY for human output.
- [ ] Normalize Hebrew company name.
- [ ] Separate issued shares from options and promises.
- [ ] Track share class and source document.
- [ ] Reconcile cap table totals.
- [ ] Link every share event to approval and register entry.

## CLI checks

```bash
python scripts/corporate-law-guide-cli.py classify --owners 2 --liability-risk high --fundraising yes --activity "software platform"
python scripts/corporate-law-guide-cli.py annual-report --company-number 516000000 --year 2026
python scripts/corporate-law-guide-cli.py shareholder-scan --founders 2 --equal-holdings yes --investor-round yes
python scripts/corporate-law-guide-cli.py validate-company-number 516000000
python scripts/corporate-law-guide-cli.py checklist incorporation --owners 2 --activity "consumer ecommerce"
```

## Acceptance

- [ ] No branding or visual assets.
- [ ] Metadata has no creator/contributor field.
- [ ] Tests pass.
- [ ] README file index matches actual files.
- [ ] Examples run offline.
- [ ] Hebrew reads naturally to an Israeli professional.
- [ ] References distinguish law/regulation from live API claims.
