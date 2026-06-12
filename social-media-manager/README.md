# Social-Media Manager

A neutral skill package for planning, validating, and scheduling organic social-media content for Israeli small businesses, freelancers, and consumer-facing services.

The package supports Facebook, Instagram, TikTok, and LinkedIn planning with Hebrew-friendly right-to-left handling, symbol preservation, Israeli timezone scheduling, Shabbat-sensitive scheduling, blackout dates, compliance notes, JSON/CSV export, a typed Python helper, a Click-based CLI, runnable examples, and pytest coverage.

## What this package does

- Builds practical organic content calendars.
- Validates captions, hashtags, platform limits, media requirements, and risk flags.
- Handles Hebrew text, mixed English/Hebrew captions, `₪`, and Israeli display dates.
- Schedules posts in `Asia/Jerusalem`.
- Avoids Friday afternoon through Saturday evening by default.
- Supports custom blackout dates such as memorial days, Yom Kippur, emergency pauses, or owner review pauses.
- Exports schedules as JSON or CSV.
- Keeps all posts in `pending_owner_review` status until approval.

## What this package does not do

- It does not publish directly to Facebook, Instagram, TikTok, or LinkedIn.
- It does not buy ads.
- It does not scrape groups or user data.
- It does not generate fake engagement.
- It does not replace legal review.

## File index

```text
.
├── SKILL.md
├── SKILL_HE.md
├── metadata.json
├── README.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── requirements-dev.txt
├── references
│   ├── api-reference.md
│   ├── workflow-guide.md
│   ├── troubleshooting.md
│   ├── test-scenarios.md
│   ├── migration-checklist.md
│   ├── branding-audit.md
│   └── hebrew-qa-log.md
└── scripts
    ├── social_media_manager_client.py
    ├── social_media_manager_cli.py
    ├── social-media-manager-cli.py
    ├── test_social-media-manager_client.py
    └── examples
        ├── 01_plan_local_salon.py
        ├── 02_validate_hebrew_caption.py
        ├── 03_export_csv.py
        ├── 04_async_schedule.py
        ├── 05_blackout_dates.py
        └── 06_cli_usage.py
```

## Installation for development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

The package is importable after installation:

```python
from social_media_manager_client import PostDraft, SocialMediaManagerClient
```

## Quick start

Create one scheduled post, extract its local identifier, then use the identifier in the next command:

```bash
CREATE_RESPONSE=$(python scripts/social-media-manager-cli.py create \
  --env sandbox \
  --platform instagram \
  --format reel \
  --media-count 1 \
  --caption "טיפ קצר לבעלי עסקים" \
  --hashtag "#עסקים קטנים" \
  --start-date 2026-06-08)

printf '%s\n' "$CREATE_RESPONSE" > created-post.json
POST_ID=$(python -c 'import json,sys; print(json.load(open("created-post.json", encoding="utf-8"))["local_id"])')
python scripts/social-media-manager-cli.py show --source created-post.json --local-id "$POST_ID"
```

Create a sample plan:

```bash
python scripts/social-media-manager-cli.py plan \
  --env sandbox \
  --platform facebook \
  --platform instagram \
  --days 14 \
  --business-type "מספרה" \
  --start-date 2026-06-08
```

Validate a Hebrew caption:

```bash
python scripts/social-media-manager-cli.py validate \
  --env sandbox \
  --platform instagram \
  --format reel \
  --media-count 1 \
  --caption "מבצע ב-₪99 עד 30/06/2026. פרטים מלאים באתר." \
  --contains-price \
  --offer-terms "עד 30/06/2026, בכפוף לזמינות"
```

Run examples:

```bash
SOCIAL_MEDIA_MANAGER_BUSINESS_TYPE="מספרה" python scripts/examples/01_plan_local_salon.py --env sandbox
python scripts/examples/04_async_schedule.py --env production
```

## Development checks

```bash
python -m pytest
python -m compileall scripts/ -q
```

## Production notes

- Keep platform tokens, owner approvals, consent records, and publishing actions outside this helper.
- Review regulated claims, discounts, giveaways, testimonials, personal-data usage, and `references/verification-log.md` before publishing.
- Use exported JSON or CSV as an approval artifact, not as proof that a platform accepted a post.
