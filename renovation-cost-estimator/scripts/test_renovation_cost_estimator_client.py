from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from renovation_cost_estimator import (
    EstimatorError,
    LineItem,
    ProjectInput,
    RenovationCostEstimatorClient,
    format_ils,
    validate_environment,
)


def client(tmp_path: Path | None = None) -> RenovationCostEstimatorClient:
    return RenovationCostEstimatorClient(store_dir=tmp_path) if tmp_path else RenovationCostEstimatorClient()


def test_standard_apartment_estimate_has_vat() -> None:
    result = client().estimate({"city": "Ramat Gan", "area_sqm": 72, "scope_level": "partial", "finish_level": "standard", "bathrooms": 1, "kitchens": 1})
    assert result.totals["total_expected"] > result.totals["direct_expected"]
    assert any("VAT included" in item for item in result.assumptions)


def test_cosmetic_less_than_full() -> None:
    assert client().estimate({"city": "Haifa", "area_sqm": 55, "scope_level": "cosmetic", "finish_level": "basic"}).totals["total_expected"] < client().estimate({"city": "Haifa", "area_sqm": 55, "scope_level": "full", "finish_level": "basic"}).totals["total_expected"]


def test_premium_tel_aviv_wet_room() -> None:
    result = client().estimate({"city": "Tel Aviv", "area_sqm": 95, "scope_level": "full", "finish_level": "premium", "bathrooms": 2, "kitchens": 1})
    assert result.totals["direct_expected"] > 95 * 7000
    assert any(risk.topic == "wet rooms" for risk in result.risks)


def test_old_no_elevator_increases_cost() -> None:
    base = client().estimate({"city": "Holon", "area_sqm": 82, "scope_level": "partial", "finish_level": "standard", "building_year": 1995, "floor": 1, "has_elevator": True})
    risky = client().estimate({"city": "Holon", "area_sqm": 82, "scope_level": "partial", "finish_level": "standard", "building_year": 1975, "floor": 4, "has_elevator": False})
    assert risky.totals["total_expected"] > base.totals["total_expected"]
    assert any(risk.topic == "old building" for risk in risky.risks)


def test_occupied_note() -> None:
    result = client().estimate({"city": "Petah Tikva", "area_sqm": 70, "scope_level": "partial", "finish_level": "standard", "occupied": True})
    assert any("Occupied" in item for item in result.assumptions)
    assert any(risk.topic == "occupied work" for risk in result.risks)


def test_clinic_compliance_flags() -> None:
    result = client().estimate({"city": "Tel Aviv", "property_type": "clinic", "area_sqm": 38, "scope_level": "commercial_fitout", "finish_level": "standard", "requires_business_license": True, "commercial_public_access": True, "include_vat": False})
    topics = {risk.topic for risk in result.risks}
    assert {"business licensing", "accessibility", "fire safety"} <= topics
    assert result.totals["total_expected"] == result.totals["total_excluding_vat_expected"]


def test_shop_signage() -> None:
    result = client().estimate({"city": "Jerusalem", "property_type": "shop", "area_sqm": 42, "scope_level": "retail_fitout", "finish_level": "premium", "requires_business_license": True, "signage": True, "include_vat": False})
    assert any(risk.topic == "signage" for risk in result.risks)


def test_office_fitout() -> None:
    result = client().estimate({"city": "Bnei Brak", "property_type": "office", "area_sqm": 60, "scope_level": "office_fitout", "finish_level": "standard", "include_vat": False})
    assert result.totals["direct_expected"] >= 60 * 3500


def test_shell_higher() -> None:
    assert client().estimate({"city": "Netanya", "area_sqm": 95, "scope_level": "shell", "finish_level": "standard"}).totals["total_expected"] > client().estimate({"city": "Netanya", "area_sqm": 95, "scope_level": "partial", "finish_level": "standard"}).totals["total_expected"]


def test_bathroom_line_item() -> None:
    result = client().estimate({"city": "Rehovot", "area_sqm": 8, "scope_level": "partial", "finish_level": "standard", "line_items": [{"category": "bathroom_full", "quantity": 1}]})
    assert any(row["category"] == "bathroom_full" for row in result.line_breakdown)


def test_kitchen_line_item() -> None:
    result = client().estimate({"city": "Givatayim", "area_sqm": 12, "scope_level": "partial", "finish_level": "premium", "line_items": [{"category": "kitchen_full", "quantity": 1}]})
    assert any(row["category"] == "kitchen_full" for row in result.line_breakdown)


def test_trade_quantities() -> None:
    result = client().estimate({"city": "Rishon LeZion", "area_sqm": 80, "scope_level": "partial", "finish_level": "standard", "line_items": [{"category": "floor_tiling", "quantity": 80}, {"category": "electrical_point", "quantity": 45}, {"category": "paint", "quantity": 220}]})
    categories = {row["category"] for row in result.line_breakdown}
    assert {"floor_tiling", "electrical_point", "paint"} <= categories
    assert result.confidence == "concept"


def test_invalid_area() -> None:
    with pytest.raises(EstimatorError) as exc:
        client().estimate({"area_sqm": 0, "scope_level": "partial", "finish_level": "standard"})
    assert exc.value.code == "INVALID_AREA"


def test_unknown_finish() -> None:
    with pytest.raises(EstimatorError) as exc:
        client().estimate({"area_sqm": 60, "scope_level": "partial", "finish_level": "gold"})
    assert exc.value.code == "UNKNOWN_FINISH_LEVEL"


def test_unknown_scope() -> None:
    with pytest.raises(EstimatorError) as exc:
        client().estimate({"area_sqm": 60, "scope_level": "mega", "finish_level": "standard"})
    assert exc.value.code == "UNKNOWN_SCOPE_LEVEL"


def test_unknown_line() -> None:
    with pytest.raises(EstimatorError) as exc:
        client().estimate({"area_sqm": 60, "scope_level": "partial", "finish_level": "standard", "line_items": [{"category": "marble_dragon", "quantity": 1}]})
    assert exc.value.code == "UNKNOWN_LINE_ITEM"


def test_negative_quantity() -> None:
    with pytest.raises(EstimatorError) as exc:
        client().estimate({"area_sqm": 60, "scope_level": "partial", "finish_level": "standard", "line_items": [{"category": "paint", "quantity": -4}]})
    assert exc.value.code == "NEGATIVE_QUANTITY"


def test_custom_vat() -> None:
    result = client().estimate({"city": "Tel Aviv", "property_type": "office", "area_sqm": 45, "scope_level": "office_fitout", "finish_level": "standard", "vat_rate": 0.17, "include_vat": True})
    assert result.totals["vat_expected"] == round(result.totals["total_excluding_vat_expected"] * 0.17 / 100) * 100


def test_hebrew_output_uses_slashes() -> None:
    result = client().estimate({"project_name": "שיפוץ קליניקה", "city": "תל אביב", "property_type": "clinic", "area_sqm": 38, "scope_level": "commercial_fitout", "finish_level": "standard", "include_vat": False, "language": "he"})
    assert "/" in result.estimate_date
    assert "אומדן" in result.to_text(language="he")
    assert "₪" in result.to_text(language="he")


def test_food_business() -> None:
    result = client().estimate({"city": "Ashdod", "property_type": "shop", "area_sqm": 50, "scope_level": "retail_fitout", "finish_level": "standard", "food_business": True, "requires_business_license": True, "include_vat": False})
    assert any(risk.topic == "food business systems" for risk in result.risks)


def test_structural_risk() -> None:
    result = client().estimate({"city": "Jerusalem", "area_sqm": 90, "scope_level": "full", "finish_level": "standard", "building_year": 1965, "structural_changes": True})
    assert any(risk.topic == "structural work" for risk in result.risks)
    assert any("Structural changes" in item for item in result.assumptions)


def test_quote_review() -> None:
    result = client().estimate({"city": "Ramat Gan", "area_sqm": 80, "scope_level": "full", "finish_level": "standard", "contractor_quote_total": 300000, "contractor_quote_includes_vat": False})
    assert result.quote_review is not None
    assert result.quote_review["normalized_including_vat"] == 354000


@pytest.mark.asyncio
async def test_async_estimate() -> None:
    result = await client().estimate_async({"city": "Haifa", "area_sqm": 55, "scope_level": "cosmetic", "finish_level": "basic"})
    assert result.totals["total_expected"] > 0


def test_benchmarks_registry() -> None:
    data = client().benchmarks()
    assert "partial" in data["base_benchmarks"]
    assert "electrical_point" in data["line_item_rates"]


def test_format_ils() -> None:
    assert format_ils(123456) == "₪123,456"


def test_to_json_round_trip() -> None:
    data = json.loads(client().estimate({"city": "Haifa", "area_sqm": 55, "scope_level": "cosmetic", "finish_level": "basic"}).to_json())
    assert data["currency"] == "ILS"


def test_project_from_mapping_line_items() -> None:
    project = ProjectInput.from_mapping({"area_sqm": 1, "line_items": [{"category": "paint", "quantity": 2}]})
    assert isinstance(project.line_items[0], LineItem)
    assert project.line_items[0].quantity == 2


def test_create_project_and_estimate_by_id(tmp_path: Path) -> None:
    api = client(tmp_path)
    record = api.create_project({"city": "Tel Aviv", "area_sqm": 38, "scope_level": "commercial_fitout", "finish_level": "standard", "include_vat": False}, environment="sandbox")
    assert record.id.startswith("prj_")
    result = api.estimate_by_id(record.id, environment="sandbox")
    assert result.totals["total_expected"] > 0


def test_invalid_environment() -> None:
    with pytest.raises(EstimatorError) as exc:
        validate_environment("qa")
    assert exc.value.code == "INVALID_ENVIRONMENT"


def test_missing_project_id(tmp_path: Path) -> None:
    with pytest.raises(EstimatorError) as exc:
        client(tmp_path).estimate_by_id("prj_missing0000", environment="sandbox")
    assert exc.value.code == "PROJECT_NOT_FOUND"


def test_cli_scenario_runs() -> None:
    proc = subprocess.run([sys.executable, "-m", "renovation_cost_estimator.cli", "scenario", "clinic"], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Clinic" in proc.stdout


def test_cli_create_then_estimate(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["RENOVATION_ESTIMATOR_STORE"] = str(tmp_path)
    create = subprocess.run(
        [sys.executable, "-m", "renovation_cost_estimator.cli", "create", "--env", "sandbox", "--city", "Tel Aviv", "--area-sqm", "38", "--scope-level", "commercial_fitout", "--finish-level", "standard", "--no-include-vat"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert create.returncode == 0
    project_id = json.loads(create.stdout)["id"]
    estimate = subprocess.run([sys.executable, "-m", "renovation_cost_estimator.cli", "estimate", "--env", "sandbox", "--project-id", project_id, "--json"], capture_output=True, text=True, env=env)
    assert estimate.returncode == 0
    assert json.loads(estimate.stdout)["totals"]["total_expected"] > 0


def test_cli_invalid_area_returns_2() -> None:
    proc = subprocess.run([sys.executable, "-m", "renovation_cost_estimator.cli", "estimate", "--area-sqm", "0"], capture_output=True, text=True)
    assert proc.returncode == 2
    assert "INVALID_AREA" in proc.stderr


def test_verification_log_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    log = root / "references" / "verification-log.md"
    assert log.exists()
    text = log.read_text(encoding="utf-8")
    assert "✓✓" in text
    assert "✗→✓" in text
    assert "CBS" in text


def test_metadata_version_bumped() -> None:
    root = Path(__file__).resolve().parents[1]
    metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["version"] == "2.2.0"
    assert "author" not in metadata
