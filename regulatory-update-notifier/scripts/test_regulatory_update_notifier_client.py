from __future__ import annotations

import asyncio
import datetime as dt
import json
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from regulatory_update_notifier import (
    AlertProfile,
    RegulatoryFetchError,
    RegulatoryMonitorClient,
    RegulatoryParseError,
    RegulatoryUpdate,
    SourceType,
    UpdateSource,
    create_profile,
    deduplicate_updates,
    default_sources,
    detect_dates,
    detect_shekel_amounts,
    format_il_date,
    infer_industries,
    load_profile,
    load_updates,
    make_digest,
    matches_filter,
    normalize_title,
    parse_date,
    save_default_config,
    save_profile,
    save_updates,
    score_update,
    stable_id,
    strip_html,
    summarize_update,
)
from regulatory_update_notifier.cli import app

RSS = """<?xml version="1.0"?>
<rss><channel>
<item><title>Consumer cancellation guidance</title><link>https://example.test/a</link><pubDate>Mon, 01 Jun 2026 10:00:00 GMT</pubDate><description>New חובה for ecommerce cancellation by 30/06/2026 and amount ₪10,000</description></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Privacy database draft</title><link href="https://example.test/p"/><updated>2026-05-20T00:00:00Z</updated><summary>טיוטה להערות הציבור בנושא מאגר מידע</summary></entry>
</feed>"""


def source(source_type: str = "rss", text: str | None = None) -> UpdateSource:
    return UpdateSource(
        name="Consumer Protection publications",
        url="inline://fixture",
        source_type=source_type,
        regulator="Consumer Protection and Fair Trade Authority",
        tags=["consumer", "ecommerce"],
        industries=["ecommerce", "retail", "consumers"],
        inline_text=text,
    )


def test_parse_il_date_dash() -> None:
    assert parse_date("02-06-2026") == dt.date(2026, 6, 2)


def test_parse_il_date_slash() -> None:
    assert parse_date("2/6/26") == dt.date(2026, 6, 2)


def test_parse_iso_date() -> None:
    assert parse_date("2026-06-02T10:00:00") == dt.date(2026, 6, 2)


def test_format_il_date_uses_local_slash_format() -> None:
    assert format_il_date(dt.date(2026, 6, 2)) == "02/06/2026"


def test_detect_dates_multiple_formats() -> None:
    assert dt.date(2026, 6, 30) in detect_dates("עד 30/06/2026 או 2026-07-01")


def test_detect_shekel_amounts() -> None:
    assert "₪10,000" in detect_shekel_amounts("הסף הוא ₪10,000 לפני מעמ")


def test_normalize_title_removes_punctuation() -> None:
    assert normalize_title("  ביטול-עסקה!!  ") == "ביטול עסקה"


def test_stable_id_is_stable() -> None:
    assert stable_id("A", "B") == stable_id("A", "B")


def test_strip_html_removes_script() -> None:
    assert "bad" not in strip_html("<script>bad</script><p>טקסט</p>")


def test_source_rejects_bad_scheme() -> None:
    with pytest.raises(ValueError):
        UpdateSource(name="bad", url="ftp://example.test", source_type="html", regulator="x")


def test_parse_rss_item() -> None:
    monitor = RegulatoryMonitorClient([source("rss", RSS)])
    updates = monitor.parse_source_content(source("rss", RSS), RSS)
    assert len(updates) == 1
    assert updates[0].title == "Consumer cancellation guidance"
    assert updates[0].published_at == dt.date(2026, 6, 1)


def test_parse_atom_item() -> None:
    updates = RegulatoryMonitorClient([source("atom", ATOM)]).parse_source_content(source("atom", ATOM), ATOM)
    assert len(updates) == 1
    assert updates[0].title == "Privacy database draft"
    assert updates[0].status == "draft-regulation"


def test_parse_json_value_records() -> None:
    payload = json.dumps({"value": [{"Name": "הצעת חוק צרכנית", "PublicationDate": "2026-05-01", "Description": "הצעת חוק בנושא צרכנות"}]}, ensure_ascii=False)
    src = source("odata", payload)
    updates = RegulatoryMonitorClient([src]).parse_source_content(src, payload)
    assert updates[0].title == "הצעת חוק צרכנית"
    assert updates[0].status == "bill"


def test_parse_html_to_single_update() -> None:
    html = "<html><h1>הנחיה בנושא ביטול עסקה</h1><p>חובה לעדכן אתר עד 30/06/2026</p></html>"
    src = source("html", html)
    updates = RegulatoryMonitorClient([src]).parse_source_content(src, html)
    assert updates[0].status == "guidance"
    assert "ביטול" in updates[0].title


def test_invalid_json_raises_parse_error() -> None:
    with pytest.raises(RegulatoryParseError):
        RegulatoryMonitorClient([source("json", "{")]).parse_source_content(source("json", "{"), "{")


def test_collect_updates_filters_keyword_and_industry() -> None:
    src = source("rss", RSS)
    monitor = RegulatoryMonitorClient([src])
    updates = monitor.collect_updates(industries=["ecommerce"], keywords=["cancellation"], minimum_score=30)
    assert len(updates) == 1
    assert updates[0].score >= 30


def test_collect_updates_since_filters_old() -> None:
    src = source("rss", RSS)
    monitor = RegulatoryMonitorClient([src])
    assert monitor.collect_updates(since="02/06/2026") == []


def test_profile_adds_filters() -> None:
    profile = create_profile(name="חנות", industries=["ecommerce"], keywords=["cancellation"], locale="he")
    updates = RegulatoryMonitorClient([source("rss", RSS)]).collect_updates(profile=profile, minimum_score=30)
    assert len(updates) == 1


def test_async_collect_updates() -> None:
    updates = asyncio.run(RegulatoryMonitorClient([source("rss", RSS)]).acollect_updates(industries=["ecommerce"]))
    assert len(updates) == 1


def test_save_and_load_updates(tmp_path: Path) -> None:
    updates = RegulatoryMonitorClient([source("rss", RSS)]).collect_updates()
    path = tmp_path / "updates.json"
    save_updates(path, updates)
    loaded = load_updates(path)
    assert loaded[0].id == updates[0].id


def test_save_and_load_profile(tmp_path: Path) -> None:
    profile = create_profile(name="יועץ", industries=["professional-services"], keywords=["מאגר מידע"])
    path = tmp_path / "profile.json"
    save_profile(path, profile)
    loaded = load_profile(path, profile.id)
    assert loaded.id == profile.id


def test_load_profile_mismatch_raises(tmp_path: Path) -> None:
    profile = create_profile(name="יועץ", industries=["professional-services"])
    path = tmp_path / "profile.json"
    save_profile(path, profile)
    with pytest.raises(ValueError):
        load_profile(path, "other")


def test_make_digest_hebrew_contains_local_date() -> None:
    update = RegulatoryMonitorClient([source("rss", RSS)]).collect_updates()[0]
    digest = make_digest([update], locale="he")
    assert "01/06/2026" in digest
    assert "₪10,000" in digest


def test_summarize_update_english() -> None:
    update = RegulatoryMonitorClient([source("rss", RSS)]).collect_updates()[0]
    summary = summarize_update(update, locale="en")
    assert "Status" in summary


def test_infer_industries_privacy() -> None:
    assert "privacy" in infer_industries("מאגר מידע ופרטיות")


def test_score_update_caps_at_100() -> None:
    update = RegulatoryUpdate(
        source="x",
        title="חובה קנס עד 30/06/2026",
        summary="מסחר מקוון ₪10,000 חובה קנס",
        url="inline://x",
        published_at=dt.date(2026, 6, 1),
        regulator="x",
        source_type="manual",
        industries=["ecommerce"],
        raw_text="חובה קנס עד 30/06/2026 ₪10,000",
        status="enacted",
    )
    assert score_update(update, industries=["ecommerce"], keywords=["חובה"]) <= 100


def test_matches_filter_false_for_unrelated_industry() -> None:
    update = RegulatoryUpdate(
        source="x",
        title="פרטיות",
        summary="מאגר מידע",
        url="inline://x",
        published_at=None,
        regulator="x",
        source_type="manual",
        industries=["privacy"],
    )
    assert not matches_filter(update, industries=["food"])


def test_deduplicate_keeps_higher_score() -> None:
    a = RegulatoryUpdate(source="s", title="A", summary="", url="u", published_at=None, regulator="r", source_type="manual", score=1)
    b = RegulatoryUpdate(source="s", title="A", summary="", url="u", published_at=None, regulator="r", source_type="manual", score=50)
    assert deduplicate_updates([a, b])[0].score == 50


def test_default_sources_sandbox_are_inline() -> None:
    assert all(item.url.startswith("inline://") for item in default_sources("sandbox"))


def test_save_default_config(tmp_path: Path) -> None:
    path = tmp_path / "sources.json"
    save_default_config(path, "sandbox")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["sources"]


def test_fetch_error_from_http_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, request=request)

    client = RegulatoryMonitorClient(
        [UpdateSource(name="remote", url="https://example.test", source_type="html", regulator="x")],
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(RegulatoryFetchError):
        client.collect_updates()


def test_cli_classify() -> None:
    result = CliRunner().invoke(app, ["classify", "מסחר מקוון וביטול עסקה"])
    assert result.exit_code == 0
    assert "ecommerce" in result.output


def test_cli_create_profile_and_scan_chain(tmp_path: Path) -> None:
    runner = CliRunner()
    profile_path = tmp_path / "profile.json"
    create_result = runner.invoke(
        app,
        [
            "create-profile",
            "--name",
            "חנות אונליין",
            "--industry",
            "ecommerce",
            "--keyword",
            "cancellation",
            "--output",
            str(profile_path),
            "--env",
            "sandbox",
        ],
    )
    assert create_result.exit_code == 0
    profile_id = json.loads(create_result.output)["id"]
    scan_result = runner.invoke(app, ["scan", "--profile", str(profile_path), "--profile-id", profile_id, "--env", "sandbox"])
    assert scan_result.exit_code == 0
    assert "Consumer cancellation" in scan_result.output


def test_cli_make_config_and_digest(tmp_path: Path) -> None:
    runner = CliRunner()
    config = tmp_path / "sources.json"
    result = runner.invoke(app, ["make-config", str(config), "--env", "sandbox"])
    assert result.exit_code == 0
    updates_path = tmp_path / "updates.json"
    scan_result = runner.invoke(app, ["scan", "--config", str(config), "--output", str(updates_path), "--env", "sandbox"])
    assert scan_result.exit_code == 0
    digest_result = runner.invoke(app, ["digest", "--input", str(updates_path), "--locale", "he"])
    assert digest_result.exit_code == 0
    assert "דוח שינויי רגולציה" in digest_result.output
