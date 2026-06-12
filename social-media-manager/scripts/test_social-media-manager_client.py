from __future__ import annotations

import asyncio
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

import social_media_manager_client as m


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "scripts" / "social-media-manager-cli.py"


def test_supported_platforms():
    assert {p.value for p in m.Platform} == {"facebook", "instagram", "tiktok", "linkedin"}


def test_parse_platform_aliases():
    assert m.parse_platform("ig") == m.Platform.INSTAGRAM
    assert m.parse_platform("fb") == m.Platform.FACEBOOK


def test_parse_platform_rejects_unknown():
    with pytest.raises(ValueError, match="UNKNOWN_PLATFORM"):
        m.parse_platform("twitter")


def test_timezone_valid():
    client = m.SocialMediaManagerClient(timezone="Asia/Jerusalem")
    assert client.timezone_name == "Asia/Jerusalem"


def test_timezone_invalid():
    with pytest.raises(ValueError, match="INVALID_TIMEZONE"):
        m.SocialMediaManagerClient(timezone="Israel/Time")


def test_contains_hebrew():
    assert m.contains_hebrew("שלום SaaS") is True
    assert m.contains_hebrew("hello") is False


def test_normalize_caption_preserves_emoji_and_english():
    text = "  מערכת SaaS   לצוותי Sales בישראל 🚀 \n\n\n חדש "
    normalized = m.normalize_caption(text)
    assert "SaaS" in normalized
    assert "Sales" in normalized
    assert "🚀" in normalized
    assert "\n\n\n" not in normalized


def test_sanitize_hebrew_hashtag_spaces():
    assert m.sanitize_hashtag("#עסקים קטנים") == "#עסקיםקטנים"


def test_sanitize_hebrew_hashtag_punctuation():
    assert m.sanitize_hashtag("#שיווק-דיגיטלי!") == "#שיווקדיגיטלי"


def test_normalize_hashtags_deduplicates():
    assert m.normalize_hashtags(["#עסקים קטנים", "עסקיםקטנים", "#שיווק"]) == ("#עסקיםקטנים", "#שיווק")


def test_normalize_city_alias():
    result = m.normalize_city("ראשלצ")
    assert result["normalized_city_he"] == "ראשון לציון"
    assert "#ראשוןלציון" in result["hashtags"]


def test_shabbat_window_friday_afternoon():
    dt = datetime.fromisoformat("2026-06-05T16:00:00+03:00")
    assert m.is_shabbat_window(dt) is True


def test_shabbat_window_saturday_evening_allowed():
    dt = datetime.fromisoformat("2026-06-06T21:00:00+03:00")
    assert m.is_shabbat_window(dt) is False


def test_recommend_slots_are_timezone_aware():
    client = m.SocialMediaManagerClient()
    slots = client.recommend_slots(["instagram"], start_date="2026-06-08", days=3)
    assert slots
    assert all(slot.scheduled_at.tzinfo is not None for slot in slots)
    assert all(slot.timezone == "Asia/Jerusalem" for slot in slots)


def test_blackout_date_skipped():
    client = m.SocialMediaManagerClient(blackout_periods=[m.BlackoutPeriod("2026-06-08")])
    slots = client.recommend_slots(["instagram"], start_date="2026-06-08", days=4)
    assert slots
    assert all(slot.scheduled_at.date().isoformat() != "2026-06-08" for slot in slots)


def test_instagram_reel_requires_media():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="instagram", format="reel", caption="טיפ קצר", media_count=0)
    valid, issues, risk_flags = client.validate_post(draft)
    assert not valid
    assert any(issue.code == "MEDIA_REQUIRED" for issue in issues)


def test_instagram_reel_with_media_valid_and_subtitle_flag():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="instagram", format="reel", caption="טיפ קצר", media_count=1)
    valid, issues, risk_flags = client.validate_post(draft)
    assert valid
    assert "requires_subtitles_check" in risk_flags


def test_hashtag_limit_exceeded():
    client = m.SocialMediaManagerClient()
    hashtags = tuple(f"#tag{i}" for i in range(31))
    draft = m.PostDraft(platform="instagram", format="post", caption="טיפ", media_count=1, hashtags=hashtags)
    valid, issues, _ = client.validate_post(draft)
    assert not valid
    assert any(issue.code == "HASHTAG_LIMIT_EXCEEDED" for issue in issues)


def test_caption_too_long():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="linkedin", caption="א" * 3001)
    valid, issues, _ = client.validate_post(draft)
    assert not valid
    assert any(issue.code == "CAPTION_TOO_LONG" for issue in issues)


def test_price_without_terms_flags_terms_required():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="facebook", caption="מבצע ב-₪99", contains_price=True)
    valid, issues, risk_flags = client.validate_post(draft)
    assert valid
    assert "terms_required" in risk_flags


def test_customer_image_flags_consent():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="instagram", format="post", media_count=1, caption="לפני ואחרי", contains_customer_image=True)
    _, _, risk_flags = client.validate_post(draft)
    assert "consent_required" in risk_flags


def test_regulated_claim_flags_review():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="facebook", caption="הטיפול מעלים כאבי גב תוך שבוע")
    _, _, risk_flags = client.validate_post(draft)
    assert "professional_review_required" in risk_flags


def test_facebook_group_flags_rules():
    client = m.SocialMediaManagerClient()
    draft = m.PostDraft(platform="facebook", format="group_post", caption="שאלה לקבוצה")
    _, _, risk_flags = client.validate_post(draft)
    assert "check_group_rules" in risk_flags


def test_schedule_posts_returns_pending_owner_review():
    client = m.SocialMediaManagerClient()
    drafts = m.sample_drafts(["facebook", "instagram"], business_type="מספרה")
    posts = client.schedule_posts(drafts, start_date="2026-06-08", days=7)
    assert posts
    assert all(post.approval_status == "pending_owner_review" for post in posts)


def test_scheduled_post_ids_deterministic():
    dt = datetime.fromisoformat("2026-06-08T08:30:00+03:00")
    first = m.deterministic_id(m.Platform.INSTAGRAM, dt, "שלום")
    second = m.deterministic_id(m.Platform.INSTAGRAM, dt, "שלום")
    assert first == second
    assert first.startswith("local-")


@pytest.mark.asyncio
async def test_async_recommend_slots():
    client = m.SocialMediaManagerClient()
    slots = await client.async_recommend_slots(["instagram"], start_date="2026-06-08", days=3)
    assert slots
    assert slots[0].timezone == "Asia/Jerusalem"


@pytest.mark.asyncio
async def test_async_schedule_posts():
    client = m.SocialMediaManagerClient()
    posts = await client.async_schedule_posts(m.sample_drafts(["tiktok"]), start_date="2026-06-08", days=7)
    assert posts
    assert posts[0].platform == m.Platform.TIKTOK


def test_export_json_parseable():
    client = m.SocialMediaManagerClient()
    posts = client.schedule_posts(m.sample_drafts(["linkedin"]), start_date="2026-06-08", days=7)
    payload = json.loads(client.export_json(posts))
    assert payload[0]["platform"] == "linkedin"
    assert payload[0]["scheduled_at"].endswith("+03:00")
    assert payload[0]["display_date_he"] == "09/06/2026"


def test_export_csv_parseable_with_hebrew():
    client = m.SocialMediaManagerClient()
    posts = client.schedule_posts(m.sample_drafts(["facebook"], business_type="מסעדה"), start_date="2026-06-08", days=7)
    rows = list(csv.DictReader(client.export_csv(posts).splitlines()))
    assert rows
    assert "מסעדה" in rows[0]["caption"]


def test_cli_validate_success():
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "validate",
            "--env",
            "sandbox",
            "--platform",
            "instagram",
            "--format",
            "reel",
            "--media-count",
            "1",
            "--caption",
            "טיפ קצר 💡",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["environment"] == "sandbox"


def test_cli_export_json_success():
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "export",
            "--platform",
            "facebook",
            "--days",
            "3",
            "--format",
            "json",
            "--start-date",
            "2026-06-08",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["items"]
    assert payload["items"][0]["platform"] == "facebook"


def test_cli_create_show_chain(tmp_path: Path):
    create = subprocess.run(
        [sys.executable, str(CLI_PATH), "create", "--platform", "linkedin", "--caption", "טיפ מקצועי לבעלי עסקים", "--start-date", "2026-06-08"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert create.returncode == 0
    created = json.loads(create.stdout)
    plan_path = tmp_path / "created.json"
    plan_path.write_text(create.stdout, encoding="utf-8")
    show = subprocess.run([sys.executable, str(CLI_PATH), "show", "--source", str(plan_path), "--local-id", created["local_id"]], text=True, capture_output=True, check=False)
    assert show.returncode == 0
    payload = json.loads(show.stdout)
    assert payload["found"] is True
    assert payload["item"]["local_id"] == created["local_id"]


def test_metadata_has_no_author():
    data = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    assert "author" not in data
    assert data["name"] == "social-media-manager"
    assert data["version"] == "2.1.0"


def test_license_uses_the_authors():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert ("Copyright " + "(c) The Authors") in text


def test_no_branding_strings():
    combined = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in ROOT.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".toml", ".txt", ".py"})
    for forbidden in ("skills" + "-il", "@" + "skills", "created " + "by", "built " + "by"):
        assert forbidden.lower() not in combined.lower()


def test_hebrew_skill_contains_local_formatting():
    text = (ROOT / "SKILL_HE.md").read_text(encoding="utf-8")
    assert "DD/MM/YYYY" in text
    assert "₪" in text
    assert "דיוור שיווקי" in text


def test_public_markdown_has_no_emoji_characters():
    public = [ROOT / "SKILL.md", ROOT / "SKILL_HE.md", ROOT / "README.md", ROOT / "CHANGELOG.md", *sorted((ROOT / "references").glob("*.md"))]
    emoji_pattern = re_compile_emoji()
    offenders = [str(path.relative_to(ROOT)) for path in public if emoji_pattern.search(path.read_text(encoding="utf-8"))]
    assert offenders == []


def re_compile_emoji():
    import re
    return re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000026FF]")


def test_required_files_exist():
    required = [
        "SKILL.md",
        "SKILL_HE.md",
        "references/api-reference.md",
        "references/workflow-guide.md",
        "references/troubleshooting.md",
        "references/test-scenarios.md",
        "references/migration-checklist.md",
        "references/branding-audit.md",
        "references/hebrew-qa-log.md",
        "references/verification-log.md",
        "scripts/social_media_manager_client.py",
        "scripts/social_media_manager_cli.py",
        "scripts/social-media-manager-cli.py",
        "scripts/test_social-media-manager_client.py",
        "CHANGELOG.md",
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "requirements-dev.txt",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel
    assert not (ROOT / "scripts" / "social-media-manager-client.py").exists()


def test_examples_count_and_use_env():
    examples = list((ROOT / "scripts" / "examples").glob("*.py"))
    assert len(examples) >= 5
    for path in examples:
        text = path.read_text(encoding="utf-8")
        assert "--env" in text
        assert "os.getenv" in text
        assert "ensure_ascii=False" in text
        assert "indent=2" in text


def test_importable_public_module():
    assert hasattr(m, "SocialMediaManagerClient")
    assert callable(m.sample_drafts)


def test_linkedin_reference_uses_rest_posts():
    text = (ROOT / "references" / "api-reference.md").read_text(encoding="utf-8")
    assert "https://api.linkedin.com/rest/posts" in text
    assert "Linkedin-Version: 202605" in text
    assert "https://api.linkedin.com/v2/ugcPosts" not in text


def test_verification_log_summary_counts():
    text = (ROOT / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "Total checks | 24" in text
    assert "Corrected in pass 2 ✗→✓ | 2" in text
    assert "Final unresolved ✗ | 0" in text
