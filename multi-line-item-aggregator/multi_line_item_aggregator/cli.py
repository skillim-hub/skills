"""Command-line interface for multi-line invoice aggregation."""
from __future__ import annotations
import asyncio, json
from pathlib import Path
from typing import Optional
import click
from .core import CalculationOptions, DiscountAllocationMethod, aggregate_invoice, aggregate_invoice_async, create_sample_invoice, format_summary, load_lines_from_csv, load_lines_from_json, parse_discount, save_result_json

def _load(path: Path, fmt: Optional[str]):
    inferred=fmt or path.suffix.lower().lstrip('.')
    if inferred=='json': return load_lines_from_json(path)
    if inferred=='csv': return load_lines_from_csv(path)
    raise click.ClickException('Use --format json or --format csv, or provide a .json/.csv file')

@click.group(context_settings={'help_option_names':['-h','--help']})
def app() -> None:
    """Aggregate multi-line Israeli invoices with VAT, discounts, and agorot rounding."""

@app.command('create-sample')
@click.argument('output_file', type=click.Path(dir_okay=False, path_type=Path))
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default='sandbox', show_default=True)
def create_sample_command(output_file: Path, environment: str) -> None:
    """Create a sample invoice file and print a JSON creation response."""
    click.echo(json.dumps(create_sample_invoice(output_file, environment=environment), ensure_ascii=False, indent=2))

@app.command('aggregate')
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--format', 'fmt', type=click.Choice(['json','csv']), default=None)
@click.option('--id', 'invoice_id', default='', help='Invoice identifier from a create response or external draft.')
@click.option('--invoice-id', 'invoice_id_alias', default='', help='Alias for --id.')
@click.option('--invoice-date', default='')
@click.option('--vat-number', default='')
@click.option('--invoice-discount-type', type=click.Choice(['amount','percent']), default=None)
@click.option('--invoice-discount-value', default=None)
@click.option('--allocation', type=click.Choice(['by_net','by_gross','equal']), default='by_net')
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default='sandbox', show_default=True)
@click.option('--output','-o', type=click.Path(dir_okay=False, path_type=Path), default=None)
@click.option('--json-output', is_flag=True)
def aggregate_command(input_file: Path, fmt: Optional[str], invoice_id: str, invoice_id_alias: str, invoice_date: str, vat_number: str, invoice_discount_type: Optional[str], invoice_discount_value: Optional[str], allocation: str, environment: str, output: Optional[Path], json_output: bool) -> None:
    """Aggregate invoice lines from JSON or CSV."""
    try:
        result=aggregate_invoice(_load(input_file, fmt), invoice_id=invoice_id or invoice_id_alias, invoice_date=invoice_date, vat_number=vat_number, invoice_discount=parse_discount(invoice_discount_type, invoice_discount_value), options=CalculationOptions(invoice_discount_allocation=DiscountAllocationMethod(allocation), environment=environment))
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    if output: save_result_json(result, output)
    click.echo(result.to_json() if json_output else format_summary(result))

@app.command('aggregate-async')
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--format', 'fmt', type=click.Choice(['json','csv']), default=None)
@click.option('--id', 'invoice_id', default='')
@click.option('--invoice-date', default='')
@click.option('--vat-number', default='')
@click.option('--allocation', type=click.Choice(['by_net','by_gross','equal']), default='by_net')
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default='sandbox', show_default=True)
@click.option('--json-output', is_flag=True)
def aggregate_async_command(input_file: Path, fmt: Optional[str], invoice_id: str, invoice_date: str, vat_number: str, allocation: str, environment: str, json_output: bool) -> None:
    """Run aggregation through the async helper."""
    async def run():
        return await aggregate_invoice_async(_load(input_file, fmt), invoice_id=invoice_id, invoice_date=invoice_date, vat_number=vat_number, options=CalculationOptions(invoice_discount_allocation=DiscountAllocationMethod(allocation), environment=environment))
    try: result=asyncio.run(run())
    except Exception as exc: raise click.ClickException(str(exc)) from exc
    click.echo(result.to_json() if json_output else format_summary(result))

def main() -> None:
    """Run the command-line interface."""
    app()

if __name__ == '__main__': main()
