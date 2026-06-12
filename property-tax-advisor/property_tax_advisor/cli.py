#!/usr/bin/env python3
"""Command-line interface for the Israeli property-tax advisor helper."""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple

import click

from property_tax_advisor import client


def _emit(result: Any, json_output: bool) -> None:
    if hasattr(result, "to_dict"):
        data = result.to_dict()
    else:
        data = result
    if json_output:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                click.echo(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                click.echo(f"{key}: {value}")
    else:
        click.echo(str(data))


def _handle_error(exc: Exception, json_output: bool) -> None:
    if isinstance(exc, client.AdvisorError):
        payload = {"error": exc.to_dict()}
        if json_output:
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2), err=True)
        else:
            click.echo(f"{exc.code}: {exc.message}", err=True)
        raise click.exceptions.Exit(2)
    raise exc


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Israeli property-tax triage helper with sample calculations."""


@main.command()
@click.option("--municipalities", is_flag=True, help="List sample municipalities.")
@click.option("--discounts", "show_discounts", is_flag=True, help="List sample discount rules.")
@click.option("--json-output", is_flag=True, help="Print JSON.")
def rates(municipalities: bool, show_discounts: bool, json_output: bool) -> None:
    """Show sample municipalities or discounts."""
    data: Dict[str, Any] = {}
    if municipalities or not show_discounts:
        data["municipalities"] = client.list_municipalities()
    if show_discounts:
        data["discounts"] = client.list_discounts()
    _emit(data, json_output)


@main.command()
@click.option("--municipality", required=True, help="Municipality key or common alias.")
@click.option("--area", "area_sqm", required=True, type=float, help="Taxable area in sqm.")
@click.option("--zone", required=True, help="Tariff zone, such as A or B.")
@click.option("--usage", required=True, help="Usage, such as residential, office, commercial.")
@click.option("--months", default=2, show_default=True, type=int, help="Billing period in months.")
@click.option("--discount", default=None, help="Discount key, such as senior or new_immigrant.")
@click.option("--discount-months", default=None, type=int, help="Eligible discount months.")
@click.option("--json-output", is_flag=True, help="Print JSON.")
def arnona(
    municipality: str,
    area_sqm: float,
    zone: str,
    usage: str,
    months: int,
    discount: str | None,
    discount_months: int | None,
    json_output: bool,
) -> None:
    """Estimate Arnona with sample rates."""
    try:
        result = client.calculate_arnona(
            {
                "municipality": municipality,
                "area_sqm": area_sqm,
                "zone": zone,
                "usage": usage,
                "months": months,
                "discount": discount,
                "discount_months": discount_months,
            }
        )
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("home-office")
@click.option("--municipality", required=True)
@click.option("--zone", required=True)
@click.option("--total-area", required=True, type=float)
@click.option("--business-area", required=True, type=float)
@click.option("--business-usage", default="office", show_default=True)
@click.option("--json-output", is_flag=True)
def home_office(
    municipality: str,
    zone: str,
    total_area: float,
    business_area: float,
    business_usage: str,
    json_output: bool,
) -> None:
    """Compare all-residential, all-business, and split home-office scenarios."""
    try:
        result = client.compare_home_office_scenarios(
            municipality, zone, total_area, business_area, business_usage
        )
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("purchase-tax")
@click.option("--price", required=True, type=float, help="Purchase price in ILS.")
@click.option("--buyer-profile", default="single_home", show_default=True)
@click.option("--contract-date", default=None, help="DD/MM/YYYY. DD-MM-YYYY is also accepted.")
@click.option("--json-output", is_flag=True, help="Print JSON.")
def purchase_tax(price: float, buyer_profile: str, contract_date: str | None, json_output: bool) -> None:
    """Estimate purchase tax using sample brackets."""
    try:
        result = client.estimate_purchase_tax(price, buyer_profile, contract_date)
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("betterment-levy")
@click.option("--planning-uplift", required=True, type=float, help="Estimated planning uplift in ILS.")
@click.option("--ownership-share", default=1.0, show_default=True, type=float)
@click.option("--exemption", is_flag=True, help="Assume exemption applies.")
@click.option("--json-output", is_flag=True)
def betterment_levy(planning_uplift: float, ownership_share: float, exemption: bool, json_output: bool) -> None:
    """Estimate betterment levy exposure."""
    try:
        result = client.estimate_betterment_levy(planning_uplift, ownership_share, exemption)
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("mas-rechush")
@click.option("--property-kind", required=True, help="apartment, store, vehicle, equipment, land, etc.")
@click.option("--damage-type", default=None, help="war_direct, hostile_act, rocket, security_event, or none.")
@click.option("--incident-date", default=None, help="DD/MM/YYYY. DD-MM-YYYY is also accepted.")
@click.option("--json-output", is_flag=True)
def mas_rechush(property_kind: str, damage_type: str | None, incident_date: str | None, json_output: bool) -> None:
    """Route a Mas Rechush or compensation-fund question."""
    try:
        result = client.assess_mas_rechush(property_kind, damage_type, incident_date)
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("appeal-packet")
@click.option("--municipality", required=True)
@click.option("--property-number", required=True)
@click.option("--issue", "issues", multiple=True, required=True, help="Issue key. Repeat as needed.")
@click.option("--facts", default="")
@click.option("--json-output", is_flag=True)
def appeal_packet(municipality: str, property_number: str, issues: Tuple[str, ...], facts: str, json_output: bool) -> None:
    """Build an Arnona objection packet checklist."""
    try:
        result = client.build_appeal_packet(municipality, property_number, issues, facts)
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("case-create")
@click.option("--tax-type", required=True)
@click.option("--subject", required=True)
@click.option("--taxpayer-type", default="consumer", show_default=True)
@click.option("--env", "environment", default="sandbox", type=click.Choice(["sandbox", "production"]), show_default=True)
@click.option("--json-output", is_flag=True)
def case_create(tax_type: str, subject: str, taxpayer_type: str, environment: str, json_output: bool) -> None:
    """Create a local workflow case id for chaining commands."""
    try:
        result = client.create_case(tax_type, subject, taxpayer_type, environment)
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("case-next-steps")
@click.option("--case-id", required=True)
@click.option("--tax-type", required=True)
@click.option("--json-output", is_flag=True)
def case_next_steps(case_id: str, tax_type: str, json_output: bool) -> None:
    """Return next steps for a local workflow case id."""
    try:
        result = client.get_case_next_steps(case_id, tax_type)
        _emit(result, json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


@main.command("classify")
@click.argument("text")
@click.option("--json-output", is_flag=True)
def classify(text: str, json_output: bool) -> None:
    """Classify a free-text property-tax question."""
    result = client.classify_tax_question(text)
    _emit(result, json_output)


@main.command("validate-input")
@click.argument("json_payload")
@click.option("--json-output", is_flag=True)
def validate_input(json_payload: str, json_output: bool) -> None:
    """Validate an Arnona JSON payload and return a calculation."""
    try:
        payload = json.loads(json_payload)
        result = client.validate_arnona_payload(payload)
        _emit(result, json_output)
    except json.JSONDecodeError as exc:
        _handle_error(client.AdvisorError("INVALID_JSON", str(exc), "json_payload"), json_output)
    except Exception as exc:
        _handle_error(exc, json_output)


if __name__ == "__main__":
    main()
