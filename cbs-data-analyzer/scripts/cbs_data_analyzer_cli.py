#!/usr/bin/env python3
"""Typer CLI for CBS data analysis workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from cbs_data_analyzer_client import (
    CBSDataAnalyzerClient,
    build_market_brief,
    calculate_indexation,
    format_nis,
)

app = typer.Typer(help="Fetch and analyze Israeli CBS data for planning workflows.")


def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _client_from_env(*, timeout: float = 30.0) -> CBSDataAnalyzerClient:
    """Create a client using optional environment overrides."""
    cbs_base_url = os.getenv("CBS_API_BASE_URL") or os.getenv("CBS_CBS_BASE_URL")
    data_gov_base_url = os.getenv("CBS_DATA_GOV_BASE_URL")
    kwargs: dict[str, object] = {"timeout": timeout}
    if cbs_base_url:
        kwargs["cbs_base_url"] = cbs_base_url
    if data_gov_base_url:
        kwargs["data_gov_base_url"] = data_gov_base_url
    return CBSDataAnalyzerClient(**kwargs)


@app.command("catalog-search")
def catalog_search(
    query: str = typer.Argument(..., help="Hebrew or English search text"),
    limit: int = typer.Option(10, min=1, max=50, help="Maximum matches to print"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON"),
    timeout: float = typer.Option(30.0, min=1.0, help="Request timeout in seconds"),
) -> None:
    """Search the CBS Price Indices catalog."""
    with _client_from_env(timeout=timeout) as client:
        matches = client.search_catalog(query)[:limit]

    if json_output:
        _echo_json(matches)
        return

    if not matches:
        typer.echo("No matching CBS index was found. Try Hebrew, English, or a known code.")
        raise typer.Exit(0)

    for item in matches:
        code = item.get("mainCode") or item.get("code") or ""
        name = item.get("chapterName") or item.get("name") or item.get("title") or ""
        typer.echo(f"{code}\t{name}")


@app.command("fetch-index")
def fetch_index(
    index_id: int = typer.Argument(..., help="CBS Price Indices mainCode, such as 120010"),
    limit: int = typer.Option(6, min=1, max=120, help="Number of recent points to print"),
    last: Optional[int] = typer.Option(None, "--last", min=1, help="Ask the CBS API for the last N observations"),
    start_period: Optional[str] = typer.Option(None, "--start-period", help="CBS startPeriod in mm-yyyy format"),
    end_period: Optional[str] = typer.Option(None, "--end-period", help="CBS endPeriod in mm-yyyy format"),
    coef: Optional[bool] = typer.Option(None, "--coef/--no-coef", help="Request CBS chaining coefficients when supported"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON"),
    csv_path: Optional[Path] = typer.Option(None, "--csv", help="Write normalized CSV"),
    timeout: float = typer.Option(30.0, min=1.0, help="Request timeout in seconds"),
) -> None:
    """Fetch a CBS price-index series."""
    with _client_from_env(timeout=timeout) as client:
        series = client.get_price_index(
            index_id,
            start_period=start_period,
            end_period=end_period,
            last=last,
            coef=coef,
        )
        if csv_path:
            client.export_series_csv(series, csv_path)

    if json_output:
        _echo_json(series.to_dict())
        return

    typer.echo(f"Series: {series.name} ({series.code})")
    typer.echo(f"Source: {series.source_url}")
    typer.echo(f"Retrieved: {series.retrieved_at}")
    typer.echo("Period\tValue\tMonthly %\tAnnual %")
    for point in series.recent(limit):
        typer.echo(f"{point.period}\t{point.value}\t{point.monthly_change}\t{point.annual_change}")

    if csv_path:
        typer.echo(f"CSV written: {csv_path}")


@app.command("latest")
def latest(
    index_id: int = typer.Argument(120010, help="CBS Price Indices mainCode"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON"),
    timeout: float = typer.Option(30.0, min=1.0, help="Request timeout in seconds"),
) -> None:
    """Show the latest point for an index."""
    with _client_from_env(timeout=timeout) as client:
        series = client.get_price_index(index_id, last=1)
    point = series.latest
    if point is None:
        typer.echo("No point was returned for this index.")
        raise typer.Exit(1)

    payload = {
        "series": series.name,
        "code": series.code,
        "period": point.period,
        "value": point.value,
        "monthly_change": point.monthly_change,
        "annual_change": point.annual_change,
        "source": series.source_url,
    }
    if json_output:
        _echo_json(payload)
    else:
        typer.echo(f"{payload['series']} ({payload['code']})")
        typer.echo(f"Period: {payload['period']}")
        typer.echo(f"Value: {payload['value']}")
        typer.echo(f"Monthly change: {payload['monthly_change']}")
        typer.echo(f"Annual change: {payload['annual_change']}")
        typer.echo(f"Source: {payload['source']}")


@app.command("indexation")
def indexation(
    amount: float = typer.Option(..., "--amount", min=0, help="Original amount in shekels"),
    base_index: float = typer.Option(..., "--base-index", min=0.0001, help="Base index value"),
    target_index: float = typer.Option(..., "--target-index", min=0.0001, help="Target index value"),
    floor_zero: bool = typer.Option(False, "--floor-zero", help="Do not reduce below original amount"),
    round_to_shekel: bool = typer.Option(False, "--round-shekel", help="Round final amount"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON"),
) -> None:
    """Calculate an index-linked amount."""
    result = calculate_indexation(
        original_amount=amount,
        base_index=base_index,
        target_index=target_index,
        floor_zero=floor_zero,
        round_to_shekel=round_to_shekel,
    )
    if json_output:
        _echo_json(result.to_dict())
        return

    typer.echo(f"Formula: {result.formula}")
    typer.echo(f"Original amount: {format_nis(result.original_amount)}")
    typer.echo(f"Adjusted amount: {format_nis(result.adjusted_amount)}")
    typer.echo(f"Difference: {format_nis(result.difference)}")
    typer.echo(f"Change: {result.percent_change:.2f}%")
    for note in result.notes:
        typer.echo(f"Note: {note}")


@app.command("data-gov-search")
def data_gov_search(
    query: str = typer.Argument(..., help="Dataset search query"),
    rows: int = typer.Option(10, min=1, max=100, help="Number of results"),
    organization: str = typer.Option("lamas", help="data.gov.il organization filter"),
    timeout: float = typer.Option(30.0, min=1.0, help="Request timeout in seconds"),
) -> None:
    """Search data.gov.il datasets, filtered to CBS by default."""
    with _client_from_env(timeout=timeout) as client:
        payload = client.search_data_gov(query, rows=rows, organization=organization)
    _echo_json(payload)


@app.command("business-brief")
def business_brief(
    question: str = typer.Option(..., help="Business question"),
    geography: str = typer.Option(..., help="Locality, district, or catchment area"),
    index_id: int = typer.Option(120010, help="Index used as price-pressure signal"),
    timeout: float = typer.Option(30.0, min=1.0, help="Request timeout in seconds"),
) -> None:
    """Build a small structured planning brief from an index series."""
    with _client_from_env(timeout=timeout) as client:
        series = client.get_price_index(index_id)
    _echo_json(build_market_brief(question=question, geography=geography, series=series))


def main() -> None:
    """Run the command-line application."""
    app()


if __name__ == "__main__":
    main()
