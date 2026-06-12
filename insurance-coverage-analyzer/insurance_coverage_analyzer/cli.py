"""Command-line interface for Insurance Coverage Analyzer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    InsuranceCoverageAnalyzer,
    create_analysis_record,
    detect_duplicates,
    load_analysis_record,
    sample_policies,
    save_report,
)

app = typer.Typer(help="Analyze Israeli health, home, and life insurance policies.")


def _read_input(input_file: Path):
    analyzer = InsuranceCoverageAnalyzer()
    return analyzer.load_json(input_file)


@app.command()
def validate(input_file: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Validate policy data."""
    analyzer = InsuranceCoverageAnalyzer()
    policies, _profile = analyzer.load_json(input_file)
    result = analyzer.validate(policies)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    raise typer.Exit(code=0 if result["valid"] else 1)


@app.command()
def compare(
    input_file: Path = typer.Argument(..., exists=True, readable=True),
    format: str = typer.Option("markdown", "--format", "-f", help="json or markdown"),
    locale: str = typer.Option("en-IL", "--locale", help="Locale such as en-IL or he-IL"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write report to file"),
) -> None:
    """Compare policies and print or save a report."""
    analyzer = InsuranceCoverageAnalyzer(locale=locale)
    policies, profile = analyzer.load_json(input_file)
    result = analyzer.compare(policies, profile=profile)
    if output:
        save_report(result, output, format=format)
        typer.echo(str(output))
        return
    if format == "json":
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    elif format == "markdown":
        typer.echo(result.to_markdown(locale=locale))
    else:
        raise typer.BadParameter("format must be json or markdown")


@app.command()
def create(
    input_file: Path = typer.Argument(..., exists=True, readable=True),
    store_dir: Path = typer.Option(Path(".ica_runs"), "--store-dir", help="Directory for saved analysis records"),
    locale: str = typer.Option("en-IL", "--locale", help="Locale such as en-IL or he-IL"),
) -> None:
    """Create a saved comparison record and return an analysis_id."""
    policies, profile = _read_input(input_file)
    response = create_analysis_record(policies, profile=profile, store_dir=store_dir, locale=locale)
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command()
def show(
    analysis_id: str = typer.Argument(...),
    store_dir: Path = typer.Option(Path(".ica_runs"), "--store-dir", help="Directory with saved records"),
    format: str = typer.Option("json", "--format", "-f", help="json or markdown"),
    locale: str = typer.Option("en-IL", "--locale", help="Locale such as en-IL or he-IL"),
) -> None:
    """Show a saved analysis record by analysis_id."""
    record = load_analysis_record(analysis_id, store_dir=store_dir)
    if format == "json":
        typer.echo(json.dumps(record, ensure_ascii=False, indent=2))
        return
    if format != "markdown":
        raise typer.BadParameter("format must be json or markdown")
    analyzer = InsuranceCoverageAnalyzer(locale=locale)
    result = analyzer.compare(record["policies"], profile=record.get("profile"))
    typer.echo(result.to_markdown(locale=locale))


@app.command()
def duplicates(input_file: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Print duplicate or overlapping coverages."""
    analyzer = InsuranceCoverageAnalyzer()
    policies, _profile = analyzer.load_json(input_file)
    normalized = analyzer.normalize(policies)
    result = detect_duplicates(normalized)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command()
def checklist(policy_type: str = typer.Option("health", "--policy-type")) -> None:
    """Print a collection checklist for a policy type."""
    items = {
        "health": [
            "full policy schedule",
            "surgery chapter",
            "drugs outside basket chapter",
            "transplants chapter",
            "ambulatory services chapter",
            "exclusions and loadings",
            "waiting periods",
            "supplementary health-plan tier",
        ],
        "home": [
            "structure sum insured",
            "contents sum insured",
            "mortgage lender clause",
            "water damage terms",
            "earthquake deductible",
            "third-party liability",
            "employer liability",
            "valuables schedule",
        ],
        "life": [
            "death benefit amount",
            "mortgage assignment",
            "beneficiary wording",
            "premium path",
            "index linkage",
            "exclusions",
            "riders",
            "business agreement dependency",
        ],
    }
    typer.echo(json.dumps(items.get(policy_type, []), ensure_ascii=False, indent=2))


@app.command()
def sample(output: Optional[Path] = typer.Option(None, "--output", "-o")) -> None:
    """Print or save sample policy input."""
    payload = {"policies": sample_policies(), "profile": {"segment": "consumer"}}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if output:
        output.write_text(text, encoding="utf-8")
        typer.echo(str(output))
    else:
        typer.echo(text)


def main() -> None:
    app()


if __name__ == "__main__":
    app()
