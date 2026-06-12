#!/usr/bin/env python3
"""Command-line interface for the transliteration helper."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import click

from transliteration_helper_client import (
    TransliterationClient,
    TransliterationValidationError,
    write_results,
)


def _common_options(func: Any) -> Any:
    func = click.option("--case", "output_case", type=click.Choice(["upper", "title", "lower", "preserve"]), default="upper", show_default=True, help="Output casing.")(func)
    func = click.option("--strict", is_flag=True, help="Disable common-name overrides and use stricter letter rules.")(func)
    func = click.option("--no-known", is_flag=True, help="Disable common Israeli name overrides.")(func)
    func = click.option("--tzadi-style", type=click.Choice(["z", "tz", "ts"]), default="z", show_default=True, help="Latin rendering for צ/ץ.")(func)
    func = click.option("--allow-mixed/--reject-mixed", default=True, show_default=True, help="Permit mixed Hebrew/Latin input.")(func)
    func = click.option("--explain", is_flag=True, help="Include rule trace in JSON output.")(func)
    return func


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Transliterate Hebrew names into Latin script for forms, exports, and checks."""


@main.command()
@click.argument("name", nargs=-1, required=True)
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text", show_default=True)
@_common_options
def transliterate(
    name: tuple[str, ...],
    output_format: str,
    output_case: str,
    strict: bool,
    no_known: bool,
    tzadi_style: str,
    allow_mixed: bool,
    explain: bool,
) -> None:
    """Transliterate one name supplied on the command line."""
    client = TransliterationClient()
    value = " ".join(name)
    try:
        result = client.transliterate(
            value,
            output_case=output_case,
            use_known_names=not no_known,
            strict=strict,
            tzadi_style=tzadi_style,
            allow_mixed=allow_mixed,
            explain=explain,
        )
    except TransliterationValidationError as exc:
        raise click.ClickException(str(exc)) from exc

    if output_format == "json":
        click.echo(result.to_json())
    else:
        click.echo(result.latin)


@main.command()
@click.option("--input-file", "-i", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, help="UTF-8 text file or CSV file.")
@click.option("--output-file", "-o", type=click.Path(dir_okay=False, path_type=Path), required=False, help="Destination file. Defaults to stdout.")
@click.option("--input-column", default="hebrew_name", show_default=True, help="CSV column containing Hebrew names.")
@click.option("--format", "output_format", type=click.Choice(["text", "json", "csv"]), default="json", show_default=True)
@_common_options
def batch(
    input_file: Path,
    output_file: Path | None,
    input_column: str,
    output_format: str,
    output_case: str,
    strict: bool,
    no_known: bool,
    tzadi_style: str,
    allow_mixed: bool,
    explain: bool,
) -> None:
    """Transliterate names from a text or CSV file."""
    client = TransliterationClient()
    try:
        results = client.transliterate_file(
            input_file,
            input_column=input_column,
            output_format=output_format,
            output_case=output_case,
            use_known_names=not no_known,
            strict=strict,
            tzadi_style=tzadi_style,
            allow_mixed=allow_mixed,
            explain=explain,
        )
    except TransliterationValidationError as exc:
        raise click.ClickException(str(exc)) from exc

    if output_file:
        write_results(results, output_file, output_format=output_format)
        click.echo(f"Wrote {len(results)} rows to {output_file}")
        return

    if output_format == "json":
        click.echo(json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2))
    elif output_format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=["original", "normalized", "latin", "warnings"])
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "original": result.original,
                    "normalized": result.normalized,
                    "latin": result.latin,
                    "warnings": ";".join(result.warnings),
                }
            )
    else:
        for result in results:
            click.echo(result.latin)


@main.command("validate")
@click.argument("name", nargs=-1, required=True)
@_common_options
def validate(
    name: tuple[str, ...],
    output_case: str,
    strict: bool,
    no_known: bool,
    tzadi_style: str,
    allow_mixed: bool,
    explain: bool,
) -> None:
    """Return warnings and rule traces for one name."""
    client = TransliterationClient()
    value = " ".join(name)
    try:
        result = client.transliterate(
            value,
            output_case=output_case,
            use_known_names=not no_known,
            strict=strict,
            tzadi_style=tzadi_style,
            allow_mixed=allow_mixed,
            explain=True,
        )
    except TransliterationValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.to_json())


@main.command("create")
@click.argument("name", nargs=-1, required=True)
@click.option("--store", type=click.Path(dir_okay=False, path_type=Path), required=True, help="JSONL store file for created records.")
@_common_options
def create_record_command(
    name: tuple[str, ...],
    store: Path,
    output_case: str,
    strict: bool,
    no_known: bool,
    tzadi_style: str,
    allow_mixed: bool,
    explain: bool,
) -> None:
    """Create a local transliteration record and return its identifier."""
    client = TransliterationClient()
    value = " ".join(name)
    try:
        record = client.create_record(
            value,
            store_path=store,
            output_case=output_case,
            use_known_names=not no_known,
            strict=strict,
            tzadi_style=tzadi_style,
            allow_mixed=allow_mixed,
            explain=explain,
        )
    except TransliterationValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(record, ensure_ascii=False, indent=2))


@main.command("show")
@click.argument("record_id")
@click.option("--store", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, help="JSONL store file containing created records.")
def show_record_command(record_id: str, store: Path) -> None:
    """Read a local transliteration record by identifier."""
    client = TransliterationClient()
    try:
        record = client.get_record(record_id, store)
    except TransliterationValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
