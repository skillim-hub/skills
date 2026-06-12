"""Command-line interface for the Israeli freelancer tax calculator."""

from __future__ import annotations

import json
from typing import Any

import click

from freelancer_tax_calculator import (
    CalculatorError,
    FreelancerTaxCalculator,
    FreelancerTaxInput,
    create_scenario,
    decimal_to_json,
    example_config as build_example_config,
    human_summary,
    load_config,
    load_environment_config,
    load_inputs,
    load_scenario,
    report_to_json,
    save_report,
)


def _merge_config(config_path: str | None, environment: str) -> Any:
    if config_path:
        return load_config(config_path)
    return load_environment_config(environment)


def _calculator(config_path: str | None = None, environment: str = "sandbox") -> FreelancerTaxCalculator:
    return FreelancerTaxCalculator(_merge_config(config_path, environment), environment=environment)


def _payload(
    business_type: str,
    revenue: str,
    expenses: str,
    input_vat: str,
    advance_rate: str,
    advance_base: str,
    micro_business: bool,
) -> FreelancerTaxInput:
    return FreelancerTaxInput(
        business_type=business_type,
        annual_revenue_ils=revenue,
        deductible_expenses_ils=expenses,
        input_vat_ils=input_vat,
        income_tax_advance_rate=advance_rate,
        income_tax_advance_base=advance_base,
        apply_micro_business_normative_expense=micro_business,
    )


common_env = click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
common_config = click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False), default=None, help="Optional JSON configuration path.")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Estimate Israeli freelancer VAT, advances, and National Insurance."""


@cli.command()
@click.option("--business-type", type=click.Choice(["osek-patur", "osek-murshe"]), required=True)
@click.option("--revenue", required=True, help="Revenue excluding VAT.")
@click.option("--expenses", default="0", show_default=True, help="Deductible expenses excluding VAT.")
@click.option("--input-vat", default="0", show_default=True, help="Eligible input VAT. Ignored for osek-patur.")
@click.option("--advance-rate", default="0", show_default=True, help="Income-tax advance rate as decimal, such as 0.08.")
@click.option("--advance-base", type=click.Choice(["revenue", "profit"]), default="revenue", show_default=True, help="Base for income-tax advances.")
@click.option("--micro-business/--no-micro-business", default=False, show_default=True, help="Apply eligible micro-business normative expense scenario.")
@common_config
@common_env
@click.option("--json", "json_output", is_flag=True, help="Print JSON instead of a human summary.")
def calculate(
    business_type: str,
    revenue: str,
    expenses: str,
    input_vat: str,
    advance_rate: str,
    advance_base: str,
    micro_business: bool,
    config_path: str | None,
    environment: str,
    json_output: bool,
) -> None:
    """Calculate a full annual estimate."""

    try:
        report = _calculator(config_path, environment).calculate(
            _payload(business_type, revenue, expenses, input_vat, advance_rate, advance_base, micro_business)
        )
    except CalculatorError as exc:
        raise click.ClickException(f"{exc.code}: {exc}") from exc
    click.echo(report_to_json(report) if json_output else human_summary(report))


@cli.command()
@click.option("--business-type", type=click.Choice(["osek-patur", "osek-murshe"]), required=True)
@click.option("--revenue", required=True, help="Period revenue excluding VAT.")
@click.option("--input-vat", default="0", show_default=True, help="Eligible input VAT for the period.")
@common_config
@common_env
@click.option("--json", "json_output", is_flag=True, help="Print JSON instead of a compact summary.")
def vat(business_type: str, revenue: str, input_vat: str, config_path: str | None, environment: str, json_output: bool) -> None:
    """Calculate a VAT-only period estimate."""

    try:
        report = _calculator(config_path, environment).calculate(
            FreelancerTaxInput(business_type=business_type, annual_revenue_ils=revenue, input_vat_ils=input_vat)
        )
    except CalculatorError as exc:
        raise click.ClickException(f"{exc.code}: {exc}") from exc
    if json_output:
        click.echo(json.dumps(decimal_to_json(report.vat), ensure_ascii=False, indent=2))
        return
    click.echo(f"Output VAT: ₪{report.vat.output_vat:,.2f}")
    click.echo(f"Input VAT credit: ₪{report.vat.input_vat_credit:,.2f}")
    click.echo(f"VAT payable: ₪{report.vat.vat_payable:,.2f}")
    click.echo(f"VAT refund position: ₪{report.vat.vat_refund_position:,.2f}")
    for warning in report.warnings:
        if "VAT" in warning or "patur" in warning or "ceiling" in warning:
            click.echo(f"Warning: {warning}")


@cli.command()
@click.option("--business-type", type=click.Choice(["osek-patur", "osek-murshe"]), required=True)
@click.option("--revenue", required=True, help="Revenue excluding VAT.")
@click.option("--expenses", default="0", show_default=True, help="Deductible expenses excluding VAT.")
@click.option("--input-vat", default="0", show_default=True, help="Eligible input VAT.")
@click.option("--advance-rate", default="0", show_default=True, help="Income-tax advance rate as decimal.")
@click.option("--advance-base", type=click.Choice(["revenue", "profit"]), default="revenue", show_default=True)
@click.option("--micro-business/--no-micro-business", default=False, show_default=True)
@click.option("--store-dir", type=click.Path(file_okay=False), default=None, help="Scenario store directory.")
@common_env
@click.option("--json", "json_output", is_flag=True, help="Print JSON create response.")
def create(
    business_type: str,
    revenue: str,
    expenses: str,
    input_vat: str,
    advance_rate: str,
    advance_base: str,
    micro_business: bool,
    store_dir: str | None,
    environment: str,
    json_output: bool,
) -> None:
    """Create a reusable scenario and return its ID."""

    try:
        record = create_scenario(
            _payload(business_type, revenue, expenses, input_vat, advance_rate, advance_base, micro_business),
            store_dir=store_dir,
            environment=environment,
        )
    except CalculatorError as exc:
        raise click.ClickException(f"{exc.code}: {exc}") from exc
    click.echo(json.dumps(record.to_dict(), ensure_ascii=False, indent=2) if json_output else record.scenario_id)


@cli.command()
@click.argument("scenario_id")
@click.option("--store-dir", type=click.Path(file_okay=False), default=None, help="Scenario store directory.")
@common_config
@common_env
@click.option("--json", "json_output", is_flag=True, help="Print JSON report.")
def run(scenario_id: str, store_dir: str | None, config_path: str | None, environment: str, json_output: bool) -> None:
    """Calculate a saved scenario by ID."""

    try:
        payload = load_scenario(scenario_id, store_dir=store_dir)
        report = _calculator(config_path, environment).calculate(payload)
    except CalculatorError as exc:
        raise click.ClickException(f"{exc.code}: {exc}") from exc
    click.echo(report_to_json(report) if json_output else human_summary(report))


@cli.command("from-json")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@common_config
@common_env
@click.option("--output", "output_path", type=click.Path(dir_okay=False), default=None, help="Optional report output path.")
def from_json(input_path: str, config_path: str | None, environment: str, output_path: str | None) -> None:
    """Calculate from an input JSON payload."""

    try:
        report = _calculator(config_path, environment).calculate(load_inputs(input_path))
    except CalculatorError as exc:
        raise click.ClickException(f"{exc.code}: {exc}") from exc
    if output_path:
        save_report(report, output_path)
        click.echo(output_path)
    else:
        click.echo(report_to_json(report))


@cli.command("example-config")
def example_config() -> None:
    """Print a default JSON configuration template."""

    click.echo(json.dumps(build_example_config(), ensure_ascii=False, indent=2))


def main() -> None:
    """Run the CLI entry point."""

    cli()


if __name__ == "__main__":
    main()
