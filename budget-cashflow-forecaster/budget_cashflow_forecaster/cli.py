
"""Command line interface for the Budget & Cash-Flow Forecaster."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from .client import CashFlowForecaster, ForecastConfig, ForecastError, ForecastStore, compare_results, load_json, write_csv


def _print_rows(rows: list[Any]) -> None:
    headers = ["month", "opening", "in", "out", "reserved", "paid", "closing", "free", "status"]
    click.echo(" | ".join(headers))
    click.echo("-" * 92)
    for row in rows:
        data = row.as_dict()
        click.echo(
            f"{data['month']} | {data['opening_balance']:.2f} | {data['cash_in']:.2f} | "
            f"{data['cash_out']:.2f} | {data['tax_reserved']:.2f} | {data['tax_paid']:.2f} | "
            f"{data['closing_balance']:.2f} | {data['free_cash']:.2f} | {data['status']}"
        )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Forecast budget and cash flow from local JSON or CSV files."""


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", "-o", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--json-output", is_flag=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def forecast(input_file: Path, output: Path | None, json_output: bool, environment: str) -> None:
    """Run a forecast from a JSON input file."""
    try:
        result = CashFlowForecaster().forecast_from_json(input_file, environment=environment)  # type: ignore[arg-type]
        if output:
            write_csv(result, output)
            click.echo(f"Wrote {output}")
        if json_output:
            click.echo(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
        else:
            _print_rows(result.rows)
    except ForecastError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--store-dir", type=click.Path(file_okay=False, path_type=Path), default=".forecasts", show_default=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def create(input_file: Path, store_dir: Path, environment: str) -> None:
    """Create a saved forecast run and print its JSON response."""
    try:
        result = CashFlowForecaster().forecast_from_json(input_file, environment=environment)  # type: ignore[arg-type]
        ForecastStore(store_dir).save(result)
        click.echo(json.dumps({
            "id": result.forecast_id,
            "environment": result.environment,
            "store_dir": str(store_dir),
            "summary": result.summary,
            "warnings": result.warnings,
        }, ensure_ascii=False, indent=2))
    except ForecastError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("forecast_id")
@click.option("--store-dir", type=click.Path(file_okay=False, path_type=Path), default=".forecasts", show_default=True)
def show(forecast_id: str, store_dir: Path) -> None:
    """Show a saved forecast run by id."""
    try:
        click.echo(json.dumps(ForecastStore(store_dir).load(forecast_id), ensure_ascii=False, indent=2))
    except ForecastError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate a JSON forecast file."""
    try:
        ForecastConfig.from_mapping(load_json(input_file))
        click.echo("Validation passed")
    except ForecastError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("input_files", nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def compare(input_files: tuple[Path, ...], environment: str) -> None:
    """Compare two or more JSON scenario files."""
    if len(input_files) < 2:
        raise click.ClickException("Provide at least two scenario files")
    try:
        forecaster = CashFlowForecaster()
        results = {path.stem: forecaster.forecast_from_json(path, environment=environment) for path in input_files}  # type: ignore[arg-type]
        for row in compare_results(results):
            click.echo(
                f"{row['scenario']}: minimum closing={row['minimum_closing_balance']:.2f}, "
                f"minimum free={row['minimum_free_cash']:.2f}, first negative={row['first_negative_month']}"
            )
    except ForecastError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("from-csv")
@click.argument("csv_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--opening-balance", type=float, required=True)
@click.option("--start-month", type=str, required=True)
@click.option("--months", type=int, required=True)
@click.option("--buffer", type=float, default=0.0)
@click.option("--vat-rate", type=float, default=0.0)
@click.option("--vat-cadence", type=click.Choice(["none", "monthly", "bimonthly", "manual"]), default="none")
@click.option("--income-tax-advance-rate", type=float, default=0.0)
@click.option("--bituach-leumi-rate", type=float, default=0.0)
@click.option("--output", "-o", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def from_csv(
    csv_file: Path,
    opening_balance: float,
    start_month: str,
    months: int,
    buffer: float,
    vat_rate: float,
    vat_cadence: str,
    income_tax_advance_rate: float,
    bituach_leumi_rate: float,
    output: Path | None,
    environment: str,
) -> None:
    """Run a forecast from CSV transactions."""
    try:
        result = CashFlowForecaster().forecast_from_csv(
            csv_file,
            opening_balance=opening_balance,
            start_month=start_month,
            months=months,
            buffer=buffer,
            environment=environment,  # type: ignore[arg-type]
            tax_profile={
                "vat_rate": vat_rate,
                "vat_cadence": vat_cadence,
                "income_tax_advance_rate": income_tax_advance_rate,
                "bituach_leumi_rate": bituach_leumi_rate,
            },
        )
        if output:
            write_csv(result, output)
            click.echo(f"Wrote {output}")
        _print_rows(result.rows)
    except ForecastError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
