from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "scripts" / "property-tax-advisor-cli.py"

import property_tax_advisor as client


def test_list_municipalities_contains_tel_aviv():
    assert "tel-aviv" in client.list_municipalities()


def test_normalize_hebrew_municipality():
    assert client.normalize_municipality("תל אביב") == "tel-aviv"


def test_get_rate_alias():
    rate = client.get_rate("tlv", "A", "residential")
    assert rate.annual_rate_per_sqm == 105.0


def test_calculate_arnona_basic_period():
    result = client.calculate_arnona(
        {"municipality": "tel-aviv", "area_sqm": 80, "zone": "A", "usage": "residential", "months": 2}
    )
    assert result.details["period_charge"] == 1400.0
    assert result.amount == 1400.0


def test_calculate_arnona_senior_discount():
    result = client.calculate_arnona(
        {
            "municipality": "tel-aviv",
            "area_sqm": 80,
            "zone": "A",
            "usage": "residential",
            "months": 2,
            "discount": "senior",
        }
    )
    assert result.details["discount_amount"] == 420.0
    assert result.details["payable"] == 980.0


def test_discount_area_cap():
    result = client.calculate_arnona(
        {
            "municipality": "tel-aviv",
            "area_sqm": 130,
            "zone": "A",
            "usage": "residential",
            "months": 2,
            "discount": "senior",
        }
    )
    assert result.details["discount"]["eligible_area_sqm"] == 100
    assert result.details["discount_amount"] == 525.0


def test_new_immigrant_discount_has_documents():
    result = client.calculate_arnona(
        {
            "municipality": "jerusalem",
            "area_sqm": 95,
            "zone": "B",
            "usage": "residential",
            "months": 12,
            "discount": "new_immigrant",
        }
    )
    assert "teudat oleh" in result.details["discount"]["required_documents"]


def test_invalid_area_raises():
    with pytest.raises(client.AdvisorError) as exc:
        client.calculate_arnona({"municipality": "tel-aviv", "area_sqm": 0, "zone": "A", "usage": "residential"})
    assert exc.value.code == "INVALID_AREA"


def test_invalid_months_raises():
    with pytest.raises(client.AdvisorError) as exc:
        client.calculate_arnona(
            {"municipality": "tel-aviv", "area_sqm": 80, "zone": "A", "usage": "residential", "months": 13}
        )
    assert exc.value.code == "INVALID_MONTHS"


def test_unknown_municipality_raises():
    with pytest.raises(client.AdvisorError) as exc:
        client.get_rate("unknown-city", "A", "residential")
    assert exc.value.code == "UNKNOWN_MUNICIPALITY"


def test_unknown_zone_raises():
    with pytest.raises(client.AdvisorError) as exc:
        client.get_rate("tel-aviv", "Z", "residential")
    assert exc.value.code == "UNKNOWN_ZONE"


def test_unknown_usage_raises():
    with pytest.raises(client.AdvisorError) as exc:
        client.get_rate("tel-aviv", "A", "clinic")
    assert exc.value.code == "UNKNOWN_USAGE"


def test_unknown_discount_raises():
    with pytest.raises(client.AdvisorError) as exc:
        client.calculate_arnona(
            {"municipality": "tel-aviv", "area_sqm": 80, "zone": "A", "usage": "residential", "discount": "fake"}
        )
    assert exc.value.code == "UNKNOWN_DISCOUNT"


def test_home_office_scenarios():
    result = client.compare_home_office_scenarios("jerusalem", "A", 72, 10, "office")
    assert result.details["all_residential"] == 6840.0
    assert result.details["all_business"] == 23760.0
    assert result.details["split_residential_business"] == 9190.0


def test_home_office_business_area_cannot_exceed_total():
    with pytest.raises(client.AdvisorError) as exc:
        client.compare_home_office_scenarios("jerusalem", "A", 10, 11)
    assert exc.value.code == "INVALID_AREA"


def test_marginal_tax_single_home_low_price():
    tax, rows = client.marginal_tax(1_000_000, client.SAMPLE_PURCHASE_TAX_BRACKETS["single_home"])
    assert tax == 0.0
    assert rows[0]["rate"] == 0.0


def test_purchase_tax_additional_home():
    result = client.estimate_purchase_tax(2_400_000, "additional_home", "15/03/2026")
    assert result.details["estimated_tax"] == 192000.0
    assert result.details["contract_date"] == "15/03/2026"


def test_purchase_tax_commercial_flat_rate():
    result = client.estimate_purchase_tax(1_000_000, "commercial_asset")
    assert result.amount == 60000.0


def test_purchase_tax_invalid_date():
    with pytest.raises(client.AdvisorError) as exc:
        client.estimate_purchase_tax(1_000_000, "single_home", "2026-03-15")
    assert exc.value.code == "DATE_FORMAT"


def test_purchase_tax_unknown_profile():
    with pytest.raises(client.AdvisorError) as exc:
        client.estimate_purchase_tax(1_000_000, "mystery")
    assert exc.value.code == "UNKNOWN_BUYER_PROFILE"


def test_betterment_levy_basic():
    result = client.estimate_betterment_levy(300_000)
    assert result.amount == 150000.0
    assert result.authority == "local_planning_committee"


def test_betterment_levy_share():
    result = client.estimate_betterment_levy(300_000, ownership_share=0.5)
    assert result.amount == 75000.0


def test_betterment_levy_exemption():
    result = client.estimate_betterment_levy(300_000, exemption=True)
    assert result.amount == 0.0


def test_betterment_invalid_share():
    with pytest.raises(client.AdvisorError) as exc:
        client.estimate_betterment_levy(100_000, ownership_share=1.5)
    assert exc.value.code == "INVALID_SHARE"


def test_mas_rechush_direct_damage():
    result = client.assess_mas_rechush("apartment", "war_direct", "15/03/2026")
    assert result.details["compensation_track_likely"] is True
    assert "Photograph damage" in result.next_actions[0]


def test_mas_rechush_no_damage_not_ordinary_tax():
    result = client.assess_mas_rechush("apartment")
    assert result.details["ordinary_annual_tax_expected"] is False


def test_appeal_packet_multiple_issues():
    packet = client.build_appeal_packet("tel aviv", "12345", ["wrong_area", "wrong_classification"])
    assert packet["municipality"] == "tel-aviv"
    assert "floor plan" in packet["evidence_checklist"]
    assert len(packet["issues"]) == 2


def test_unknown_appeal_issue():
    with pytest.raises(client.AdvisorError) as exc:
        client.build_appeal_packet("tel-aviv", "123", ["bad_issue"])
    assert exc.value.code == "UNKNOWN_APPEAL_ISSUE"


def test_classify_arnona_hebrew():
    result = client.classify_tax_question("קיבלתי חשבון ארנונה גבוה")
    assert result["tax_type"] == "arnona"


def test_classify_betterment_hebrew():
    result = client.classify_tax_question("הוועדה שלחה דרישה להיטל השבחה")
    assert result["tax_type"] == "betterment_levy"


def test_validate_payload_missing_field():
    with pytest.raises(client.AdvisorError) as exc:
        client.validate_arnona_payload({"municipality": "tel-aviv"})
    assert exc.value.code == "MISSING_FIELD"


def test_to_json_contains_hebrew():
    payload = {"term": "ארנונה"}
    assert "ארנונה" in client.to_json(payload)


def test_format_ils():
    assert client.format_ils(1234.5) == "₪1,234.50"


def test_round_money():
    assert client.round_money(10.005) == 10.01


def test_async_arnona_matches_sync():
    data = {"municipality": "haifa", "area_sqm": 90, "zone": "A", "usage": "residential"}
    sync_result = client.calculate_arnona(data).to_dict()
    async_result = asyncio.run(client.calculate_arnona_async(data)).to_dict()
    assert async_result == sync_result


def test_async_purchase_tax_matches_sync():
    sync_result = client.estimate_purchase_tax(2_400_000, "additional_home").to_dict()
    async_result = asyncio.run(client.estimate_purchase_tax_async(2_400_000, "additional_home")).to_dict()
    assert async_result == sync_result


def test_cli_rates_json():
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH), "rates", "--municipalities", "--json-output"],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(completed.stdout)
    assert "tel-aviv" in data["municipalities"]


def test_cli_arnona_json():
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "arnona",
            "--municipality",
            "tel-aviv",
            "--area",
            "80",
            "--zone",
            "A",
            "--usage",
            "residential",
            "--json-output",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(completed.stdout)
    assert data["details"]["payable"] == 1400.0


def test_cli_invalid_returns_code_2():
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "arnona",
            "--municipality",
            "tel-aviv",
            "--area",
            "-1",
            "--zone",
            "A",
            "--usage",
            "residential",
            "--json-output",
        ],
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 2
    assert "INVALID_AREA" in completed.stderr



def test_parse_local_date_accepts_slashes_and_hyphens():
    assert client.parse_local_date("15/03/2026").isoformat() == "2026-03-15"
    assert client.parse_local_date("15-03-2026").isoformat() == "2026-03-15"


def test_create_case_returns_chainable_id():
    result = client.create_case("arnona", "Tel Aviv bill area dispute", "small_business", "sandbox")
    assert result["case_id"].startswith("PTA-")
    assert "case-next-steps" in result["next_command"]


def test_get_case_next_steps_accepts_created_id():
    created = client.create_case("mas_rechush", "Rocket damage to shop")
    steps = client.get_case_next_steps(created["case_id"], created["tax_type"])
    assert steps["case_id"] == created["case_id"]
    assert any("Tax Authority" in step for step in steps["steps"])


def test_cli_case_chain(tmp_path):
    create = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "case-create",
            "--tax-type",
            "arnona",
            "--subject",
            "area dispute",
            "--json-output",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    case_id = json.loads(create.stdout)["case_id"]
    follow = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "case-next-steps",
            "--case-id",
            case_id,
            "--tax-type",
            "arnona",
            "--json-output",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert json.loads(follow.stdout)["case_id"] == case_id
