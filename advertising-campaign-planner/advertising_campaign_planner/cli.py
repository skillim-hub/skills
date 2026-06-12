"""Command-line interface for advertising campaign planning."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

import typer

from .client import CampaignPlanner, CampaignRequest, load_plan, save_plan

app = typer.Typer(help="Plan Israeli advertising campaigns with multilingual targeting, compliance checks, and ROI estimation.")


def _default_state_file() -> Path:
    return Path(os.environ.get("AD_PLANNER_STATE_FILE", ".ad-planner-state.json"))


def _write_or_echo(data: dict, output: Optional[Path]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(text)


def _request_from_options(
    business: str,
    goal: str,
    monthly_budget: float,
    language: List[str],
    city: List[str],
    sector: str,
    audience: str,
    offer: str,
    avg_order_value: Optional[float],
    gross_margin: Optional[float],
    regulated_flag: List[str],
    no_website: bool,
    uses_remarketing: bool,
    uses_direct_messages: bool,
    service_language: List[str],
    date: str,
    env: str,
) -> CampaignRequest:
    return CampaignRequest(
        business=business,
        goal=goal,
        monthly_budget=monthly_budget,
        languages=language,
        cities=city,
        sector=sector,
        audience=audience,
        offer=offer,
        avg_order_value=avg_order_value,
        gross_margin=gross_margin,
        regulated_flags=regulated_flag,
        has_website=not no_website,
        uses_remarketing=uses_remarketing,
        uses_direct_messages=uses_direct_messages,
        service_languages=service_language or None,
        date=date,
        environment=env,
    )


@app.command()
def plan(
    business: str = typer.Option(..., help="Business type or short business description."),
    goal: str = typer.Option("leads", help="leads, bookings, sales, calls, store_visits, or awareness."),
    monthly_budget: float = typer.Option(..., min=0.01, help="Monthly budget in ₪."),
    language: List[str] = typer.Option(["he"], "--language", "-l", help="Language code: he, ar, ru, en. Repeat for multiple."),
    city: List[str] = typer.Option([], "--city", "-c", help="Israeli city or region. Repeat for multiple."),
    sector: str = typer.Option("general", help="Sector, such as professional_services, health, finance, ecommerce."),
    audience: str = typer.Option("", help="Audience description."),
    offer: str = typer.Option("", help="Campaign offer or promotion."),
    avg_order_value: Optional[float] = typer.Option(None, help="Average order value in ₪."),
    gross_margin: Optional[float] = typer.Option(None, help="Gross margin as decimal, e.g. 0.55."),
    regulated_flag: List[str] = typer.Option([], "--regulated-flag", help="Regulated risk flag."),
    no_website: bool = typer.Option(False, help="Use when no campaign landing page exists."),
    uses_remarketing: bool = typer.Option(False, help="Flag remarketing/custom audience use."),
    uses_direct_messages: bool = typer.Option(False, help="Flag email/SMS/WhatsApp marketing follow-up."),
    service_language: List[str] = typer.Option([], "--service-language", help="Languages the business can actually serve."),
    date: str = typer.Option("03/06/2026", help="Plan date in DD/MM/YYYY."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write JSON plan to a file."),
) -> None:
    request = _request_from_options(business, goal, monthly_budget, language, city, sector, audience, offer, avg_order_value, gross_margin, regulated_flag, no_website, uses_remarketing, uses_direct_messages, service_language, date, env)
    _write_or_echo(CampaignPlanner().plan(request).to_dict(), output)


@app.command()
def create(
    business: str = typer.Option(...),
    goal: str = typer.Option("leads"),
    monthly_budget: float = typer.Option(..., min=0.01),
    language: List[str] = typer.Option(["he"], "--language", "-l"),
    city: List[str] = typer.Option([], "--city", "-c"),
    sector: str = typer.Option("general"),
    audience: str = typer.Option(""),
    offer: str = typer.Option(""),
    avg_order_value: Optional[float] = typer.Option(None),
    gross_margin: Optional[float] = typer.Option(None),
    regulated_flag: List[str] = typer.Option([], "--regulated-flag"),
    no_website: bool = typer.Option(False),
    uses_remarketing: bool = typer.Option(False),
    uses_direct_messages: bool = typer.Option(False),
    service_language: List[str] = typer.Option([], "--service-language"),
    date: str = typer.Option("03/06/2026"),
    env: str = typer.Option("sandbox", "--env"),
    state_file: Path = typer.Option(None, "--state-file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    state = state_file or _default_state_file()
    request = _request_from_options(business, goal, monthly_budget, language, city, sector, audience, offer, avg_order_value, gross_margin, regulated_flag, no_website, uses_remarketing, uses_direct_messages, service_language, date, env)
    plan_obj = CampaignPlanner().plan(request)
    plan_id = save_plan(plan_obj, state)
    payload = {"plan_id": plan_id, "state_file": str(state), "plan": plan_obj.to_dict()}
    _write_or_echo(payload, output)


@app.command()
def show(
    plan_id: str = typer.Option(..., "--plan-id"),
    state_file: Path = typer.Option(None, "--state-file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    state = state_file or _default_state_file()
    _write_or_echo(load_plan(plan_id, state), output)


@app.command("estimate-roi")
def estimate_roi(
    spend: float = typer.Option(..., min=0.01, help="Ad spend in ₪."),
    clicks: int = typer.Option(..., min=0, help="Number of clicks."),
    conversions: int = typer.Option(..., min=0, help="Number of conversions."),
    avg_order_value: float = typer.Option(..., min=0.01, help="Average order value in ₪."),
    gross_margin: float = typer.Option(..., min=0, max=1, help="Gross margin as decimal."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write JSON estimate to a file."),
) -> None:
    result = CampaignPlanner().estimate_roi(spend=spend, clicks=clicks, conversions=conversions, avg_order_value=avg_order_value, gross_margin=gross_margin)
    _write_or_echo(result.to_dict(), output)


@app.command()
def validate(
    business: str = typer.Option(...),
    goal: str = typer.Option("leads"),
    monthly_budget: float = typer.Option(...),
    language: List[str] = typer.Option(["he"], "--language", "-l"),
    regulated_flag: List[str] = typer.Option([], "--regulated-flag"),
    offer: str = typer.Option(""),
    uses_remarketing: bool = typer.Option(False),
    uses_direct_messages: bool = typer.Option(False),
    service_language: List[str] = typer.Option([], "--service-language"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    request = CampaignRequest(
        business=business,
        goal=goal,
        monthly_budget=monthly_budget,
        languages=language,
        regulated_flags=regulated_flag,
        offer=offer,
        uses_remarketing=uses_remarketing,
        uses_direct_messages=uses_direct_messages,
        service_languages=service_language or None,
    )
    issues = [issue.__dict__ for issue in CampaignPlanner().validate(request)]
    _write_or_echo({"issues": issues, "count": len(issues)}, output)


@app.command()
def template(
    language: str = typer.Option("en", help="Template language: en or he."),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    if language == "he":
        data = {
            "business": "רואה חשבון עצמאי",
            "goal": "leads",
            "monthly_budget": 6000,
            "avg_order_value": 2400,
            "gross_margin": 0.7,
            "languages": ["he", "ru"],
            "cities": ["פתח תקווה", "רמת גן"],
            "sector": "professional_services",
            "audience": "עצמאים ובעלי עסקים קטנים",
            "offer": "שיחת ייעוץ של 20 דקות ללא התחייבות",
            "regulated_flags": ["tax_advice"],
            "has_website": True,
            "uses_remarketing": True,
            "uses_direct_messages": False,
            "date": "03/06/2026",
            "environment": "sandbox",
        }
    else:
        data = {
            "business": "Family dental clinic",
            "goal": "bookings",
            "monthly_budget": 12000,
            "avg_order_value": 1800,
            "gross_margin": 0.62,
            "languages": ["he", "ar"],
            "cities": ["Haifa"],
            "sector": "health",
            "audience": "local families and comparison shoppers",
            "offer": "Initial consultation with transparent treatment plan",
            "regulated_flags": ["health"],
            "has_website": True,
            "uses_remarketing": False,
            "uses_direct_messages": False,
            "date": "03/06/2026",
            "environment": "sandbox",
        }
    _write_or_echo(data, output)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
