from __future__ import annotations

import asyncio
import json
from decimal import Decimal

from click.testing import CliRunner
import pytest

from hebrew_copywriter import (
    AsyncHebrewCopywriterClient,
    BriefValidationError,
    Channel,
    CopyBrief,
    GenderMode,
    HebrewCopywriterClient,
    Register,
    brief_template,
)
import hebrew_copywriter_cli as cli_mod


def make_brief(**overrides):
    data = {
        "business_name": "סטודיו נועה",
        "business_type": "פילאטיס",
        "offer": "קבוצת בוקר קטנה",
        "audience": "נשים אחרי לידה",
        "channel": Channel.INSTAGRAM,
        "register": Register.WARM,
        "gender_mode": GenderMode.FEMININE,
        "price": Decimal("220"),
        "include_vat": True,
        "proof_points": ["עד 8 משתתפות", "מדריכה מוסמכת"],
    }
    data.update(overrides)
    return CopyBrief(**data)


def test_format_price_with_vat():
    c = HebrewCopywriterClient()
    assert c.format_price(Decimal("249"), True) == '₪249 כולל מע"מ'


def test_format_price_without_vat():
    c = HebrewCopywriterClient()
    assert c.format_price(Decimal("3800"), False) == '₪3,800 לא כולל מע"מ'


def test_price_with_vat_default_rate():
    c = HebrewCopywriterClient()
    assert c.price_with_vat(Decimal("100")) == Decimal("118.00")


def test_localize_iso_date():
    c = HebrewCopywriterClient()
    assert c.localize_date("2026-06-03") == "03/06/2026"


def test_localize_hyphen_local_date():
    c = HebrewCopywriterClient()
    assert c.localize_date("30-06-2026") == "30/06/2026"


def test_localize_slash_local_date():
    c = HebrewCopywriterClient()
    assert c.localize_date("30/06/2026") == "30/06/2026"


def test_validate_valid_brief_returns_list():
    c = HebrewCopywriterClient()
    assert isinstance(c.validate_brief(make_brief()), list)


def test_missing_required_field_raises():
    c = HebrewCopywriterClient()
    with pytest.raises(BriefValidationError):
        c.validate_brief(make_brief(offer=""))


def test_direct_marketing_warns_without_unsubscribe():
    c = HebrewCopywriterClient()
    brief = make_brief(channel=Channel.WHATSAPP, include_unsubscribe=False)
    warnings = c.validate_brief(brief)
    assert any("unsubscribe" in w for w in warnings)


def test_generate_landing_page_has_headline_body_cta():
    c = HebrewCopywriterClient()
    result = c.generate_copy(make_brief(channel=Channel.LANDING_PAGE))
    assert result["headline"]
    assert result["body"]
    assert result["cta"]


def test_generate_whatsapp_includes_unsubscribe_when_requested():
    c = HebrewCopywriterClient()
    brief = make_brief(channel=Channel.WHATSAPP, include_unsubscribe=True)
    result = c.generate_copy(brief)
    assert "להסרה" in result["text"]


def test_generate_sms_is_short():
    c = HebrewCopywriterClient()
    brief = make_brief(channel=Channel.SMS, include_unsubscribe=True)
    result = c.generate_copy(brief)
    assert len(result["text"]) <= 160


def test_google_ads_returns_headlines_and_descriptions():
    c = HebrewCopywriterClient()
    result = c.generate_copy(make_brief(channel=Channel.GOOGLE_ADS))
    assert len(result["headlines"]) == 3
    assert all(len(item) <= 31 for item in result["headlines"])
    assert len(result["descriptions"]) == 2


def test_prompt_contains_hebrew_instruction():
    c = HebrewCopywriterClient()
    prompt = c.build_prompt(make_brief())
    assert "עברית ישראלית" in prompt
    assert "DD/MM/YYYY" in prompt


def test_compliance_flags_guarantee():
    c = HebrewCopywriterClient()
    issues = c.compliance_check("מובטח 100% הצלחה")
    assert any("guarantee" in issue.lower() for issue in issues)


def test_compliance_flags_missing_unsubscribe():
    c = HebrewCopywriterClient()
    issues = c.compliance_check("מבצע מיוחד היום", Channel.SMS)
    assert any("unsubscribe" in issue.lower() for issue in issues)


def test_compliance_flags_iso_date():
    c = HebrewCopywriterClient()
    issues = c.compliance_check("המבצע עד 2026-06-03")
    assert any("DD/MM/YYYY" in issue for issue in issues)


def test_compliance_flags_hyphen_local_date():
    c = HebrewCopywriterClient()
    issues = c.compliance_check("המבצע עד 03-06-2026")
    assert any("DD/MM/YYYY" in issue for issue in issues)


def test_feminine_default_cta():
    c = HebrewCopywriterClient()
    assert c.default_cta(make_brief(gender_mode=GenderMode.FEMININE)) == "קבלי פרטים"


def test_masculine_default_cta():
    c = HebrewCopywriterClient()
    assert c.default_cta(make_brief(gender_mode=GenderMode.MASCULINE)) == "קבל פרטים"


def test_mixed_default_cta():
    c = HebrewCopywriterClient()
    assert c.default_cta(make_brief(gender_mode=GenderMode.MIXED)) == "בואו לבדוק התאמה"


def test_neutral_default_cta():
    c = HebrewCopywriterClient()
    assert c.default_cta(make_brief(gender_mode=GenderMode.NEUTRAL)) == "לקבלת פרטים"


def test_brief_json_round_trip():
    brief = make_brief()
    loaded = CopyBrief.from_mapping(json.loads(brief.to_json()))
    assert loaded.business_name == brief.business_name
    assert loaded.price == brief.price
    assert loaded.channel == brief.channel


def test_brief_template_is_loadable():
    template = brief_template()
    brief = CopyBrief.from_mapping(template)
    assert brief.business_name
    assert brief.channel == Channel.INSTAGRAM
    assert brief.deadline == "30/06/2026"


def test_generate_variants_count():
    c = HebrewCopywriterClient()
    variants = c.generate_variants(make_brief(), count=3)
    assert len(variants) == 3
    assert len({v["variant_register"] for v in variants}) == 3


@pytest.mark.asyncio
async def test_async_generate_copy():
    c = AsyncHebrewCopywriterClient()
    result = await c.generate_copy(make_brief())
    assert result["business_name"] == "סטודיו נועה"


def test_cli_brief_template():
    runner = CliRunner()
    result = runner.invoke(cli_mod.main, ["brief-template"])
    assert result.exit_code == 0
    assert "סטודיו נועה" in result.output


def test_cli_quick_json():
    runner = CliRunner()
    result = runner.invoke(
        cli_mod.main,
        [
            "quick",
            "--business-name", "סטודיו נועה",
            "--business-type", "פילאטיס",
            "--offer", "קבוצת בוקר",
            "--audience", "נשים",
            "--channel", "whatsapp",
            "--include-unsubscribe",
            "--format", "json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["channel"] == "whatsapp"
    assert "להסרה" in payload["text"]


def test_cli_check_flags_issue():
    runner = CliRunner()
    result = runner.invoke(cli_mod.main, ["check", "מובטח 100% הצלחה"])
    assert result.exit_code == 0
    assert "Unsupported" in result.output


def test_cli_generate_from_json_file(tmp_path):
    runner = CliRunner()
    brief_path = tmp_path / "brief.json"
    brief_path.write_text(make_brief().to_json(), encoding="utf-8")
    result = runner.invoke(cli_mod.main, ["generate", str(brief_path), "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["headline"]


def test_privacy_warning_for_lead_offer():
    c = HebrewCopywriterClient()
    warnings = c.validate_brief(make_brief(offer="טופס הרשמה לייעוץ"))
    assert any("privacy" in w.lower() for w in warnings)


def test_save_and_generate_id_chain(tmp_path):
    runner = CliRunner()
    store = tmp_path / "briefs"
    create = runner.invoke(
        cli_mod.main,
        [
            "create-brief",
            "--business-name", "סטודיו נועה",
            "--business-type", "פילאטיס",
            "--offer", "קבוצת בוקר",
            "--audience", "נשים",
            "--store-dir", str(store),
        ],
    )
    assert create.exit_code == 0
    response = json.loads(create.output)
    assert response["id"]
    generated = runner.invoke(cli_mod.main, ["generate-id", response["id"], "--store-dir", str(store), "--format", "json"])
    assert generated.exit_code == 0
    payload = json.loads(generated.output)
    assert payload["business_name"] == "סטודיו נועה"


def test_importable_package_module():
    import hebrew_copywriter

    assert hasattr(hebrew_copywriter, "HebrewCopywriterClient")


def test_example_script_outputs_json():
    import subprocess
    import sys
    from pathlib import Path

    path = Path(__file__).parent / "examples" / "retention_sms.py"
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(Path(__file__).parents[1])
    result = subprocess.run([sys.executable, str(path), "--env", "sandbox"], cwd=Path(__file__).parents[1], text=True, capture_output=True, env=env)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["env"] == "sandbox"
    assert payload["result"]["channel"] == "sms"


def test_verification_log_exists_and_summarizes_two_passes():
    from pathlib import Path

    root = Path(__file__).parents[1]
    log = (root / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "Pass 1 source" in log
    assert "Pass 2 source" in log
    assert "✓✓" in log
    assert "Total checks" in log


def test_metadata_version_bumped_to_v3_minor():
    import json
    from pathlib import Path

    root = Path(__file__).parents[1]
    metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["version"] == "2.2.0"
