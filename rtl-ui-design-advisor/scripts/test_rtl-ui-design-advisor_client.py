from __future__ import annotations

import asyncio
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from rtl_ui_design_advisor import (
    RtlAuditClient,
    format_dd_mm_yyyy,
    infer_direction,
    recommend_input_attributes,
    recommended_input_dir,
    validate_israeli_id,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_infer_hebrew_direction():
    assert infer_direction("שלום") == "rtl"


def test_infer_arabic_direction():
    assert infer_direction("مرحبا") == "rtl"


def test_infer_english_direction():
    assert infer_direction("hello") == "ltr"


def test_infer_auto_for_numbers():
    assert infer_direction("12345") == "auto"


def test_recommended_email_ltr():
    assert recommended_input_dir("email") == "ltr"


def test_recommended_search_auto():
    assert recommended_input_dir("search") == "auto"


def test_recommend_tel_attributes():
    attrs = recommend_input_attributes("tel", "phone")
    assert attrs["dir"] == "ltr"
    assert attrs["inputmode"] == "tel"


def test_recommend_amount_attributes():
    attrs = recommend_input_attributes("text", "amount")
    assert attrs["dir"] == "ltr"
    assert attrs["inputmode"] == "decimal"


def test_html_missing_dir_is_high():
    result = RtlAuditClient().audit_html('<html lang="he"><body></body></html>')
    assert any(issue.code == "HTML_DIR_MISSING" and issue.severity == "high" for issue in result.issues)


def test_html_missing_lang_is_medium():
    result = RtlAuditClient().audit_html('<html dir="rtl"><body></body></html>')
    assert any(issue.code == "HTML_LANG_MISSING" for issue in result.issues)


def test_html_valid_root_no_root_issue():
    result = RtlAuditClient().audit_html('<html lang="he" dir="rtl"><body><main></main></body></html>')
    codes = {issue.code for issue in result.issues}
    assert "HTML_DIR_MISSING" not in codes
    assert "HTML_LANG_MISSING" not in codes


def test_tel_input_requires_ltr():
    result = RtlAuditClient().audit_html('<html lang="he" dir="rtl"><input type="tel" name="phone"></html>')
    assert any(issue.code == "FORM_LTR_DIR_MISSING" for issue in result.issues)


def test_text_input_recommends_auto():
    result = RtlAuditClient().audit_html('<html lang="he" dir="rtl"><input type="text" name="customerName"></html>')
    assert any(issue.code == "FORM_AUTO_DIR_MISSING" for issue in result.issues)


def test_textarea_recommends_auto():
    result = RtlAuditClient().audit_html('<html lang="he" dir="rtl"><textarea name="note"></textarea></html>')
    assert any(issue.code == "TEXTAREA_AUTO_DIR_MISSING" for issue in result.issues)


def test_css_margin_left_detected():
    result = RtlAuditClient().audit_css(".x { margin-left: 1rem; }")
    assert any(issue.code == "CSS_PHYSICAL_DIRECTION" for issue in result.issues)


def test_css_padding_right_detected():
    result = RtlAuditClient().audit_css(".x { padding-right: 8px; }")
    assert any("padding-right" in (issue.evidence or "") for issue in result.issues)


def test_css_text_align_right_detected():
    result = RtlAuditClient().audit_css(".x { text-align: right; }")
    assert any(issue.code == "CSS_PHYSICAL_TEXT_ALIGN" for issue in result.issues)


def test_css_translate_review():
    result = RtlAuditClient().audit_css(".drawer { transform: translateX(100%); }")
    assert any(issue.code == "CSS_TRANSLATE_X_REVIEW" for issue in result.issues)


def test_css_bidi_override_detected():
    result = RtlAuditClient().audit_css(".x { unicode-bidi: bidi-override; }")
    assert any(issue.code == "CSS_BIDI_OVERRIDE" for issue in result.issues)


def test_fix_css_logical_replaces_padding_and_alignment():
    fixed = RtlAuditClient().fix_css_logical(".x { padding-left: 1rem; text-align: right; right: 0; }")
    assert "padding-inline-start" in fixed
    assert "text-align: start" in fixed
    assert "inset-inline-end" in fixed


def test_tailwind_ml_detected():
    result = RtlAuditClient().audit_tailwind("flex ml-4")
    assert any(issue.code == "TW_PHYSICAL_MARGIN" for issue in result.issues)


def test_tailwind_text_left_detected():
    result = RtlAuditClient().audit_tailwind("text-left")
    assert any(issue.code == "TW_PHYSICAL_TEXT_ALIGN" for issue in result.issues)


def test_tailwind_space_x_detected():
    result = RtlAuditClient().audit_tailwind("space-x-4")
    assert any(issue.code == "TW_SPACE_X" for issue in result.issues)


def test_tailwind_logical_is_clean():
    result = RtlAuditClient().audit_tailwind("flex gap-4 ps-4 pe-4 text-start start-0 end-0")
    assert result.summary["total"] == 0


def test_result_json_is_valid():
    result = RtlAuditClient().audit_css(".x { left: 0; }")
    payload = json.loads(result.to_json())
    assert payload["summary"]["total"] >= 1


def test_result_markdown_has_table():
    result = RtlAuditClient().audit_css(".x { right: 0; }")
    assert "| Severity | Code |" in result.to_markdown()


def test_async_html_audit():
    result = asyncio.run(RtlAuditClient().audit_html_async('<html lang="he"><body></body></html>'))
    assert any(issue.code == "HTML_DIR_MISSING" for issue in result.issues)


def test_async_css_audit():
    result = asyncio.run(RtlAuditClient().audit_css_async(".x { margin-right: 1rem; }"))
    assert result.summary["total"] == 1


def test_async_tailwind_audit():
    result = asyncio.run(RtlAuditClient().audit_tailwind_async("right-0"))
    assert any(issue.code == "TW_PHYSICAL_INSET" for issue in result.issues)


def test_create_and_get_audit(tmp_path):
    client = RtlAuditClient(tmp_path)
    record = client.create_audit("tailwind", "ml-4 text-left", env="sandbox")
    loaded = client.get_audit(record.id)
    assert loaded.id == record.id
    assert loaded.result.summary["total"] == 2


def test_create_audit_production_env(tmp_path):
    record = RtlAuditClient(tmp_path).create_audit("css", ".x { left: 0; }", env="production")
    assert record.env == "production"


def test_create_audit_invalid_kind(tmp_path):
    with pytest.raises(ValueError):
        RtlAuditClient(tmp_path).create_audit("bad", "x")  # type: ignore[arg-type]


def test_async_create_and_get_audit(tmp_path):
    async def run():
        client = RtlAuditClient(tmp_path)
        record = await client.create_audit_async("css", ".x { right: 0; }")
        return await client.get_audit_async(record.id)
    loaded = asyncio.run(run())
    assert loaded.result.summary["total"] == 1


def test_validate_israeli_id_known_valid():
    assert validate_israeli_id("123456782") is True


def test_validate_israeli_id_invalid():
    assert validate_israeli_id("123456789") is False


def test_date_format_uses_slashes():
    assert format_dd_mm_yyyy(2026, 6, 3) == "03/06/2026"


def test_localization_profile():
    profile = RtlAuditClient().localization_profile("he-IL")
    assert profile["dir"] == "rtl"
    assert profile["currency_symbol"] == "₪"
    assert profile["date_policy"] == "DD/MM/YYYY"


def test_checklist_has_many_items():
    assert len(RtlAuditClient().production_checklist()) >= 12


def test_summarize_result():
    result = RtlAuditClient().audit_tailwind("ml-4")
    assert "1 issue" in RtlAuditClient().summarize(result)


def test_test_scenarios_has_more_than_twenty():
    text = (ROOT / "references" / "test-scenarios.md").read_text(encoding="utf-8")
    assert text.count("## Scenario") >= 20


def test_metadata_has_no_author_field():
    metadata = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    assert "author" not in metadata
    assert metadata["version"] == "2.2.0"


def test_license_uses_neutral_holder():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "The Authors" in text and "MIT License" in text


def test_no_hyphenated_client_script():
    assert not (ROOT / "scripts" / "rtl-ui-design-advisor-client.py").exists()
    assert (ROOT / "scripts" / "rtl_ui_design_advisor_client.py").exists()


def test_pyproject_installable_package_config():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'where = ["src"]' in text
    assert 'rtl-ui-design-advisor = "rtl_ui_design_advisor.cli:main"' in text


def test_public_markdown_has_no_emoji():
    public_md = [ROOT / "SKILL.md", ROOT / "SKILL_HE.md", ROOT / "README.md", ROOT / "CHANGELOG.md"]
    public_md.extend((ROOT / "references").glob("*.md"))
    emoji_re = re.compile(r"[\U0001F300-\U0001FAFF]")
    offenders = [str(path.relative_to(ROOT)) for path in public_md if emoji_re.search(path.read_text(encoding="utf-8"))]
    assert offenders == []


def test_hebrew_markdown_has_no_nikud():
    text = (ROOT / "SKILL_HE.md").read_text(encoding="utf-8")
    assert re.search(r"[\u0591-\u05BD\u05BF-\u05C7]", text) is None


def test_hebrew_replaced_common_anglicisms():
    text = (ROOT / "SKILL_HE.md").read_text(encoding="utf-8")
    forbidden = ["פרודקשן", "מובייל", "דסקטופ", "לוקליזציה", "קליינט", "דשבורד"]
    assert [term for term in forbidden if term in text] == []


def test_branding_audit_file_exists():
    assert (ROOT / "references" / "branding-audit.md").exists()


def test_cli_create_then_show_audit(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    create = subprocess.run(
        [
            sys.executable,
            "-m",
            "rtl_ui_design_advisor.cli",
            "create-audit",
            "--kind",
            "tailwind",
            "--text",
            "ml-4 text-left",
            "--store-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    audit_id = json.loads(create.stdout)["id"]
    show = subprocess.run(
        [
            sys.executable,
            "-m",
            "rtl_ui_design_advisor.cli",
            "show-audit",
            audit_id,
            "--store-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(show.stdout)["id"] == audit_id


def test_cli_date_command():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    result = subprocess.run(
        [sys.executable, "-m", "rtl_ui_design_advisor.cli", "date", "2026", "6", "3"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "03/06/2026"


def test_example_runs_with_env(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["RTL_ADVISOR_SAMPLE_CLASSES"] = "ml-4"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "examples" / "audit_tailwind_card.py"), "--env", "sandbox"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["env"] == "sandbox"
    assert payload["result"]["summary"]["total"] == 1


def test_public_method_count_at_least_twelve():
    import rtl_ui_design_advisor.client as client_module

    methods = [
        name for name, value in inspect.getmembers(client_module.RtlAuditClient, inspect.isfunction)
        if not name.startswith("_")
    ]
    assert len(methods) >= 12


def test_verification_log_summary_exists():
    text = (ROOT / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "| Total checks | 17 |" in text
    assert "| ✓✓ double-confirmed | 17 |" in text
    assert "| Final ✗ unconfirmed | 0 |" in text
