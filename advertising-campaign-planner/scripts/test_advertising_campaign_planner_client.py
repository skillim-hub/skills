from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from advertising_campaign_planner import CampaignPlanner, CampaignRequest, CURRENT_VAT_RATE, CURRENT_VAT_EFFECTIVE_DATE, campaign_request_from_mapping, load_plan


ROOT = Path(__file__).resolve().parent
CLI_PATH = ROOT / "advertising-campaign-planner-cli.py"


def make_request(**kwargs):
    data = dict(
        business="Local plumber",
        goal="calls",
        monthly_budget=3000,
        languages=["he"],
        cities=["Rishon LeZion"],
    )
    data.update(kwargs)
    return CampaignRequest(**data)


def test_valid_plan_contains_summary():
    plan = CampaignPlanner().plan(make_request())
    assert plan.campaign_summary["business"] == "Local plumber"
    assert plan.campaign_summary["budget"] == "₪3,000"
    assert plan.campaign_summary["plan_id"].startswith("plan_")


def test_budget_allocation_sums_to_budget():
    plan = CampaignPlanner().plan(make_request(monthly_budget=6000))
    assert sum(item.budget for item in plan.channel_mix) == 6000


def test_sales_budget_contains_catalog():
    plan = CampaignPlanner().plan(make_request(goal="sales", monthly_budget=10000, avg_order_value=200, gross_margin=0.5))
    assert any("catalog" in item.channel.lower() for item in plan.channel_mix)


def test_tiny_budget_warning():
    issues = CampaignPlanner().validate(make_request(monthly_budget=700))
    assert any(i.code == "TINY_BUDGET_FRAGMENTATION" for i in issues)


def test_invalid_budget_error():
    issues = CampaignPlanner().validate(make_request(monthly_budget=0))
    assert any(i.code == "INVALID_BUDGET" for i in issues)


def test_invalid_goal_error():
    issues = CampaignPlanner().validate(make_request(goal="viral"))
    assert any(i.code == "INVALID_GOAL" for i in issues)


def test_unsupported_language_error():
    issues = CampaignPlanner().validate(make_request(languages=["fr"]))
    assert any(i.code == "UNSUPPORTED_LANGUAGE" for i in issues)


def test_invalid_margin_error():
    issues = CampaignPlanner().validate(make_request(gross_margin=1.4))
    assert any(i.code == "INVALID_MARGIN" for i in issues)


def test_direct_message_warning():
    issues = CampaignPlanner().validate(make_request(uses_direct_messages=True))
    assert any(i.code == "DIRECT_MARKETING_CONSENT_REQUIRED" for i in issues)


def test_remarketing_warning():
    issues = CampaignPlanner().validate(make_request(uses_remarketing=True))
    assert any(i.code == "PRIVACY_NOTICE_REQUIRED" for i in issues)


def test_health_regulated_warning():
    issues = CampaignPlanner().validate(make_request(sector="health", regulated_flags=["health"]))
    assert any(i.code == "REGULATED_REVIEW_REQUIRED" for i in issues)


def test_guarantee_claim_warning():
    issues = CampaignPlanner().validate(make_request(offer="Guaranteed results"))
    assert any(i.code == "UNSUPPORTED_CLAIM_RISK" for i in issues)


def test_language_service_mismatch_warning():
    issues = CampaignPlanner().validate(make_request(languages=["he", "ru"], service_languages=["he"]))
    assert any(i.code == "NO_SERVICE_LANGUAGE" for i in issues)


def test_roi_positive():
    roi = CampaignPlanner().estimate_roi(spend=1000, clicks=500, conversions=20, avg_order_value=200, gross_margin=0.5)
    assert roi.gross_profit == 2000
    assert roi.roi == 1.0


def test_roi_rejects_bad_spend():
    with pytest.raises(ValueError):
        CampaignPlanner().estimate_roi(spend=0, clicks=1, conversions=1, avg_order_value=1, gross_margin=0.5)


def test_roi_rejects_bad_margin():
    with pytest.raises(ValueError):
        CampaignPlanner().estimate_roi(spend=1, clicks=1, conversions=1, avg_order_value=1, gross_margin=2)


def test_directional_roi_none_without_aov():
    plan = CampaignPlanner().plan(make_request(gross_margin=0.5))
    assert plan.roi_estimate is None


def test_directional_roi_exists_with_inputs():
    plan = CampaignPlanner().plan(make_request(avg_order_value=800, gross_margin=0.4))
    assert plan.roi_estimate is not None


def test_async_plan_matches_sync():
    planner = CampaignPlanner()
    req = make_request(avg_order_value=800, gross_margin=0.4)
    sync_plan = planner.plan(req).to_dict()
    async_plan = asyncio.run(planner.aplan(req)).to_dict()
    assert async_plan["campaign_summary"] == sync_plan["campaign_summary"]


def test_mapping_builder_accepts_aliases():
    req = campaign_request_from_mapping({"business": "Tutor", "goal": "leads", "budget": 1200, "language": ["he"], "city": "Tel Aviv"})
    assert req.monthly_budget == 1200
    assert req.cities == ["Tel Aviv"]


def test_format_ils():
    assert CampaignPlanner.format_ils(12345) == "₪12,345"


def test_plan_json_serializable():
    plan = CampaignPlanner().plan(make_request(avg_order_value=500, gross_margin=0.5))
    parsed = json.loads(plan.to_json())
    assert "launch_checklist" in parsed


def test_compliance_actions_include_accessibility():
    plan = CampaignPlanner().plan(make_request())
    assert any(flag.code == "ACCESSIBILITY_CHECK_REQUIRED" for flag in plan.compliance_flags)


def test_tax_claim_review_added():
    plan = CampaignPlanner().plan(make_request(regulated_flags=["tax_advice"]))
    assert any(flag.code == "TAX_CLAIM_REVIEW" for flag in plan.compliance_flags)


def test_environmental_review_added():
    plan = CampaignPlanner().plan(make_request(regulated_flags=["environmental"]))
    assert any(flag.code == "ENVIRONMENTAL_CLAIM_REVIEW" for flag in plan.compliance_flags)


def test_cli_roi_command_runs():
    result = subprocess.run(
        [sys.executable, str(CLI_PATH), "estimate-roi", "--spend", "1000", "--clicks", "500", "--conversions", "20", "--avg-order-value", "200", "--gross-margin", "0.5"],
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["roi"] == 1.0


def test_cli_template_hebrew_runs():
    result = subprocess.run([sys.executable, str(CLI_PATH), "template", "--language", "he"], text=True, capture_output=True, check=True)
    data = json.loads(result.stdout)
    assert data["date"] == "03/06/2026"
    assert "he" in data["languages"]


def test_cli_plan_command_runs():
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "plan",
            "--business",
            "רואה חשבון עצמאי",
            "--goal",
            "leads",
            "--monthly-budget",
            "6000",
            "--language",
            "he",
            "--language",
            "ru",
            "--city",
            "פתח תקווה",
            "--avg-order-value",
            "2400",
            "--gross-margin",
            "0.7",
            "--regulated-flag",
            "tax_advice",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["campaign_summary"]["budget"] == "₪6,000"
    assert any(flag["code"] == "TAX_CLAIM_REVIEW" for flag in data["compliance_flags"])


def test_cli_create_show_chain_runs(tmp_path):
    state_file = tmp_path / "planner-state.json"
    create = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "create",
            "--business",
            "Local tutor",
            "--goal",
            "leads",
            "--monthly-budget",
            "1500",
            "--language",
            "he",
            "--city",
            "Holon",
            "--state-file",
            str(state_file),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    created = json.loads(create.stdout)
    plan_id = created["plan_id"]
    assert plan_id.startswith("plan_")
    show = subprocess.run(
        [sys.executable, str(CLI_PATH), "show", "--plan-id", plan_id, "--state-file", str(state_file)],
        text=True,
        capture_output=True,
        check=True,
    )
    shown = json.loads(show.stdout)
    assert shown["campaign_summary"]["plan_id"] == plan_id
    assert load_plan(plan_id, state_file)["campaign_summary"]["business"] == "Local tutor"


def test_example_accepts_env_argument():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT.parent)
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "roi_estimator.py"), "--env", "sandbox"],
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT.parent,
        env=env,
    )
    data = json.loads(result.stdout)
    assert data["environment"] == "sandbox"


def test_current_vat_constant():
    assert CURRENT_VAT_RATE == 0.18
    assert CURRENT_VAT_EFFECTIVE_DATE == "01/01/2025"

def test_vat_note_in_launch_checklist():
    plan = CampaignPlanner().plan(make_request())
    assert any("18% VAT" in item for item in plan.launch_checklist)
