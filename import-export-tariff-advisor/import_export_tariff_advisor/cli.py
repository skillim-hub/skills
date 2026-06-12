"""Command-line interface for the Israeli import/export tariff advisor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from import_export_tariff_advisor import TariffAdvisorClient


app = typer.Typer(help="Estimate Israeli import customs duty, purchase tax, VAT, and landed cost.")


def _print_result(result, as_json: bool) -> None:
    if as_json:
        typer.echo(result.to_json(ensure_ascii=False, indent=2))
        return
    data = result.to_dict()
    typer.echo("Israeli import-tax estimate")
    if data.get("estimate_id"):
        typer.echo(f"Estimate ID: {data['estimate_id']}")
    typer.echo(f"Environment: {data['environment']}")
    typer.echo(f"Customs value: ₪{data['customs_value']:.2f}")
    typer.echo(f"Customs duty: ₪{data['customs_duty']:.2f}")
    typer.echo(f"Purchase tax: ₪{data['purchase_tax']:.2f}")
    typer.echo(f"VAT base: ₪{data['vat_base']:.2f}")
    typer.echo(f"VAT: ₪{data['vat']:.2f}")
    typer.echo(f"Total taxes: ₪{data['total_taxes']:.2f}")
    typer.echo(f"Non-tax fees: ₪{data['non_tax_fees']:.2f}")
    typer.echo(f"Landed cost: ₪{data['landed_cost']:.2f}")
    if data["warnings"]:
        typer.echo("\nWarnings:")
        for warning in data["warnings"]:
            typer.echo(f"- {warning}")


def _client(vat_rate: float = 0.18, store: Optional[Path] = None) -> TariffAdvisorClient:
    return TariffAdvisorClient(default_vat_rate=vat_rate, store_path=store)


@app.command()
def estimate(
    description: str = typer.Option(..., help="Product description."),
    goods_value: float = typer.Option(..., min=0, help="Goods value in the source currency."),
    shipping: float = typer.Option(0.0, min=0, help="International shipping in the source currency."),
    insurance: float = typer.Option(0.0, min=0, help="Insurance in the source currency."),
    currency: str = typer.Option("ILS", help="Label for the source currency."),
    exchange_rate_to_ils: float = typer.Option(1.0, min=0.000001, help="Exchange rate from source currency to ILS."),
    duty_rate: float = typer.Option(0.0, min=0, max=1, help="Customs duty rate as decimal, for example 0.12."),
    purchase_tax_rate: float = typer.Option(0.0, min=0, max=1, help="Purchase tax rate as decimal."),
    vat_rate: float = typer.Option(0.18, min=0, max=1, help="VAT rate as decimal."),
    taxable_fees_ils: float = typer.Option(0.0, min=0, help="Fees included in VAT base, already in ILS."),
    non_tax_fees_ils: float = typer.Option(0.0, min=0, help="Courier/broker fees not treated as government taxes, in ILS."),
    quantity: float = typer.Option(1.0, min=0.000001, help="Quantity."),
    tariff_code: Optional[str] = typer.Option(None, help="Israeli tariff code if known."),
    origin_country: Optional[str] = typer.Option(None, help="Country of origin."),
    importer_type: Optional[str] = typer.Option(None, help="Consumer, exempt dealer, licensed dealer, company, nonprofit."),
    use_type: Optional[str] = typer.Option(None, help="Personal, resale, internal business use, sample, repair."),
    estimate_date: Optional[str] = typer.Option(None, help="Estimate date, preferably DD/MM/YYYY for reports."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    """Estimate one line item."""
    _ = currency
    result = _client(vat_rate).estimate(
        description=description,
        goods_value=goods_value,
        shipping=shipping,
        insurance=insurance,
        exchange_rate_to_ils=exchange_rate_to_ils,
        duty_rate=duty_rate,
        purchase_tax_rate=purchase_tax_rate,
        vat_rate=vat_rate,
        taxable_fees_ils=taxable_fees_ils,
        non_tax_fees_ils=non_tax_fees_ils,
        quantity=quantity,
        tariff_code=tariff_code,
        origin_country=origin_country,
        importer_type=importer_type,
        use_type=use_type,
        estimate_date=estimate_date,
        environment=env,
    )
    _print_result(result, json_output)


@app.command()
def create(
    description: str = typer.Option(..., help="Product description."),
    goods_value: float = typer.Option(..., min=0, help="Goods value in the source currency."),
    shipping: float = typer.Option(0.0, min=0, help="International shipping in the source currency."),
    exchange_rate_to_ils: float = typer.Option(1.0, min=0.000001, help="Exchange rate from source currency to ILS."),
    duty_rate: float = typer.Option(0.0, min=0, max=1, help="Customs duty rate as decimal."),
    purchase_tax_rate: float = typer.Option(0.0, min=0, max=1, help="Purchase tax rate as decimal."),
    vat_rate: float = typer.Option(0.18, min=0, max=1, help="VAT rate as decimal."),
    store: Path = typer.Option(Path(".tariff-advisor-estimates.json"), help="Local JSON store path."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(True, "--json/--text", help="Emit JSON."),
) -> None:
    """Create and store an estimate with an identifier."""
    result = _client(vat_rate, store).create_estimate(
        description=description,
        goods_value=goods_value,
        shipping=shipping,
        exchange_rate_to_ils=exchange_rate_to_ils,
        duty_rate=duty_rate,
        purchase_tax_rate=purchase_tax_rate,
        vat_rate=vat_rate,
        environment=env,
    )
    _print_result(result, json_output)


@app.command()
def show(
    estimate_id: str = typer.Argument(..., help="Estimate ID returned by create."),
    store: Path = typer.Option(Path(".tariff-advisor-estimates.json"), help="Local JSON store path."),
    json_output: bool = typer.Option(True, "--json/--text", help="Emit JSON."),
) -> None:
    """Show a previously stored estimate."""
    result = _client(store=store).get_estimate(estimate_id)
    _print_result(result, json_output)


@app.command("from-json")
def from_json(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="JSON file with estimate input."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    """Estimate from a JSON file."""
    result = _client().estimate_from_json_file(path)
    _print_result(result, json_output)


@app.command()
def template(kind: str = typer.Argument("consumer")) -> None:
    """Print a runnable JSON input template."""
    templates = {
        "consumer": {
            "description": "Bluetooth headphones",
            "goods_value": 120,
            "shipping": 20,
            "insurance": 0,
            "exchange_rate_to_ils": 3.70,
            "duty_rate": 0,
            "purchase_tax_rate": 0,
            "vat_rate": 0.18,
            "non_tax_fees_ils": 35,
            "tariff_code": "8518300000",
            "use_type": "personal",
            "estimate_date": "15/04/2026",
            "environment": "sandbox",
        },
        "mixed": {
            "line_items": [
                {
                    "description": "Cotton T-shirts",
                    "goods_value": 500,
                    "shipping": 40,
                    "exchange_rate_to_ils": 3.70,
                    "duty_rate": 0.06,
                    "purchase_tax_rate": 0,
                    "vat_rate": 0.18,
                    "quantity": 50,
                    "use_type": "resale",
                    "environment": "sandbox",
                },
                {
                    "description": "Bluetooth power banks",
                    "goods_value": 800,
                    "shipping": 60,
                    "exchange_rate_to_ils": 3.70,
                    "duty_rate": 0,
                    "purchase_tax_rate": 0,
                    "vat_rate": 0.18,
                    "quantity": 20,
                    "use_type": "resale",
                    "environment": "sandbox",
                },
            ]
        },
    }
    if kind not in templates:
        raise typer.BadParameter(f"unknown template {kind!r}; choose one of: {', '.join(templates)}")
    typer.echo(json.dumps(templates[kind], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
