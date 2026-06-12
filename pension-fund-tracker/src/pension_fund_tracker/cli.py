#!/usr/bin/env python3
"""CLI for information-only pension fund tracking."""

from __future__ import annotations
from pathlib import Path
from typing import Any
import typer
from rich.console import Console
from rich.table import Table

import pension_fund_tracker as client_module

app = typer.Typer(help="Information-only Israeli pension fund returns and fees tracker.", no_args_is_help=True)
console = Console()

def _client() -> Any: return client_module.PensionFundTrackerClient()
def _load(path: Path) -> list[Any]:
    c = _client()
    return c.load_json(path) if path.suffix.lower() == ".json" else c.load_csv(path)

@app.command()
def normalize(input_path: Path, output: Path = typer.Option(Path("normalized.json"), "--output", "-o")) -> None:
    """Normalize CSV or JSON to canonical JSON."""
    records = _load(input_path); _client().export_json(records, output)
    console.print(f"Normalized {len(records)} records to {output}")

@app.command()
def validate(input_path: Path) -> None:
    """Validate source or normalized data."""
    c = _client(); issues = c.validate_records(_load(input_path))
    table = Table(title=f"Validation issues: {len(issues)}")
    for col in ("Level","Code","Fund ID","Row","Message"): table.add_column(col)
    for issue in issues:
        table.add_row(issue.level, issue.code, issue.fund_id or "", "" if issue.record_index is None else str(issue.record_index), issue.message)
    console.print(table)
    if any(i.level == "critical" for i in issues): raise typer.Exit(code=2)

@app.command()
def rank(input_path: Path, metric: str = typer.Option("trailing_36m_return_pct", "--metric", "-m"), top: int = typer.Option(10, "--top", "-n"), ascending: bool = typer.Option(False, "--ascending")) -> None:
    """Rank latest records by a selected metric."""
    c = _client(); rows = c.rank(_load(input_path), metric=metric, top=top, ascending=ascending)
    table = Table(title=f"Latest records ranked by {metric}")
    for col in ("Fund ID","Fund name","Provider","Report date",metric): table.add_column(col)
    for r in rows:
        v = getattr(r, metric)
        table.add_row(r.fund_id, r.fund_name, r.provider, r.report_date.isoformat() if r.report_date else "", "" if v is None else f"{v:.4g}")
    console.print(table)

@app.command()
def compare(input_path: Path, fund_ids: list[str]) -> None:
    """Compare selected funds using latest records."""
    rows = _client().compare(_load(input_path), fund_ids)
    cols = ["fund_id","fund_name","provider","report_date","monthly_return_pct","trailing_12m_return_pct","trailing_36m_return_pct","management_fee_deposit_pct","management_fee_assets_pct"]
    table = Table(title="Information-only comparison")
    for col in cols: table.add_column(col)
    for row in rows: table.add_row(*(str(row.get(col, "")) for col in cols))
    console.print(table)
    console.print("Information only. Not pension, investment, insurance, or tax advice. Past returns do not indicate future returns.")

@app.command("fee-impact")
def fee_impact(monthly_contribution: float = typer.Option(..., "--monthly-contribution"), years: int = typer.Option(..., "--years"), annual_return: float = typer.Option(..., "--annual-return"), deposit_fee: float = typer.Option(0.0, "--deposit-fee"), asset_fee: float = typer.Option(0.0, "--asset-fee"), starting_balance: float = typer.Option(0.0, "--starting-balance")) -> None:
    """Estimate management-fee impact under explicit assumptions."""
    result = _client().estimate_fee_impact(monthly_contribution=monthly_contribution, starting_balance=starting_balance, years=years, annual_return_pct=annual_return, deposit_fee_pct=deposit_fee, asset_fee_pct=asset_fee)
    table = Table(title="Fee impact estimate")
    table.add_column("Metric"); table.add_column("Value", justify="right")
    table.add_row("Monthly contribution", client_module.format_nis(result.monthly_contribution))
    table.add_row("Starting balance", client_module.format_nis(result.starting_balance))
    table.add_row("Years", str(result.years))
    table.add_row("Assumed annual gross return", f"{result.annual_return_pct:.2f}%")
    table.add_row("Deposit fee", f"{result.deposit_fee_pct:.2f}%")
    table.add_row("Asset fee", f"{result.asset_fee_pct:.2f}%")
    table.add_row("Gross no-fee balance", client_module.format_nis(result.gross_no_fee_balance))
    table.add_row("Net with fees balance", client_module.format_nis(result.net_with_fees_balance))
    table.add_row("Estimated fee drag", client_module.format_nis(result.estimated_fee_drag))
    console.print(table)
    console.print("Information only. Simplified estimate based on explicit assumptions.")

@app.command("fetch-ckan")
def fetch_ckan(resource_id: str, output: Path = typer.Option(Path("normalized-ckan.json"), "--output", "-o"), limit: int = typer.Option(1000, "--limit"), max_records: int | None = typer.Option(None, "--max-records")) -> None:
    """Fetch and normalize a Data.gov.il CKAN resource."""
    c = _client(); records = c.fetch_ckan(resource_id=resource_id, limit=limit, max_records=max_records)
    c.export_json(records, output); console.print(f"Fetched and normalized {len(records)} records to {output}")

@app.command()
def score(input_path: Path) -> None:
    """Calculate a neutral composite sorting score from available public metrics."""
    table = Table(title="Information-only composite score")
    for col in ("Fund ID","Fund name","Provider","Score","Caveats"): table.add_column(col)
    for result in _client().score_funds(_load(input_path)):
        table.add_row(result.fund_id, result.fund_name, result.provider, f"{result.score:.2f}", "; ".join(result.caveats))
    console.print(table)
    console.print("Score is for sorting comparable public records only. It is not a recommendation.")

if __name__ == "__main__":
    app()
