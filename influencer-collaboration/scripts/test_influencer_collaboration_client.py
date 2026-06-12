from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

import pytest

from influencer_collaboration_client import (
    DEFAULT_ISRAEL_VAT_EFFECTIVE_DATE,
    DEFAULT_ISRAEL_VAT_RATE,
    AsyncInfluencerCollaborationClient,
    CampaignBrief,
    CampaignMetric,
    CollaborationGoal,
    InfluencerCollaborationClient,
    InfluencerProfile,
    MarketSegment,
    Platform,
    brief_from_dict,
    build_campaign_plan,
    detect_market_segment,
    engagement_rate,
    estimate_creator_fee_ils,
    estimated_reach,
    generate_outreach_message,
    load_profiles_csv,
    normalize_handle,
    profile_from_dict,
    rank_influencers,
    read_json,
    safe_divide,
    score_influencer,
    summarize_campaign,
    validate_campaign_brief,
    validate_disclosure,
    validate_profile,
    write_json,
)


@pytest.fixture()
def profile() -> InfluencerProfile:
    return InfluencerProfile(
        handle="@haifa_food",
        display_name="דנה",
        platform=Platform.INSTAGRAM,
        niche="אוכל בחיפה",
        followers=20000,
        avg_views=9000,
        avg_likes=700,
        avg_comments=90,
        location="חיפה",
        audience_israel_pct=0.92,
        contact_email="creator@example.test",
    )


@pytest.fixture()
def brief() -> CampaignBrief:
    return CampaignBrief(
        business_name="קפה שכונתי",
        product_or_service="תפריט בוקר",
        goal=CollaborationGoal.FOOT_TRAFFIC,
        target_locations=["חיפה"],
        target_segments=[MarketSegment.FOOD],
        budget_ils=6000,
        start_date=date(2026, 6, 10),
        end_date=date(2026, 6, 20),
        deliverables=["reel", "story"],
        coupon_code="HAIFA10",
    )


def test_normalize_handle_strips_at_and_url() -> None:
    assert normalize_handle("https://instagram.com/@abc/") == "abc"


def test_normalize_handle_rejects_empty() -> None:
    with pytest.raises(ValueError):
        normalize_handle("  ")


def test_safe_divide_zero() -> None:
    assert safe_divide(10, 0) == 0


def test_detect_market_segment_hebrew_food() -> None:
    assert detect_market_segment("מסעדה חדשה וקפה") == MarketSegment.FOOD


def test_detect_market_segment_hebrew_fitness() -> None:
    assert detect_market_segment("סטודיו כושר ופילאטיס") == MarketSegment.FITNESS


def test_engagement_rate(profile: InfluencerProfile) -> None:
    assert round(engagement_rate(profile), 4) == 0.0395


def test_estimated_reach(profile: InfluencerProfile) -> None:
    assert estimated_reach(profile) == 8280


def test_estimate_creator_fee_positive(profile: InfluencerProfile) -> None:
    assert estimate_creator_fee_ils(profile, ["reel"]) > 350


def test_validate_profile_catches_bad_pct(profile: InfluencerProfile) -> None:
    bad = InfluencerProfile(**{**profile.__dict__, "audience_israel_pct": 2})
    assert "audience_israel_pct must be between 0 and 1" in validate_profile(bad)


def test_validate_campaign_brief_bad_dates(brief: CampaignBrief) -> None:
    bad = CampaignBrief(**{**brief.__dict__, "start_date": date(2026, 7, 1), "end_date": date(2026, 6, 1)})
    assert "end_date must be on or after start_date" in validate_campaign_brief(bad)


def test_score_influencer_shortlists_good_fit(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    score = score_influencer(profile, brief)
    assert score.recommendation == "shortlist"
    assert score.total_score >= 80


def test_score_influencer_budget_penalty(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    tiny = CampaignBrief(**{**brief.__dict__, "budget_ils": 100})
    score = score_influencer(profile, tiny)
    assert score.budget_score < 100


def test_rank_influencers_orders_by_score(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    weak = InfluencerProfile("weak", "חלש", Platform.TIKTOK, "גיימינג", 50000, 1000, 50, 2, "לונדון", 0.12)
    ranked = rank_influencers([weak, profile], brief)
    assert ranked[0].handle == "haifa_food"


def test_validate_disclosure_accepts_clear_hebrew() -> None:
    ok, issues = validate_disclosure("פרסומת בשיתוף עסק מקומי")
    assert ok is True
    assert issues == []


def test_validate_disclosure_rejects_missing() -> None:
    ok, issues = validate_disclosure("קבלו הטבה מיוחדת היום")
    assert ok is False
    assert "missing clear commercial disclosure" in issues


def test_validate_disclosure_flags_late() -> None:
    text = "טקסט " * 25 + " פרסומת"
    ok, issues = validate_disclosure(text)
    assert ok is False
    assert "disclosure appears too late" in issues


def test_generate_outreach_contains_dates_and_shekel(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    message = generate_outreach_message(profile, brief)
    assert "10/06/2026" in message.body
    assert "₪" in message.body
    assert message.language == "he"


def test_build_campaign_plan_contains_checklist(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    plan = build_campaign_plan([profile], brief)
    assert plan["shortlist"]
    assert "confirm commercial disclosure wording" in plan["checklist"]


def test_build_campaign_plan_empty_for_skip(brief: CampaignBrief) -> None:
    weak = InfluencerProfile("weak", "חלש", Platform.TIKTOK, "גיימינג", 50000, 1000, 50, 2, "לונדון", 0.12)
    plan = build_campaign_plan([weak], brief)
    assert isinstance(plan["shortlist"], list)


def test_build_campaign_plan_rejects_zero_max(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    with pytest.raises(ValueError):
        build_campaign_plan([profile], brief, max_creators=0)


def test_summarize_campaign_calculates_roas() -> None:
    metrics = [CampaignMetric("a", 1000, 10000, 5000, 200, 40, 10, 2500, date(2026, 1, 1))]
    summary = summarize_campaign(metrics)
    assert summary.roas == 2.5
    assert summary.cpm_ils == 100


def test_summarize_campaign_handles_zero_values() -> None:
    summary = summarize_campaign([])
    assert summary.cpc_ils == 0
    assert summary.recommendations


def test_profile_from_dict_defaults() -> None:
    profile = profile_from_dict({"handle": "x", "niche": "tech"})
    assert profile.display_name == "x"
    assert profile.platform == Platform.INSTAGRAM


def test_brief_from_dict_parses_localized_date() -> None:
    brief = brief_from_dict(
        {
            "business_name": "עסק",
            "product_or_service": "שירות",
            "goal": "leads",
            "target_locations": ["ירושלים"],
            "target_segments": ["local_services"],
            "budget_ils": 1000,
            "start_date": "01/07/2026",
            "end_date": "10/07/2026",
        }
    )
    assert brief.start_date == date(2026, 7, 1)


def test_json_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "x.json"
    write_json(path, {"name": "עברית"})
    assert read_json(path)["name"] == "עברית"


def test_load_profiles_csv(tmp_path: Path) -> None:
    path = tmp_path / "profiles.csv"
    path.write_text(
        "handle,display_name,platform,niche,followers,avg_views,avg_likes,avg_comments,location,audience_israel_pct\n"
        "x,שם,instagram,אוכל,1000,500,40,5,חיפה,0.8\n",
        encoding="utf-8",
    )
    profiles = load_profiles_csv(path)
    assert profiles[0].display_name == "שם"


def test_sync_client_methods(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    client = InfluencerCollaborationClient()
    assert client.score_profile(profile, brief).handle == "haifa_food"
    assert client.estimate_fee(profile) > 0
    assert client.generate_outreach(profile, brief).subject
    assert client.validate_disclosure("פרסומת: בדיקה")[0]
    assert client.build_plan([profile], brief)["shortlist"]
    assert client.summarize_metrics([]).spend_ils == 0


@pytest.mark.asyncio
async def test_async_score(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    client = AsyncInfluencerCollaborationClient()
    score = await client.score_profile(profile, brief)
    assert score.handle == "haifa_food"


@pytest.mark.asyncio
async def test_async_rank(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    client = AsyncInfluencerCollaborationClient()
    ranked = await client.rank_profiles([profile], brief)
    assert ranked[0].handle == "haifa_food"


@pytest.mark.asyncio
async def test_async_estimate(profile: InfluencerProfile) -> None:
    client = AsyncInfluencerCollaborationClient()
    fee = await client.estimate_fee(profile)
    assert fee > 0


@pytest.mark.asyncio
async def test_async_outreach(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    client = AsyncInfluencerCollaborationClient()
    message = await client.generate_outreach(profile, brief)
    assert "קפה שכונתי" in message.subject


@pytest.mark.asyncio
async def test_async_disclosure() -> None:
    client = AsyncInfluencerCollaborationClient()
    ok, issues = await client.validate_disclosure("פרסומת בשיתוף עסק")
    assert ok
    assert issues == []


@pytest.mark.asyncio
async def test_async_plan(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    client = AsyncInfluencerCollaborationClient()
    plan = await client.build_plan([profile], brief)
    assert plan["shortlist"]


@pytest.mark.asyncio
async def test_async_summary() -> None:
    client = AsyncInfluencerCollaborationClient()
    summary = await client.summarize_metrics([])
    assert summary.spend_ils == 0


def test_asdict_score_is_json_serializable(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    payload = json.dumps(asdict(score_influencer(profile, brief)), ensure_ascii=False, default=str)
    assert "haifa_food" in payload


def test_value_error_for_invalid_scoring(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    bad = InfluencerProfile(**{**profile.__dict__, "followers": -1})
    with pytest.raises(ValueError):
        score_influencer(bad, brief)


def test_low_israel_audience_reduces_score(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    low = InfluencerProfile(**{**profile.__dict__, "audience_israel_pct": 0.2})
    assert score_influencer(low, brief).israel_relevance_score == 20


def test_conflicts_reduce_risk(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    conflict = InfluencerProfile(**{**profile.__dict__, "past_brand_conflicts": ("מתחרה",)})
    assert score_influencer(conflict, brief).risk_score < score_influencer(profile, brief).risk_score


def test_deliverables_increase_fee(profile: InfluencerProfile) -> None:
    one = estimate_creator_fee_ils(profile, ["story"])
    three = estimate_creator_fee_ils(profile, ["story", "reel", "post"])
    assert three > one


def test_verified_vat_planning_constants():
    assert DEFAULT_ISRAEL_VAT_RATE == 0.18
    assert DEFAULT_ISRAEL_VAT_EFFECTIVE_DATE.isoformat() == "2025-01-01"


def test_outreach_uses_correct_hebrew_vat_acronym(profile: InfluencerProfile, brief: CampaignBrief) -> None:
    message = generate_outreach_message(profile, brief)
    assert 'מע"מ' in message.body
    assert "מעמ" not in message.body
