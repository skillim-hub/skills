from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from real_estate_search import ClientError, Listing, RealEstateSearchClient, SearchCriteria
from real_estate_search.cli import app


@pytest.fixture()
def client() -> RealEstateSearchClient:
    return RealEstateSearchClient("sandbox")


def test_normalize_city_trims_spaces(client: RealEstateSearchClient) -> None:
    assert client.normalize_city("  תל אביב-יפו  ") == "תל אביב-יפו"


def test_normalize_city_rejects_blank(client: RealEstateSearchClient) -> None:
    with pytest.raises(ClientError):
        client.normalize_city("   ")


def test_normalize_neighborhoods_deduplicates(client: RealEstateSearchClient) -> None:
    assert client.normalize_neighborhoods("לב העיר, לב העיר | הצפון הישן") == ("לב העיר", "הצפון הישן")


def test_invalid_environment_rejected() -> None:
    with pytest.raises(ClientError):
        RealEstateSearchClient("staging")


def test_from_env_uses_defaults() -> None:
    client = RealEstateSearchClient.from_env({})
    assert client.environment == "sandbox"


def test_validate_price_range(client: RealEstateSearchClient) -> None:
    with pytest.raises(ClientError):
        client.normalize_criteria({"city": "חיפה", "min_price": 6000, "max_price": 5000})


def test_validate_room_range(client: RealEstateSearchClient) -> None:
    with pytest.raises(ClientError):
        client.normalize_criteria({"city": "חיפה", "min_rooms": 4, "max_rooms": 3})


def test_entry_date_accepts_israeli_format(client: RealEstateSearchClient) -> None:
    criteria = client.normalize_criteria({"city": "רמת גן", "entry_date": "15/07/2026"})
    assert criteria.entry_date == "2026-07-15"


def test_entry_date_rejects_invalid(client: RealEstateSearchClient) -> None:
    with pytest.raises(ClientError):
        client.normalize_criteria({"city": "רמת גן", "entry_date": "2026/07/15"})


def test_source_url_contains_yad2_domain(client: RealEstateSearchClient) -> None:
    url = client.build_source_url("yad2", {"city": "ירושלים", "max_price": 7500})
    assert "yad2.co.il" in url
    assert "max_price=7500" in url


def test_komo_url_uses_verified_city_path(client: RealEstateSearchClient) -> None:
    url = client.build_source_url("komo", {"city": "ירושלים", "neighborhoods": "בקעה"})
    assert "/code/nadlan/apartments-for-rent.asp" in url
    assert "cityName=%D7%99%D7%A8%D7%95%D7%A9%D7%9C%D7%99%D7%9D" in url
    assert "nehes=1" in url
    assert "neighborhood" not in url


def test_komo_rooms_use_verified_parameters(client: RealEstateSearchClient) -> None:
    url = client.build_source_url("komo", {"city": "חולון", "min_rooms": 3, "max_rooms": 3})
    assert "fromRooms=3" in url
    assert "toRooms=3" in url


def test_komo_commercial_rent_uses_commercial_property_code(client: RealEstateSearchClient) -> None:
    url = client.build_source_url("komo", {"city": "חיפה", "deal_type": "commercial_rent"})
    assert "nehes=28" in url


def test_yad2_commercial_uses_verified_commercial_path(client: RealEstateSearchClient) -> None:
    url = client.build_source_url("yad2", {"city": "חיפה", "deal_type": "commercial_rent"})
    assert "/realestate/commercial" in url


def test_madlan_commercial_uses_verified_path(client: RealEstateSearchClient) -> None:
    url = client.build_source_url("madlan", {"city": "חיפה", "deal_type": "commercial_rent"})
    assert "/commercial/for-rent" in url


def test_build_source_urls_default_three_sources(client: RealEstateSearchClient) -> None:
    links = client.build_source_urls({"city": "באר שבע"})
    assert [link.source for link in links] == ["yad2", "madlan", "komo"]


def test_build_source_urls_respects_source_filter(client: RealEstateSearchClient) -> None:
    links = client.build_source_urls({"city": "באר שבע", "sources": "madlan,komo"})
    assert [link.source for link in links] == ["madlan", "komo"]


def test_duplicate_sources_rejected(client: RealEstateSearchClient) -> None:
    with pytest.raises(ClientError):
        client.normalize_criteria({"city": "נתניה", "sources": "yad2,yad2"})


def test_plan_has_stable_id(client: RealEstateSearchClient) -> None:
    criteria = {"city": "חולון", "max_price": 5500}
    assert client.build_search_plan(criteria).plan_id == client.build_search_plan(criteria).plan_id


def test_plan_to_json_uses_hebrew(client: RealEstateSearchClient) -> None:
    payload = client.build_search_plan({"city": "חולון", "neighborhoods": "אגרובנק"}).to_json()
    assert "אגרובנק" in payload


def test_export_and_load_plan(tmp_path: Path, client: RealEstateSearchClient) -> None:
    plan = client.build_search_plan({"city": "חולון"})
    path = client.export_plan_json(plan, tmp_path / "plan.json")
    loaded = client.load_plan_json(path)
    assert loaded.plan_id == plan.plan_id


def test_summarize_plan_mentions_plan_id(client: RealEstateSearchClient) -> None:
    plan = client.build_search_plan({"city": "אשדוד", "max_price": 5000})
    assert plan.plan_id in client.summarize_plan(plan)


def test_review_checklist_sale_includes_land_registry(client: RealEstateSearchClient) -> None:
    checklist = client.build_review_checklist({"city": "הרצליה", "deal_type": "sale"})
    assert any("land registry" in item for item in checklist)


def test_review_checklist_commercial_includes_licensing(client: RealEstateSearchClient) -> None:
    checklist = client.build_review_checklist({"city": "הרצליה", "deal_type": "commercial_rent"})
    assert any("licensing" in item for item in checklist)


def test_parse_listing_map(client: RealEstateSearchClient) -> None:
    listing = client.parse_listing_map({"title": "דירה", "source": "yad2", "city": "חיפה", "price": "4200"})
    assert listing.price == 4200


def test_compare_listings_ranks_budget_match_first(client: RealEstateSearchClient) -> None:
    criteria = SearchCriteria(city="חיפה", max_price=5000, neighborhoods=("בת גלים",))
    listings = [
        Listing(title="יקרה", source="manual", city="חיפה", neighborhood="בת גלים", price=6200),
        Listing(title="מתאימה", source="manual", city="חיפה", neighborhood="בת גלים", price=4700),
    ]
    ranked = client.compare_listings(listings, criteria)
    assert ranked[0].listing.title == "מתאימה"


def test_rank_listings_returns_dicts(client: RealEstateSearchClient) -> None:
    ranked = client.rank_listings([{"title": "א", "city": "חיפה", "price": 4500}], {"city": "חיפה", "max_price": 5000})
    assert isinstance(ranked[0], dict)


def test_cost_estimate_first_month(client: RealEstateSearchClient) -> None:
    estimate = client.estimate_monthly_cash_needed({"title": "א", "city": "חיפה", "price": 5000}, 400, 250, 1, 2)
    assert estimate.first_month_cash_needed == 20650
    assert estimate.recurring_monthly_cost == 5650


@pytest.mark.asyncio
async def test_async_build_search_plan(client: RealEstateSearchClient) -> None:
    plan = await client.abuild_search_plan({"city": "מודיעין"})
    assert plan.criteria.city == "מודיעין"


@pytest.mark.asyncio
async def test_async_check_links_without_fetch(client: RealEstateSearchClient) -> None:
    plan = client.build_search_plan({"city": "מודיעין", "sources": "komo"})
    result = await client.async_check_links(plan.links)
    assert result[0]["checked"] is False


def test_cli_create_writes_file(tmp_path: Path) -> None:
    runner = CliRunner()
    output = tmp_path / "plan.json"
    result = runner.invoke(app, ["create", "--city", "חיפה", "--max-price", "5000", "--output", str(output)])
    assert result.exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["plan_id"].startswith("res-")


def test_cli_show_uses_plan_id(tmp_path: Path) -> None:
    runner = CliRunner()
    output = tmp_path / "plan.json"
    create = runner.invoke(app, ["create", "--city", "חיפה", "--output", str(output)])
    assert create.exit_code == 0
    plan_id = json.loads(output.read_text(encoding="utf-8"))["plan_id"]
    show = runner.invoke(app, ["show", "--file", str(output), "--plan-id", plan_id])
    assert show.exit_code == 0
    assert plan_id in show.output


def test_cli_links_outputs_json() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["links", "--city", "חיפה", "--neighborhoods", "בת גלים"])
    assert result.exit_code == 0
    assert "links" in json.loads(result.output)


def test_cli_compare_outputs_ranked_json(tmp_path: Path) -> None:
    runner = CliRunner()
    listings = tmp_path / "listings.json"
    listings.write_text(json.dumps([{"title": "א", "city": "חיפה", "price": 4500}], ensure_ascii=False), encoding="utf-8")
    result = runner.invoke(app, ["compare", "--listings", str(listings), "--city", "חיפה", "--max-price", "5000"])
    assert result.exit_code == 0
    assert json.loads(result.output)[0]["listing"]["title"] == "א"
