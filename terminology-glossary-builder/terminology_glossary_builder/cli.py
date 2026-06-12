"""Command-line interface for the terminology glossary builder."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import GlossaryBuilder, GlossaryStore, build_sample_terms, validate_environment

app = typer.Typer(help="Create English-Hebrew glossaries with Israeli authoritative citations.", no_args_is_help=True)


def _emit(content: str, output: Optional[Path] = None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        typer.echo(str(output))
        return
    typer.echo(content, nl=False)


@app.command()
def build(
    terms: list[str] = typer.Argument(None, help="Terms. Accept repeated values or comma-separated text."),
    industry: str = typer.Option("general", "--industry", "-i"),
    audience: str = typer.Option("general", "--audience", "-a"),
    env: str = typer.Option("sandbox", "--env"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    fmt: str = typer.Option("markdown", "--format", "-f"),
    hebrew: bool = typer.Option(False, "--hebrew"),
    max_terms: Optional[int] = typer.Option(None, "--max-terms"),
    no_sort: bool = typer.Option(False, "--no-sort"),
) -> None:
    """Build a one-off glossary without saving it to the local store."""
    environment = validate_environment(env)
    builder = GlossaryBuilder()
    raw_terms = terms if terms else build_sample_terms(industry)
    result = builder.build_glossary(
        raw_terms,
        industry=industry,
        audience=audience,  # type: ignore[arg-type]
        language_mode="hebrew" if hebrew else "bilingual",
        environment=environment,
        max_terms=max_terms,
        sort_terms=not no_sort,
    )
    if fmt == "markdown":
        content = builder.to_markdown(result, localization="he" if hebrew else "en")
    elif fmt == "json":
        content = builder.to_json(result)
    elif fmt == "csv":
        content = builder.to_csv(result)
    else:
        raise typer.BadParameter("format must be markdown, json, or csv")
    _emit(content, output)


@app.command()
def create(
    terms: list[str] = typer.Argument(None, help="Terms to save. Accept repeated values or comma-separated text."),
    industry: str = typer.Option("general", "--industry", "-i"),
    audience: str = typer.Option("general", "--audience", "-a"),
    env: str = typer.Option("sandbox", "--env"),
    store: Path = typer.Option(Path(".terminology-glossaries.json"), "--store"),
    title: str = typer.Option("English-Hebrew Terminology Glossary", "--title"),
) -> None:
    """Create a glossary, save it, and print a JSON response containing its id."""
    environment = validate_environment(env)
    builder = GlossaryBuilder()
    raw_terms = terms if terms else build_sample_terms(industry)
    response = builder.create_glossary(
        raw_terms,
        store_path=store,
        industry=industry,
        audience=audience,  # type: ignore[arg-type]
        title=title,
        environment=environment,
    )
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command(name="export")
def export_command(
    glossary_id: str = typer.Argument(..., help="Glossary id returned by create."),
    store: Path = typer.Option(Path(".terminology-glossaries.json"), "--store"),
    fmt: str = typer.Option("markdown", "--format", "-f"),
    hebrew: bool = typer.Option(False, "--hebrew"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Export a saved glossary by id."""
    builder = GlossaryBuilder()
    content = builder.export_glossary(
        glossary_id,
        store_path=store,
        output_format=fmt,  # type: ignore[arg-type]
        localization="he" if hebrew else "en",
    )
    _emit(content, output)


@app.command()
def list_saved(store: Path = typer.Option(Path(".terminology-glossaries.json"), "--store")) -> None:
    """List saved glossaries from the local store."""
    rows = GlossaryStore(store).list()
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


@app.command()
def sources(json_output: bool = typer.Option(False, "--json")) -> None:
    """List source registry entries."""
    from .client import SOURCE_REGISTRY

    if json_output:
        typer.echo(json.dumps({key: source.to_dict() for key, source in SOURCE_REGISTRY.items()}, ensure_ascii=False, indent=2))
        return
    for key, source in SOURCE_REGISTRY.items():
        typer.echo(f"{key}\t{source.title_en}\t{source.authority}\t{source.url}")


@app.command()
def validate() -> None:
    """Validate source registry and term templates."""
    errors = GlossaryBuilder().validate_source_registry()
    if errors:
        for error in errors:
            typer.echo(error, err=True)
        raise typer.Exit(code=1)
    typer.echo("Validation passed")


@app.command()
def sample(industry: str = typer.Option("tax", "--industry", "-i"), fmt: str = typer.Option("terms", "--format", "-f")) -> None:
    """Print sample terms or a sample glossary for an industry."""
    terms = build_sample_terms(industry)
    builder = GlossaryBuilder()
    result = builder.build_glossary(terms, industry=industry, audience="small_business")
    if fmt == "terms":
        typer.echo("\n".join(terms))
    elif fmt == "json":
        typer.echo(builder.to_json(result), nl=False)
    elif fmt == "csv":
        typer.echo(builder.to_csv(result), nl=False)
    elif fmt == "markdown":
        typer.echo(builder.to_markdown(result), nl=False)
    else:
        raise typer.BadParameter("format must be terms, markdown, json, or csv")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
