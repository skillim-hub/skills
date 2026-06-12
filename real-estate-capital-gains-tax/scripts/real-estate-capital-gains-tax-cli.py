"""Command-line interface for the Mas Shevach helper."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from real_estate_capital_gains_tax import (
    TaxInputs,
    create_case as create_case_record,
    estimate_case as estimate_saved_case,
    estimate_tax,
    summarize,
)

app = typer.Typer(help="Estimate Israeli Mas Shevach for real-estate sales.")


def _input_payload(
    purchase_date: str,
    sale_date: str,
    purchase_price: float,
    sale_price: float,
    purchase_costs: float,
    sale_costs: float,
    improvements: float,
    depreciation_claimed: float,
    ownership_share: float,
    property_type: str,
    qualifying_residential: bool,
    seller_residency: str,
    seller_type: str,
    cpi_purchase: Optional[float],
    cpi_sale: Optional[float],
    linear_relief_start_date: str,
    tax_rate: float,
    exemption_code: Optional[str],
    notes: str,
) -> TaxInputs:
    return TaxInputs.from_dict({
        "purchase_date": purchase_date,
        "sale_date": sale_date,
        "purchase_price": purchase_price,
        "sale_price": sale_price,
        "purchase_costs": purchase_costs,
        "sale_costs": sale_costs,
        "improvements": improvements,
        "depreciation_claimed": depreciation_claimed,
        "ownership_share": ownership_share,
        "property_type": property_type,
        "is_qualifying_residential_apartment": qualifying_residential,
        "seller_residency": seller_residency,
        "seller_type": seller_type,
        "cpi_purchase": cpi_purchase,
        "cpi_sale": cpi_sale,
        "linear_relief_start_date": linear_relief_start_date,
        "tax_rate": tax_rate,
        "exemption_code": exemption_code,
        "notes": notes,
    })


def _common_options(
    purchase_date: str = typer.Option(..., help="Purchase date, YYYY-MM-DD or DD/MM/YYYY."),
    sale_date: str = typer.Option(..., help="Sale date, YYYY-MM-DD or DD/MM/YYYY."),
    purchase_price: float = typer.Option(..., min=0.0, help="Purchase price in NIS."),
    sale_price: float = typer.Option(..., min=0.0, help="Sale price in NIS."),
    purchase_costs: float = typer.Option(0.0, min=0.0, help="Purchase-related deductible costs."),
    sale_costs: float = typer.Option(0.0, min=0.0, help="Sale-related deductible costs."),
    improvements: float = typer.Option(0.0, min=0.0, help="Capital improvements."),
    depreciation_claimed: float = typer.Option(0.0, min=0.0, help="Depreciation claimed or claimable."),
    ownership_share: float = typer.Option(1.0, min=0.000001, max=1.0, help="Seller ownership fraction."),
    property_type: str = typer.Option("residential_apartment", help="residential_apartment, land, commercial, mixed_use, other."),
    qualifying_residential: bool = typer.Option(False, "--qualifying-residential", help="Treat as qualifying residential apartment for linear allocation."),
    seller_residency: str = typer.Option("unknown", help="israel_resident, foreign_resident, unknown."),
    seller_type: str = typer.Option("individual", help="individual, company, partnership, trust, estate, unknown."),
    cpi_purchase: Optional[float] = typer.Option(None, help="Official CPI at purchase."),
    cpi_sale: Optional[float] = typer.Option(None, help="Official CPI at sale."),
    linear_relief_start_date: str = typer.Option("2014-01-01", help="Linear relief start date."),
    tax_rate: float = typer.Option(0.25, min=0.0, max=1.0, help="Assumed tax rate as decimal."),
    exemption_code: Optional[str] = typer.Option(None, help="single_apartment, inherited_apartment, gift_continuity, replacement_apartment, none."),
    notes: str = typer.Option("", help="Free-form notes for warnings."),
) -> TaxInputs:
    return _input_payload(
        purchase_date,
        sale_date,
        purchase_price,
        sale_price,
        purchase_costs,
        sale_costs,
        improvements,
        depreciation_claimed,
        ownership_share,
        property_type,
        qualifying_residential,
        seller_residency,
        seller_type,
        cpi_purchase,
        cpi_sale,
        linear_relief_start_date,
        tax_rate,
        exemption_code,
        notes,
    )


@app.command()
def estimate(
    purchase_date: str = typer.Option(..., help="Purchase date, YYYY-MM-DD or DD/MM/YYYY."),
    sale_date: str = typer.Option(..., help="Sale date, YYYY-MM-DD or DD/MM/YYYY."),
    purchase_price: float = typer.Option(..., min=0.0, help="Purchase price in NIS."),
    sale_price: float = typer.Option(..., min=0.0, help="Sale price in NIS."),
    purchase_costs: float = typer.Option(0.0, min=0.0, help="Purchase-related deductible costs."),
    sale_costs: float = typer.Option(0.0, min=0.0, help="Sale-related deductible costs."),
    improvements: float = typer.Option(0.0, min=0.0, help="Capital improvements."),
    depreciation_claimed: float = typer.Option(0.0, min=0.0, help="Depreciation claimed or claimable."),
    ownership_share: float = typer.Option(1.0, min=0.000001, max=1.0, help="Seller ownership fraction."),
    property_type: str = typer.Option("residential_apartment", help="residential_apartment, land, commercial, mixed_use, other."),
    qualifying_residential: bool = typer.Option(False, "--qualifying-residential", help="Treat as qualifying residential apartment for linear allocation."),
    seller_residency: str = typer.Option("unknown", help="israel_resident, foreign_resident, unknown."),
    seller_type: str = typer.Option("individual", help="individual, company, partnership, trust, estate, unknown."),
    cpi_purchase: Optional[float] = typer.Option(None, help="Official CPI at purchase."),
    cpi_sale: Optional[float] = typer.Option(None, help="Official CPI at sale."),
    linear_relief_start_date: str = typer.Option("2014-01-01", help="Linear relief start date."),
    tax_rate: float = typer.Option(0.25, min=0.0, max=1.0, help="Assumed tax rate as decimal."),
    exemption_code: Optional[str] = typer.Option(None, help="single_apartment, inherited_apartment, gift_continuity, replacement_apartment, none."),
    notes: str = typer.Option("", help="Free-form notes for warnings."),
    pretty: bool = typer.Option(False, "--pretty", help="Print readable summary."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
):
    """Run a direct Mas Shevach estimate."""
    inputs = _input_payload(
        purchase_date,
        sale_date,
        purchase_price,
        sale_price,
        purchase_costs,
        sale_costs,
        improvements,
        depreciation_claimed,
        ownership_share,
        property_type,
        qualifying_residential,
        seller_residency,
        seller_type,
        cpi_purchase,
        cpi_sale,
        linear_relief_start_date,
        tax_rate,
        exemption_code,
        notes,
    )
    estimate_result = estimate_tax(inputs)
    if pretty and not json_output:
        typer.echo(summarize(estimate_result))
    else:
        typer.echo(json.dumps(estimate_result.rounded(), ensure_ascii=False, indent=2))


@app.command()
def create(
    purchase_date: str = typer.Option(..., help="Purchase date, YYYY-MM-DD or DD/MM/YYYY."),
    sale_date: str = typer.Option(..., help="Sale date, YYYY-MM-DD or DD/MM/YYYY."),
    purchase_price: float = typer.Option(..., min=0.0, help="Purchase price in NIS."),
    sale_price: float = typer.Option(..., min=0.0, help="Sale price in NIS."),
    purchase_costs: float = typer.Option(0.0, min=0.0, help="Purchase-related deductible costs."),
    sale_costs: float = typer.Option(0.0, min=0.0, help="Sale-related deductible costs."),
    improvements: float = typer.Option(0.0, min=0.0, help="Capital improvements."),
    depreciation_claimed: float = typer.Option(0.0, min=0.0, help="Depreciation claimed or claimable."),
    ownership_share: float = typer.Option(1.0, min=0.000001, max=1.0, help="Seller ownership fraction."),
    property_type: str = typer.Option("residential_apartment", help="residential_apartment, land, commercial, mixed_use, other."),
    qualifying_residential: bool = typer.Option(False, "--qualifying-residential", help="Treat as qualifying residential apartment for linear allocation."),
    seller_residency: str = typer.Option("unknown", help="israel_resident, foreign_resident, unknown."),
    seller_type: str = typer.Option("individual", help="individual, company, partnership, trust, estate, unknown."),
    cpi_purchase: Optional[float] = typer.Option(None, help="Official CPI at purchase."),
    cpi_sale: Optional[float] = typer.Option(None, help="Official CPI at sale."),
    linear_relief_start_date: str = typer.Option("2014-01-01", help="Linear relief start date."),
    tax_rate: float = typer.Option(0.25, min=0.0, max=1.0, help="Assumed tax rate as decimal."),
    exemption_code: Optional[str] = typer.Option(None, help="single_apartment, inherited_apartment, gift_continuity, replacement_apartment, none."),
    notes: str = typer.Option("", help="Free-form notes for warnings."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    case_dir: Optional[Path] = typer.Option(None, help="Optional local case directory."),
):
    """Create a local case record and return its case id."""
    inputs = _input_payload(
        purchase_date,
        sale_date,
        purchase_price,
        sale_price,
        purchase_costs,
        sale_costs,
        improvements,
        depreciation_claimed,
        ownership_share,
        property_type,
        qualifying_residential,
        seller_residency,
        seller_type,
        cpi_purchase,
        cpi_sale,
        linear_relief_start_date,
        tax_rate,
        exemption_code,
        notes,
    )
    record = create_case_record(inputs=inputs, environment=env, case_dir=case_dir)
    typer.echo(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))


@app.command()
def estimate_case(
    case_id: str = typer.Option(..., help="Case id from the create command."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    case_dir: Optional[Path] = typer.Option(None, help="Optional local case directory."),
    pretty: bool = typer.Option(False, "--pretty", help="Print readable summary."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
):
    """Estimate a previously created local case."""
    estimate_result = estimate_saved_case(case_id=case_id, environment=env, case_dir=case_dir)
    if pretty and not json_output:
        typer.echo(summarize(estimate_result))
    else:
        typer.echo(json.dumps(estimate_result.rounded(), ensure_ascii=False, indent=2))


@app.command()
def checklist(property_type: str = typer.Option("residential_apartment", help="Property type for checklist.")):
    """Print a practical document checklist."""
    base = [
        "purchase contract",
        "sale contract",
        "land registry or rights extract",
        "purchase tax assessment",
        "legal fee invoices",
        "broker invoices",
        "improvement invoices and proofs of payment",
        "CPI values used in the estimate",
    ]
    if property_type in {"commercial", "mixed_use"}:
        base.extend(["fixed-asset ledger", "depreciation schedule", "VAT/accounting review"])
    if property_type == "residential_apartment":
        base.extend(["apartment ownership history", "exemption history", "residency support"])
    for item in base:
        typer.echo(f"- {item}")


if __name__ == "__main__":
    app()
