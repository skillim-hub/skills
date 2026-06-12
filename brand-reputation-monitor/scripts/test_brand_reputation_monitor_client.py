from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from brand_reputation_monitor import (
    BrandReputationMonitor,
    Mention,
    MonitorConfig,
    create_monitor_config,
    deduplicate_mentions,
    detect_language,
    dump_results,
    load_mentions,
    load_monitor_config,
    normalize_date,
    normalize_source,
    parse_engagement,
    redact_private_data,
)


def result_for(text, source="facebook", engagement=0):
    mention = Mention(text=text, source=source, engagement=engagement)
    return BrandReputationMonitor().analyze_mention(mention)


def test_package_import_works():
    from brand_reputation_monitor import BrandReputationMonitor as Imported
    assert Imported is BrandReputationMonitor


def test_positive_hebrew():
    assert result_for("שירות מצוין ותודה רבה").sentiment.label == "positive"


def test_negative_hebrew():
    assert result_for("לא להתקרב, חיכיתי שעה ואף אחד לא ענה").sentiment.label == "negative"


def test_mixed_hebrew():
    assert result_for("המוצר טוב אבל השירות איטי").sentiment.label == "mixed"


def test_neutral_question():
    result = result_for("מישהו יודע מה שעות הפתיחה?")
    assert result.sentiment.label == "neutral"
    assert "info" in result.topics


def test_urgent_safety():
    result = result_for("העוגה הייתה מקולקלת, הילד הקיא")
    assert result.sentiment.label == "urgent"
    assert result.urgency is True
    assert "safety" in result.topics


def test_sarcasm_negative():
    assert result_for('איזה שירות "מדהים", מחכה כבר יומיים').sentiment.label in {"negative", "urgent"}


def test_slang_positive():
    assert result_for("אמאלה איזה טעים, נחזור שוב").sentiment.label == "positive"


def test_billing_topic():
    result = result_for("לא קיבלתי חשבונית מס ויש חיוב כפול")
    assert "billing" in result.topics
    assert result.risk_score >= 40


def test_legal_urgent():
    result = result_for("אני פונה לעורך דין אם לא תקבלו אחריות")
    assert result.urgency is True
    assert "legal" in result.topics


def test_privacy_redaction_id():
    redacted = redact_private_data('ת"ז 123456782 הופיעה בחשבונית')
    assert "[ID]" in redacted
    assert "123456782" not in redacted


def test_email_redaction():
    redacted = redact_private_data("שלחתי מייל ל-a@example.com ולא ענו")
    assert "[EMAIL]" in redacted
    assert "a@example.com" not in redacted


def test_phone_redaction():
    redacted = redact_private_data("הטלפון שלי 050-1234567")
    assert "[PHONE]" in redacted


def test_detect_language_hebrew():
    assert detect_language("שירות מצוין") == "he"


def test_detect_language_mixed():
    assert detect_language("הservice היה אחלה אבל delivery disaster") == "mixed"


def test_normalize_source_alias():
    assert normalize_source("twitter") == "x"
    assert normalize_source("fb") == "facebook"


def test_normalize_date_to_israeli_slash():
    assert normalize_date("2026-06-24") == "24/06/2026"
    assert normalize_date("24-06-2026") == "24/06/2026"


def test_parse_engagement_string():
    assert parse_engagement("1,234") == 1234


def test_parse_engagement_invalid():
    with pytest.raises(ValueError):
        parse_engagement("many")


def test_brand_match_required_excludes_common_name():
    monitor = BrandReputationMonitor(MonitorConfig(brand_terms=["המאפייה של דנה"], require_brand_match=True))
    result = monitor.analyze_mention(Mention(text="נועה אחרת לגמרי, לא קשור לעסק"))
    assert result.topics == ["false_positive"]
    assert result.risk_score == 0


def test_brand_match_required_allows_brand():
    monitor = BrandReputationMonitor(MonitorConfig(brand_terms=["המאפייה של דנה"], require_brand_match=True))
    result = monitor.analyze_mention(Mention(text="המאפייה של דנה מעולה"))
    assert result.sentiment.label == "positive"


def test_extract_accessibility_topic():
    result = result_for("האתר לא נגיש לקורא מסך")
    assert "accessibility" in result.topics


def test_high_engagement_increases_risk():
    low = result_for("לא מומלץ בכלל", engagement=0)
    high = result_for("לא מומלץ בכלל", engagement=60)
    assert high.risk_score > low.risk_score


def test_deduplicate_keeps_highest_engagement():
    mentions = [
        Mention(text="שירות מצוין", source="facebook", engagement=1),
        Mention(text="שירות מצוין", source="facebook", engagement=9),
    ]
    deduped = deduplicate_mentions(mentions)
    assert len(deduped) == 1
    assert deduped[0].engagement == 9


def test_load_mentions_csv(tmp_path):
    path = tmp_path / "mentions.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["date", "source", "text", "engagement"])
        writer.writeheader()
        writer.writerow({"date": "24/06/2026", "source": "facebook", "text": "שירות מצוין", "engagement": "3"})
    mentions = load_mentions(path)
    assert len(mentions) == 1
    assert mentions[0].engagement == 3


def test_load_mentions_json_object(tmp_path):
    path = tmp_path / "mentions.json"
    path.write_text(json.dumps({"mentions": [{"text": "לא מומלץ", "source": "x"}]}, ensure_ascii=False), encoding="utf-8")
    mentions = load_mentions(path)
    assert len(mentions) == 1
    assert mentions[0].source == "x"


def test_dump_results_json(tmp_path):
    result = result_for("שירות מצוין")
    out = tmp_path / "out.json"
    dump_results([result], out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data[0]["sentiment"]["label"] == "positive"


def test_dump_results_csv(tmp_path):
    result = result_for("שירות מצוין")
    out = tmp_path / "out.csv"
    dump_results([result], out, "csv")
    assert "sentiment" in out.read_text(encoding="utf-8-sig")


@pytest.mark.asyncio
async def test_async_analyze_one():
    monitor = BrandReputationMonitor()
    result = await monitor.analyze_mention_async(Mention(text="שירות מצוין"))
    assert result.sentiment.label == "positive"


@pytest.mark.asyncio
async def test_async_analyze_many():
    monitor = BrandReputationMonitor()
    results = await monitor.analyze_many_async([Mention(text="שירות מצוין"), Mention(text="לא מומלץ")])
    assert len(results) == 2


def test_summary_counts():
    monitor = BrandReputationMonitor()
    results = monitor.analyze_many([Mention(text="שירות מצוין"), Mention(text="לא מומלץ")])
    summary = monitor.summarize(results)
    assert summary["total"] == 2
    assert summary["sentiment"]["positive"] == 1


def test_markdown_report_contains_local_date():
    monitor = BrandReputationMonitor()
    report = monitor.generate_markdown_report([result_for("שירות מצוין")])
    assert "# Brand Reputation Report" in report
    assert "Generated:" in report


def test_cli_single_runs():
    completed = subprocess.run(
        [sys.executable, "-m", "brand_reputation_monitor.cli", "single", "שירות מצוין", "--env", "sandbox"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert '"label": "positive"' in completed.stdout


def test_cli_chained_config_create_and_analyze(tmp_path, monkeypatch):
    monkeypatch.setenv("BRM_CONFIG_DIR", str(tmp_path / "configs"))
    data = tmp_path / "mentions.json"
    data.write_text(json.dumps({"mentions": [{"text": "המאפייה של דנה מעולה", "source": "facebook"}]}, ensure_ascii=False), encoding="utf-8")
    created = subprocess.run(
        [
            sys.executable,
            "-m",
            "brand_reputation_monitor.cli",
            "config-create",
            "--name",
            "daily-monitor",
            "--env",
            "sandbox",
            "--brand-term",
            "המאפייה של דנה",
            "--require-brand-match",
        ],
        text=True,
        capture_output=True,
        check=True,
        env=os.environ.copy(),
    )
    config_id = json.loads(created.stdout)["id"]
    analyzed = subprocess.run(
        [sys.executable, "-m", "brand_reputation_monitor.cli", "analyze", str(data), "--env", "sandbox", "--config-id", config_id],
        text=True,
        capture_output=True,
        check=True,
        env=os.environ.copy(),
    )
    assert '"total": 1' in analyzed.stdout
    assert '"positive": 1' in analyzed.stdout


def test_create_and_load_config(tmp_path, monkeypatch):
    monkeypatch.setenv("BRM_CONFIG_DIR", str(tmp_path / "configs"))
    payload = create_monitor_config("test", env="sandbox", brand_terms=["מותג"], require_brand_match=True)
    loaded = load_monitor_config(payload["id"], env="sandbox")
    assert loaded.brand_terms == ["מותג"]
    assert loaded.require_brand_match is True


def test_unsupported_format(tmp_path):
    path = tmp_path / "mentions.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        load_mentions(path)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_mentions("/path/that/does/not/exist.csv")
