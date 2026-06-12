# Test Scenarios

Use these scenarios to validate the skill, scripts, CLI, and operational workflows. Each scenario includes input, expected output, and acceptance criteria.

## Scenario 1: Instagram Reel for a salon

Input:
```json
{
  "platform": "instagram",
  "format": "reel",
  "caption": "לפני צבע? 3 דברים שכדאי לדעת ",
  "media_count": 1,
  "hashtags": ["#מספרה", "#ראשוןלציון"]
}
```

Expected:
- Caption is valid.
- Hebrew and emoji are preserved.
- Risk flag reminds to add subtitles.
- Schedule uses `Asia/Jerusalem`.

Acceptance:
- No caption length error.
- No media-required error.

## Scenario 2: Instagram Reel without media

Input: same as Scenario 1 with `media_count: 0`.

Expected:
- Validation fails with `MEDIA_REQUIRED`.

Acceptance:
- Error text explains that Instagram Reels require media.

## Scenario 3: TikTok educational video

Input:
```json
{
  "platform": "tiktok",
  "format": "video",
  "caption": "3 טעויות לפני שמזמינים שירות לבית",
  "media_count": 1
}
```

Expected:
- Valid caption.
- Schedule suggests Sunday, Tuesday or Thursday.
- Risk flag suggests subtitles.

Acceptance:
- Output includes a video-specific asset reminder.

## Scenario 4: LinkedIn B2B insight

Input:
```json
{
  "platform": "linkedin",
  "format": "text",
  "caption": "רוב צוותי המכירות לא צריכים עוד dashboard. הם צריכים פחות רעש בין lead לפעולה הבאה."
}
```

Expected:
- Valid.
- Tone classified as professional.
- No hashtag requirement.

Acceptance:
- No Instagram-style hashtag warning unless hashtags exceed limit.

## Scenario 5: Facebook group local post

Input:
```json
{
  "platform": "facebook",
  "format": "group_post",
  "caption": "יש תורים פנויים השבוע בגבעתיים. כתבו לי בפרטי לפרטים."
}
```

Expected:
- Valid.
- Warning to read group rules.
- CTA accepted.

Acceptance:
- No automation recommendation for mass group posting.

## Scenario 6: Friday afternoon schedule

Input:
```json
{
  "platforms": ["facebook"],
  "start_date": "2026-06-05",
  "time": "16:00",
  "avoid_shabbat": true
}
```

Expected:
- Slot rejected or moved.
- `SHABBAT_WINDOW` warning appears.

Acceptance:
- New slot is outside Friday 15:00 to Saturday 20:30.

## Scenario 7: Saturday evening schedule

Input:
```json
{
  "platforms": ["instagram"],
  "start_date": "2026-06-06",
  "time": "21:00",
  "avoid_shabbat": true
}
```

Expected:
- Slot accepted.

Acceptance:
- Time is after Saturday 20:30 in `Asia/Jerusalem`.

## Scenario 8: Custom blackout date

Input:
```json
{
  "platforms": ["linkedin"],
  "start_date": "2026-09-22",
  "blackout_dates": ["2026-09-22"]
}
```

Expected:
- No post scheduled on blackout date.

Acceptance:
- Item moves to next safe workday.

## Scenario 9: Hebrew hashtag with spaces

Input: `"#עסקים קטנים"`

Expected:
- Sanitized to `#עסקיםקטנים`.

Acceptance:
- Output has no spaces.

## Scenario 10: Hebrew hashtag with punctuation

Input: `"#שיווק-דיגיטלי!"`

Expected:
- Sanitized to `#שיווקדיגיטלי`.

Acceptance:
- Punctuation removed.

## Scenario 11: Too many Instagram hashtags

Input: Instagram post with 31 hashtags.

Expected:
- Validation issue `HASHTAG_LIMIT_EXCEEDED`.

Acceptance:
- Message explains maximum hashtag count.

## Scenario 12: Caption too long

Input: LinkedIn caption longer than configured limit.

Expected:
- Validation issue `CAPTION_TOO_LONG`.

Acceptance:
- Message includes current length and max length.

## Scenario 13: Offer without expiry

Input:
```json
{
  "caption": "מבצע ענק! כל החנות ב-₪99",
  "contains_price": true,
  "offer_terms": ""
}
```

Expected:
- Risk flag `terms_required`.

Acceptance:
- Output asks for expiry date and conditions.

## Scenario 14: Customer before/after photo

Input:
```json
{
  "contains_customer_image": true,
  "caption": "לפני ואחרי טיפול"
}
```

Expected:
- Risk flag `consent_required`.

Acceptance:
- Output requires documented consent.

## Scenario 15: Health claim

Input:
```json
{
  "caption": "הטיפול הזה מעלים כאבי גב תוך שבוע"
}
```

Expected:
- Risk flag `professional_review_required`.

Acceptance:
- Output recommends professional review and softer wording.

## Scenario 16: Async schedule generation

Input:
```python
await client.async_recommend_slots(["instagram"], days=3)
```

Expected:
- Returns a list of timezone-aware slots.

Acceptance:
- All slots include `Asia/Jerusalem`.

## Scenario 17: JSON export

Input: generated schedule with two posts.

Expected:
- Valid JSON array.
- ISO timestamps include offsets.

Acceptance:
- `json.loads` succeeds.

## Scenario 18: CSV export with Hebrew

Input: generated schedule with Hebrew captions.

Expected:
- CSV is UTF-8 compatible.
- Hebrew remains readable.

Acceptance:
- `csv.DictReader` reads expected rows.

## Scenario 19: CLI validate command

Command:
```bash
python scripts/social-media-manager-cli.py validate --platform instagram --caption "טיפ קצר " --media-count 1
```

Expected:
- CLI exits 0.
- Output includes `"valid": true`.

Acceptance:
- JSON output parse succeeds.

## Scenario 20: CLI export command

Command:
```bash
python scripts/social-media-manager-cli.py export --platform facebook --days 3 --format json
```

Expected:
- CLI exits 0.
- Output includes at least one scheduled item.

Acceptance:
- Each item has `platform`, `scheduled_at`, and `timezone`.

## Scenario 21: Mixed Hebrew and English

Input:
```text
מערכת SaaS חדשה לצוותי Sales בישראל 
```

Expected:
- Normalization preserves Hebrew, English and emoji.
- Directional characters do not corrupt visible text.

Acceptance:
- Output contains `SaaS`, `Sales`, and ``.

## Scenario 22: City nickname normalization

Input: `ראשלצ`

Expected:
- Suggested canonical city: `ראשון לציון`.
- Suggested hashtag: `#ראשוןלציון`.

Acceptance:
- Low-confidence mappings request confirmation.

## Scenario 23: Emergency pause

Input:
```json
{
  "emergency_pause": true,
  "queued_posts": 5
}
```

Expected:
- Commercial posts marked `hold`.
- Service updates remain eligible.

Acceptance:
- No promotional post remains approved automatically.

## Scenario 24: Duplicate post prevention

Input: same draft scheduled twice.

Expected:
- Deterministic IDs match.
- Duplicate can be detected.

Acceptance:
- Export includes only one item when deduplication is enabled.

## Scenario 25: Owner approval status

Input: new generated schedule.

Expected:
- Every item starts as `pending_owner_review`.

Acceptance:
- No item defaults to `approved`.

## Scenario 26: LinkedIn confidential client detail

Input:
```text
לקוח מחברת X שילם ₪180,000 ועזב מתחרה ספציפי אחרי שבוע.
```

Expected:
- Risk flag for confidentiality and claim review.

Acceptance:
- Output suggests anonymization.

## Scenario 27: Giveaway terms missing

Input:
```text
הגרלה! כתבו תגובה וזכו בטיפול חינם.
```

Expected:
- Risk flag `terms_required`.

Acceptance:
- Output asks for eligibility, dates, prize, selection method, limitations.

## Scenario 28: Accessibility review for video

Input: video post with no subtitles.

Expected:
- Warning to add Hebrew subtitles.

Acceptance:
- Risk flag or asset requirement mentions subtitles.

## Scenario 29: Wrong timezone input

Input: `Israel/Time`

Expected:
- Error `INVALID_TIMEZONE`.

Acceptance:
- Message recommends `Asia/Jerusalem`.

## Scenario 30: Unknown platform

Input: `twitter`

Expected:
- Error `UNKNOWN_PLATFORM`.

Acceptance:
- Message lists supported platforms.
