from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import click

from .client import EquityScenario, StockOptionsTaxAdvisorClient, normalize_environment, summarize_breakdown


def _scenario_kwargs(
    grant_type: str,
    track: str,
    quantity: float,
    sale_price: float,
    exercise_price: float,
    grant_date: Optional[str],
    sale_date: Optional[str],
    trustee_deposit_date: Optional[str],
    holding_period_anchor: str,
    other_income: float,
    fmv_at_grant: Optional[float],
    fmv_at_exercise: Optional[float],
    fmv_at_purchase: Optional[float],
    public_at_grant: bool,
    trustee_approved: bool,
    controlling_shareholder: bool,
    currency: str,
    fx_rate_to_ils: float,
) -> Dict[str, Any]:
    return {
        "grant_type": grant_type,
        "track": track,
        "quantity": quantity,
        "sale_price": sale_price,
        "exercise_price": exercise_price,
        "grant_date": grant_date,
        "sale_date": sale_date,
        "trustee_deposit_date": trustee_deposit_date,
        "holding_period_anchor": holding_period_anchor,
        "other_annual_income": other_income,
        "fmv_at_grant": fmv_at_grant,
        "fmv_at_exercise": fmv_at_exercise,
        "fmv_at_purchase": fmv_at_purchase,
        "public_at_grant": public_at_grant,
        "trustee_approved": trustee_approved,
        "is_controlling_shareholder": controlling_shareholder,
        "currency": currency,
        "fx_rate_to_ils": fx_rate_to_ils,
    }


def _environment_value(env: Optional[str]) -> str:
    return normalize_environment(env or os.getenv("STOCK_OPTIONS_TAX_ADVISOR_ENV", "sandbox"))


COMMON_OPTIONS = [
    click.option("--grant-type", type=click.Choice(["options", "rsu", "espp", "restricted_shares"]), required=True),
    click.option("--track", type=click.Choice(["102_capital", "102_income", "102_non_trustee", "3i", "non_employee", "unknown"]), required=True),
    click.option("--quantity", type=float, required=True),
    click.option("--sale-price", type=float, required=True),
    click.option("--exercise-price", type=float, default=0.0, show_default=True),
    click.option("--grant-date", type=str, default=None, help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    click.option("--sale-date", type=str, default=None, help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    click.option("--trustee-deposit-date", type=str, default=None, help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    click.option("--holding-period-anchor", type=click.Choice(["grant_year_end", "grant_date", "trustee_deposit_date"]), default="grant_year_end", show_default=True),
    click.option("--other-income", type=float, default=0.0, show_default=True),
    click.option("--fmv-at-grant", type=float, default=None),
    click.option("--fmv-at-exercise", type=float, default=None),
    click.option("--fmv-at-purchase", type=float, default=None),
    click.option("--public-at-grant", is_flag=True, default=False),
    click.option("--trustee-approved", is_flag=True, default=False),
    click.option("--controlling-shareholder", is_flag=True, default=False),
    click.option("--currency", type=str, default="ILS", show_default=True),
    click.option("--fx-rate-to-ils", type=float, default=1.0, show_default=True),
]


def add_common_options(func: Any) -> Any:
    for option in reversed(COMMON_OPTIONS):
        func = option(func)
    return func


@click.group()
def main() -> None:
    """Israeli stock options and equity tax planning CLI."""


@main.command()
@add_common_options
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default=None)
@click.option("--json-output", "--json", "json_output", is_flag=True, default=False)
def calculate(env_name: Optional[str], json_output: bool, **kwargs: Any) -> None:
    """Calculate one equity tax scenario."""
    scenario_data = _scenario_kwargs(**kwargs)
    client = StockOptionsTaxAdvisorClient(environment=_environment_value(env_name))
    try:
        scenario = EquityScenario.from_dict(scenario_data)
        result = client.calculate(scenario)
    except Exception as exc:
        if json_output:
            click.echo(json.dumps({"error": {"message": str(exc)}}, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps({"environment": client.environment, "scenario": scenario.to_dict(), "result": result.to_dict()}, ensure_ascii=False, indent=2))
    else:
        click.echo(summarize_breakdown(result))


@main.command()
@add_common_options
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default=None)
@click.option("--json-output", "--json", "json_output", is_flag=True, default=False)
def compare(env_name: Optional[str], json_output: bool, **kwargs: Any) -> None:
    """Compare Section 102 capital, income-track, and Section 3(i) scenarios."""
    scenario_data = _scenario_kwargs(**kwargs)
    client = StockOptionsTaxAdvisorClient(environment=_environment_value(env_name))
    try:
        scenario = EquityScenario.from_dict(scenario_data)
        results = client.compare_tracks(scenario)
    except Exception as exc:
        if json_output:
            click.echo(json.dumps({"error": {"message": str(exc)}}, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps({"environment": client.environment, "results": {name: result.to_dict() for name, result in results.items()}}, ensure_ascii=False, indent=2))
    else:
        for name, result in results.items():
            click.echo(f"\n=== {name} ===")
            click.echo(summarize_breakdown(result))


@main.command()
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default=None)
@click.option("--grant-date", required=True, help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")
@click.option("--sale-date", default=None, help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")
@click.option("--holding-period-anchor", type=click.Choice(["grant_year_end", "grant_date", "trustee_deposit_date"]), default="grant_year_end", show_default=True)
@click.option("--trustee-deposit-date", default=None, help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")
def eligibility(env_name: Optional[str], grant_date: str, sale_date: Optional[str], holding_period_anchor: str, trustee_deposit_date: Optional[str]) -> None:
    """Check preferred-treatment holding-period date."""
    client = StockOptionsTaxAdvisorClient(environment=_environment_value(env_name))
    scenario = EquityScenario.from_dict({
        "grant_type": "options",
        "track": "102_capital",
        "quantity": 1,
        "sale_price": 1,
        "grant_date": grant_date,
        "sale_date": sale_date,
        "trustee_deposit_date": trustee_deposit_date,
        "holding_period_anchor": holding_period_anchor,
        "trustee_approved": True,
    })
    preferred = client.earliest_preferred_sale_date(scenario)
    satisfied = client.holding_period_satisfied(scenario)
    click.echo(json.dumps({
        "environment": client.environment,
        "earliest_preferred_sale_date": preferred.isoformat() if preferred else None,
        "holding_period_satisfied": satisfied,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
