# Migration Checklist

Use this checklist to migrate from the previous small social-content package to the enhanced neutral package.

## Migration goals

- Remove branding fields, attribution fields, decorative visual assets, and distribution callouts.
- Rename the skill to `social-media-manager`.
- Replace a basic posting scheduler with a typed client, CLI, examples, and tests.
- Add English and Hebrew documentation with equal operational depth.
- Add references for APIs, regulations, workflows, troubleshooting, tests, and migration.
- Add packaging metadata and development dependencies.
- Keep the skill focused on organic scheduling and compliance-aware planning.

## File mapping

| Previous file | New file | Action |
|---|---|---|
| `SKILL.md` | `SKILL.md` | Replace with expanded English guide |
| `SKILL_HE.md` | `SKILL_HE.md` | Replace with expanded Hebrew guide |
| `metadata.json` | `metadata.json` | Bump version, remove author, expand tags |
| `references/israeli-social-platforms.md` | `references/api-reference.md` and `references/workflow-guide.md` | Split into reference and workflows |
| `scripts/posting_scheduler.py` | `scripts/social_media_manager_client.py` | Replace with typed scheduling client |
| None | `scripts/social-media-manager-cli.py` | Add CLI |
| None | `scripts/test_social-media-manager_client.py` | Add pytest suite |
| None | `scripts/examples/` | Add runnable examples |
| None | `README.md` | Add package index and quick start |
| None | `CHANGELOG.md` | Add Keep-a-Changelog file |
| None | `LICENSE` | Add MIT license |
| None | `pyproject.toml` | Add Python project metadata |
| None | `requirements-dev.txt` | Add development dependencies |

## Pre-migration checks

- Confirm current package location.
- Back up existing package.
- Identify downstream references to old file paths.
- Identify any automation that imports `scripts/posting_scheduler.py`.
- Identify metadata consumers that expect an `author` field.
- Confirm no decorative visual files are required.
- Confirm no public distribution language remains in templates.
- Confirm Hebrew docs use local terminology and `₪`.

## Metadata migration

Apply the following changes:

- Set `name` to `social-media-manager`.
- Set `version` to `2.0.0` or later.
- Remove `author`.
- Remove `supported_agents`.
- Expand tags in English and Hebrew.
- Keep category neutral, such as `marketing-operations`.
- Keep description focused on scheduling and compliance-aware social planning.
- Avoid references to organizations, repositories, sponsors, decorative visual assets, or distribution channels.

Expected metadata shape:

```json
{
  "name": "social-media-manager",
  "version": "2.0.0",
  "category": "marketing-operations",
  "tags": {
    "en": ["social-media", "scheduling", "hebrew", "rtl", "israel"],
    "he": ["רשתות-חברתיות", "תזמון", "עברית", "ישראל"]
  }
}
```

## Documentation migration

### English guide

Confirm the English `SKILL.md` includes:

- Purpose and operating principles.
- Platform decision tree.
- Israeli posting windows.
- Hebrew RTL and emoji handling.
- Platform-specific guidance.
- Compliance decision tree.
- Examples for local businesses, freelancers and B2B.
- Edge cases.
- Anti-patterns.
- Troubleshooting.
- Production checklist.
- Output templates.

### Hebrew guide

Confirm `SKILL_HE.md` includes equivalent depth:

- Natural Israeli professional Hebrew.
- Correct terms such as `חשבונית`, `מדיניות פרטיות`, `הצהרת נגישות`, `עוסק פטור`, `דיוור שיווקי`.
- `₪` for prices.
- `DD/MM/YYYY` date display.
- No forced transliteration where a Hebrew term exists.
- Platform names as commonly used in Israel.
- Practical Israeli examples.

## Script migration

### Client

Replace ad-hoc scheduling with typed structures:

- `Platform`
- `PostDraft`
- `ScheduledPost`
- `ValidationIssue`
- `BusinessProfile`
- `BlackoutPeriod`
- `SocialMediaManagerClient`

Required capabilities:

- Sync schedule generation.
- Async schedule generation.
- Caption validation.
- Hashtag sanitation.
- RTL/emoji normalization.
- Shabbat avoidance.
- Blackout dates.
- JSON export.
- CSV export.
- Deterministic local IDs.

### CLI

Add commands:

- `plan`
- `validate`
- `export`
- `hashtags`
- `next-slots`

Required CLI behavior:

- Exit non-zero for invalid platform or invalid timezone.
- Output JSON by default for machine readability.
- Support `--platform` multiple times.
- Support `--days`.
- Support `--avoid-shabbat/--allow-shabbat`.
- Support `--blackout-date`.
- Preserve Hebrew output.

## Testing migration

Add at least 20 tests covering:

- Supported platforms.
- Invalid platforms.
- Timezone handling.
- Shabbat windows.
- Blackout dates.
- RTL and emoji preservation.
- Hashtag sanitation.
- Platform limits.
- Media requirements.
- Risk flags.
- Sync and async methods.
- JSON and CSV export.
- CLI validation.
- CLI export.
- Deterministic IDs.
- Metadata without author.
- License text.
- File presence.
- Hebrew guide content.
- No branding strings.

Run:

```bash
python -m pytest scripts/test_social-media-manager_client.py -q
```

Expected result:

```text
20+ passed
```

## Compliance migration

- Add anti-spam checklist.
- Add privacy checklist.
- Add consumer-offer checklist.
- Add accessibility checklist.
- Add influencer-disclosure note.
- Add copyright and music-rights note.
- Add escalation triggers for regulated claims.
- Add explicit fake-engagement and scraping boundary.

## Export migration

- Replace plain console schedules with structured exports.
- Use timezone-aware ISO 8601 for JSON.
- Use UTF-8 CSV.
- Add display dates in `DD/MM/YYYY` when appropriate.
- Include approval status on every item.
- Include risk flags.
- Keep captions and hashtags in separate fields.

## Backward compatibility notes

The enhanced package intentionally breaks compatibility with the old `posting_scheduler.py` interface. Use the new client or CLI instead.

Old:

```bash
python scripts/posting_scheduler.py --all
```

New:

```bash
python scripts/social-media-manager-cli.py plan --platform facebook --platform instagram --days 14
```

Old output:

```text
Facebook
Best times: 09:00, 12:30, 19:00
```

New output:

```json
{
  "items": [
    {
      "platform": "facebook",
      "scheduled_at": "2026-06-08T09:00:00+03:00",
      "approval_status": "pending_owner_review"
    }
  ]
}
```

## Rollout plan

1. Replace files in a branch.
2. Run tests.
3. Inspect generated zip tree.
4. Search for removed branding and author fields.
5. Run CLI examples.
6. Review Hebrew guide manually.
7. Review API/regulation references for current external changes.
8. Publish internally to the intended environment.
9. Monitor first real usage.
10. Update changelog with any corrections.

## Final acceptance checklist

- `metadata.json` contains no `author`.
- `LICENSE` says `the MIT copyright notice`.
- No decorative visuals, decorative visual references, or branding strings exist.
- `SKILL.md` and `SKILL_HE.md` are comprehensive.
- `references/api-reference.md` includes request/response examples and error tables.
- `references/workflow-guide.md` includes end-to-end workflows.
- `references/troubleshooting.md` exists.
- `references/test-scenarios.md` includes at least 20 scenarios.
- `references/migration-checklist.md` exists.
- `scripts/social_media_manager_client.py` exists.
- `scripts/social-media-manager-cli.py` exists.
- `scripts/test_social-media-manager_client.py` exists and passes.
- `scripts/examples/` contains at least 5 runnable examples.
- `CHANGELOG.md`, `README.md`, `LICENSE`, `pyproject.toml`, and `requirements-dev.txt` exist.
- Zip archive contains the enhanced package at the root.
