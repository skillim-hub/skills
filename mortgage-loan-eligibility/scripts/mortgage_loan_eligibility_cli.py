#!/usr/bin/env python3
"""Command-line interface for the local Israeli mortgage eligibility helper."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Optional

import typer

from mortgage_loan_eligibility_client import (
    DEFAULT_DSR_LIMIT,
    DEFAULT_DSR_REVIEW_THRESHOLD,
    DEFAULT_TERM_YEARS,
    MAX_TERM_YEARS,
    LTV_LIMITS,
    MortgageEligibilityClient,
)

app = typer.Typer(help="Calculate Israeli mortgage eligibility, LTV, payment, and DSR.")


def _env_key(env: str, key: str) -> str:
    return f"MLE_{env.upper()}_{key}"


def _env_float(env: str, key: str, fallback: float) -> float:
    raw = os.getenv(_env_key(env, key), os.getenv(f"MLE_{key}", ""))
    return fallback if raw == "" else float(raw)


def _env_int(env: str, key: str, fallback: int) -> int:
    raw = os.getenv(_env_key(env, key), os.getenv(f"MLE_{key}", ""))
    return fallback if raw == "" else int(raw)


def _client_for_env(env: str) -> MortgageEligibilityClient:
    return MortgageEligibilityClient(
        default_annual_rate=_env_float(env, "DEFAULT_ANNUAL_RATE", 0.0525),
        default_term_years=_env_int(env, "DEFAULT_TERM_YEARS", DEFAULT_TERM_YEARS),
        default_dsr_limit=_env_float(env, "DSR_LIMIT", DEFAULT_DSR_LIMIT),
    )


def _request_from_options(
    *,
    property_value: float,
    loan_amount: float,
    net_income: Optional[float],
    status: str,
    existing_debt: float,
    cash_equity: Optional[float],
    annual_rate: Optional[float],
    term_years: Optional[int],
    dsr_limit: Optional[float],
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "property_value": property_value,
        "requested_loan_amount": loan_amount,
        "property_status": status,
        "net_monthly_income": net_income,
        "existing_monthly_debt": existing_debt,
        "cash_equity": cash_equity,
    }
    if annual_rate is not None:
        request["annual_rate"] = annual_rate
    if term_years is not None:
        request["term_years"] = term_years
    if dsr_limit is not None:
        request["dsr_limit"] = dsr_limit
    return {key: value for key, value in request.items() if value is not None}


def _scenario_id(request: dict[str, Any]) -> str:
    canonical = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _read_scenario_store(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"scenarios": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"scenarios": data}
    if not isinstance(data, dict) or "scenarios" not in data:
        raise typer.BadParameter("scenario store must contain a scenarios array")
    return data


def _write_scenario_store(path: Path, store: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@app.command()
def calculate(
    property_value: float = typer.Option(..., help="Purchase price or accepted property value in ₪."),
    loan_amount: float = typer.Option(..., help="Requested mortgage amount in ₪."),
    net_income: Optional[float] = typer.Option(None, help="Net monthly household income in ₪."),
    status: str = typer.Option("single_home", help="single_home, replacement_home, or investment_property."),
    existing_debt: float = typer.Option(0.0, help="Existing monthly debt repayments in ₪."),
    cash_equity: Optional[float] = typer.Option(None, help="Verified available cash equity in ₪."),
    annual_rate: Optional[float] = typer.Option(None, help="Annual rate as 5.25 or 0.0525. Env default is used when omitted."),
    term_years: Optional[int] = typer.Option(None, help="Mortgage term in years. Env default is used when omitted."),
    dsr_limit: Optional[float] = typer.Option(None, help="Debt-service limit as 50 or 0.50. Env default is used when omitted."),
    env: str = typer.Option("sandbox", "--env", help="Environment defaults: sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Calculate one scenario from command-line options."""

    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    request = _request_from_options(
        property_value=property_value,
        loan_amount=loan_amount,
        net_income=net_income,
        status=status,
        existing_debt=existing_debt,
        cash_equity=cash_equity,
        annual_rate=annual_rate,
        term_years=term_years,
        dsr_limit=dsr_limit,
    )
    result = _client_for_env(env).calculate(request)
    if json_output:
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        raise typer.Exit()
    for line in result.summary_lines():
        typer.echo(line)
    if result.reasons:
        typer.echo("Reasons:")
        for item in result.reasons:
            typer.echo(f"- {item}")
    if result.warnings:
        typer.echo("Warnings:")
        for item in result.warnings:
            typer.echo(f"- {item}")
    if result.recommendations:
        typer.echo("Recommendations:")
        for item in result.recommendations:
            typer.echo(f"- {item}")


@app.command()
def create(
    output: Path = typer.Option(..., "--output", "-o", help="Scenario store path."),
    property_value: float = typer.Option(..., help="Purchase price or accepted property value in ₪."),
    loan_amount: float = typer.Option(..., help="Requested mortgage amount in ₪."),
    net_income: Optional[float] = typer.Option(None, help="Net monthly household income in ₪."),
    status: str = typer.Option("single_home", help="single_home, replacement_home, or investment_property."),
    existing_debt: float = typer.Option(0.0, help="Existing monthly debt repayments in ₪."),
    cash_equity: Optional[float] = typer.Option(None, help="Verified available cash equity in ₪."),
    annual_rate: Optional[float] = typer.Option(None, help="Annual rate as 5.25 or 0.0525."),
    term_years: Optional[int] = typer.Option(None, help="Mortgage term in years."),
    dsr_limit: Optional[float] = typer.Option(None, help="Debt-service limit as 50 or 0.50."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable create response."),
) -> None:
    """Create a reusable scenario and return its scenario_id."""

    request = _request_from_options(
        property_value=property_value,
        loan_amount=loan_amount,
        net_income=net_income,
        status=status,
        existing_debt=existing_debt,
        cash_equity=cash_equity,
        annual_rate=annual_rate,
        term_years=term_years,
        dsr_limit=dsr_limit,
    )
    scenario_id = _scenario_id(request)
    store = _read_scenario_store(output)
    scenarios = [item for item in store.get("scenarios", []) if item.get("scenario_id") != scenario_id]
    scenarios.append({"scenario_id": scenario_id, "request": request})
    store["scenarios"] = scenarios
    _write_scenario_store(output, store)
    response = {"scenario_id": scenario_id, "path": str(output), "created": True}
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2) if json_output else scenario_id)


@app.command()
def evaluate(
    input_path: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="Scenario store path."),
    scenario_id: str = typer.Option(..., "--scenario-id", help="Scenario id returned by create."),
    env: str = typer.Option("sandbox", "--env", help="Environment defaults: sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Evaluate one stored scenario by scenario_id."""

    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    store = _read_scenario_store(input_path)
    match = next((item for item in store.get("scenarios", []) if item.get("scenario_id") == scenario_id), None)
    if match is None:
        raise typer.BadParameter("scenario_id was not found in the scenario store")
    result = _client_for_env(env).calculate(match["request"])
    if json_output:
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        for line in result.summary_lines():
            typer.echo(line)


@app.command(name="from-file")
def from_file(
    path: Path = typer.Argument(..., exists=True, readable=True, help="JSON request file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional JSON result path."),
    env: str = typer.Option("sandbox", "--env", help="Environment defaults: sandbox or production."),
) -> None:
    """Calculate one scenario from a JSON request file."""

    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    data = json.loads(path.read_text(encoding="utf-8"))
    result = _client_for_env(env).calculate(data)
    payload = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    if output:
        output.write_text(payload + "\n", encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(payload)


@app.command()
def batch(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="JSON array of request objects."),
    output: Path = typer.Option(..., "--output", "-o", help="JSON array result file."),
    env: str = typer.Option("sandbox", "--env", help="Environment defaults: sandbox or production."),
) -> None:
    """Calculate many scenarios from a JSON array."""

    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    requests = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(requests, list):
        raise typer.BadParameter("input_path must contain a JSON array")
    client = _client_for_env(env)
    results = [client.calculate(item).to_dict() for item in requests]
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Wrote {len(results)} result(s) to {output}")


@app.command()
def sample(path: Path = typer.Option(Path("mortgage-request.sample.json"), help="Output sample request path.")) -> None:
    """Create a sample JSON request."""

    sample_request = {
        "property_value": 2400000,
        "requested_loan_amount": 1680000,
        "property_status": "single_home",
        "net_monthly_income": 28000,
        "existing_monthly_debt": 1500,
        "annual_rate": 5.25,
        "term_years": 25,
        "dsr_limit": 50,
        "dsr_review_threshold": 40,
        "cash_equity": 720000,
        "notes": ["Sample only; validate current lender policy before use."],
    }
    path.write_text(json.dumps(sample_request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Wrote {path}")


@app.command()
def explain() -> None:
    """Print supported statuses and default thresholds."""

    typer.echo("Property statuses:")
    for status_name, limit in LTV_LIMITS.items():
        typer.echo(f"- {status_name.value}: {limit:.0%} LTV cap")
    typer.echo(f"Default DSR limit: {DEFAULT_DSR_LIMIT:.0%}")
    typer.echo(f"Review threshold: {DEFAULT_DSR_REVIEW_THRESHOLD:.0%}")
    typer.echo(f"Maximum standard term: {MAX_TERM_YEARS} years")


def main() -> None:
    """Run the Typer application."""

    app()


if __name__ == "__main__":
    main()
