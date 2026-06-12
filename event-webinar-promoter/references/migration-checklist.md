# Migration Checklist

Use this checklist when upgrading an older event/webinar promotion package, replacing manual templates, or moving from ad-hoc campaign planning to this structured skill.

## Migration goals

- Remove branding, visual identity assets, creator metadata, and distribution callouts.
- Use neutral imperative voice.
- Standardize Israel timezone handling.
- Add Hebrew-first copy patterns.
- Add compliance, accessibility, and privacy checks.
- Add testable CLI/client behavior.
- Make event planning repeatable.

## Files to add or replace

| File | Required action |
|---|---|
| `SKILL.md` | Replace with comprehensive English guide |
| `SKILL_HE.md` | Replace with natural Hebrew guide |
| `metadata.json` | Bump version, remove creator field, expand tags |
| `references/api-reference.md` | Add Israeli regulation and schema reference |
| `references/workflow-guide.md` | Add end-to-end workflows |
| `references/troubleshooting.md` | Add operational troubleshooting |
| `references/test-scenarios.md` | Add 20+ concrete scenarios |
| `references/migration-checklist.md` | Add this checklist |
| `scripts/event_webinar_promoter_client.py` | Add typed sync/async helper |
| `scripts/event-webinar-promoter-cli.py` | Add Click CLI |
| `scripts/test_event_webinar_promoter_client.py` | Add pytest suite |
| `scripts/examples/` | Add runnable examples |
| `README.md` | Add install, quick start, file index |
| `CHANGELOG.md` | Add Keep a Changelog format |
| `LICENSE` | Add MIT license with “The Authors” |
| `pyproject.toml` | Add project/test configuration |
| `requirements-dev.txt` | Add development dependencies |

## Branding removal

Search and remove:

- Organization names.
- Named creator references.
- Visual status markers.
- Visual identity files.
- Header artwork.
- “Distributed by” text.
- Promotional package claims.
- Image references used as visual identity assets.
- External identity metadata not needed for operation.

Recommended grep:

```bash
grep -RniE "creator|visual|distributed|sponsor|maintainer" .
```

Expected outcome:

- `metadata.json` has no creator field.
- `LICENSE` keeps the required MIT holder line.
- No visual status marker markdown exists.
- No visual identity images are referenced.

## Hebrew localization migration

Replace:

| Old pattern | New pattern |
|---|---|
| `YYYY-MM-DD` or `DD-MM-YYYY` in user-facing Hebrew | `DD/MM/YYYY` |
| `₪` | `₪` |
| Literal English marketing terms | Natural Hebrew professional phrasing |
| Masculine-only CTA by default | Neutral plural or inclusive wording |
| “חינם” everywhere | “ללא עלות” when professional tone fits |
| “וובינר מדהים/עוצמתי” | “וובינר מעשי/ממוקד” |

## Timezone migration

Required:

- Store event datetime with `Asia/Jerusalem`.
- Use timezone-aware datetimes in code.
- Avoid naive datetime output in schedules.
- Recalculate reminder times from event start.
- Keep Israel time visible in copy.

Test:

```bash
python -m event_webinar_promoter.cli sample > /tmp/event.json
python -m event_webinar_promoter.cli plan /tmp/event.json
```

Expected:

- `timezone` equals `Asia/Jerusalem`.
- `starts_at` includes an offset.
- Reminder times are before event start.

## Compliance migration

Add checks for:

- Consent status for direct marketing.
- Unsubscribe route for direct channels.
- Advertiser identity.
- Paid event terms.
- VAT wording.
- Privacy note.
- Accessibility contact.
- Capacity/scarcity truthfulness.
- Recording/replay accuracy.
- Partner list ownership.

## CLI migration

Commands to support:

- `sample`
- `validate`
- `plan`
- `copy`
- `checklist`
- `utm`

Expected behavior:

- Accept JSON input files.
- Emit JSON for machine-readable commands.
- Emit readable checklist text.
- Return non-zero exit code for invalid input.
- Avoid network calls.
- Work without external credentials.

## Test migration

Minimum test coverage:

- Date parsing.
- Time parsing.
- Timezone.
- Reminder generation.
- Saturday risk.
- Friday afternoon risk.
- Paid event warnings.
- Consent warnings.
- Channel recommendations.
- UTM generation.
- Hebrew copy generation.
- Checklist generation.
- JSON roundtrip.
- Async client wrapper.
- CLI helper importability.
- Edge cases for missing fields.

Run:

```bash
pytest -q
```

## Release readiness

- [ ] No creator metadata.
- [ ] No visual identity assets.
- [ ] Neutral voice.
- [ ] English guide complete.
- [ ] Hebrew guide complete and natural.
- [ ] References complete.
- [ ] Workflows complete.
- [ ] Troubleshooting complete.
- [ ] 20+ scenarios present.
- [ ] Client and CLI runnable.
- [ ] 5+ examples runnable.
- [ ] 20+ pytest tests passing.
- [ ] Zip contains only intended files.
- [ ] README explains installation and use.
- [ ] Changelog documents changes.
- [ ] License is MIT with “The Authors”.
