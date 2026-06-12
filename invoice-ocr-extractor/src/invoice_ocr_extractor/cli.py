from __future__ import annotations

import json
from pathlib import Path

import click

from .client import ExtractorConfig, ExtractedInvoice, InvoiceOCRExtractor, export_csv, load_invoice_json, SCHEMA_VERSION


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Extract and validate invoice OCR data."""


@cli.command()
@click.option("--text-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, help="OCR text file to parse.")
@click.option("--pretty", is_flag=True, help="Pretty-print JSON.")
@click.option("--default-vat-rate", type=float, default=18.0, show_default=True, help="Default VAT rate for optional inference.")
@click.option("--infer-vat-when-rate-missing", is_flag=True, help="Infer VAT when no printed rate exists.")
def parse(text_file: Path, pretty: bool, default_vat_rate: float, infer_vat_when_rate_missing: bool) -> None:
    """Create one extraction response from an OCR text file."""
    config = ExtractorConfig(default_vat_rate=default_vat_rate, infer_vat_when_rate_missing=infer_vat_when_rate_missing)
    result = InvoiceOCRExtractor(config).extract_from_file(text_file)
    click.echo(result.to_json(indent=2 if pretty else None))


@cli.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", "-o", type=click.Path(dir_okay=False, path_type=Path), required=True, help="CSV output path.")
@click.option("--pattern", default="*.txt", show_default=True, help="Glob pattern for OCR text files.")
@click.option("--pretty-summary", is_flag=True, help="Pretty-print batch summary.")
def batch(folder: Path, output: Path, pattern: str, pretty_summary: bool) -> None:
    """Create extraction responses for a folder and export CSV."""
    extractor = InvoiceOCRExtractor()
    rows = extractor.batch_extract(folder, pattern)
    export_csv(rows, output)
    summary = {
        "processed": len(rows),
        "output": str(output),
        "record_ids": [result.record_id for _, result in rows],
        "low_confidence": sum(1 for _, result in rows if result.confidence < extractor.config.low_confidence_threshold),
    }
    click.echo(json.dumps(summary, ensure_ascii=False, indent=2 if pretty_summary else None))


@cli.command()
@click.option("--json-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, help="Extraction JSON to validate.")
@click.option("--expected-id", default=None, help="Record id from the create response.")
def validate(json_file: Path, expected_id: str | None) -> None:
    """Validate a JSON extraction response, optionally checking the record id chain."""
    errors = InvoiceOCRExtractor().validate(load_invoice_json(json_file), expected_id=expected_id)
    click.echo(json.dumps({"valid": not bool(errors), "errors": errors}, ensure_ascii=False, indent=2))
    if errors:
        raise click.exceptions.Exit(1)


@cli.command("schema")
def schema() -> None:
    """Print the schema version and fields."""
    fields = list(ExtractedInvoice().to_dict().keys())
    click.echo(json.dumps({"schema_version": SCHEMA_VERSION, "fields": fields}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
