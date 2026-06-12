"""Command line interface for the regulatory update notifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    AlertProfile,
    RegulatoryMonitorClient,
    RuntimeEnvironment,
    create_profile,
    default_sources,
    infer_industries,
    load_profile,
    load_updates,
    make_digest,
    save_default_config,
    save_profile,
    save_updates,
)

app = typer.Typer(help="Monitor and summarize Israeli regulatory updates.")


def _environment(value: str) -> RuntimeEnvironment:
    try:
        return RuntimeEnvironment(value)
    except ValueError as exc:
        raise typer.BadParameter("env must be sandbox or production") from exc


@app.command("make-config")
def make_config(
    output: Path = typer.Argument(..., help="Path for generated JSON config."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Write a starter source configuration."""
    environment = _environment(env)
    save_default_config(output, environment)
    typer.echo(json.dumps({"path": str(output), "environment": environment.value}, ensure_ascii=False, indent=2))


@app.command("create-profile")
def create_profile_command(
    name: str = typer.Option(..., "--name", "-n", help="Profile name."),
    industry: list[str] = typer.Option([], "--industry", "-i", help="Industry/profile tag. Repeatable."),
    keyword: list[str] = typer.Option([], "--keyword", "-k", help="Keyword filter. Repeatable."),
    locale: str = typer.Option("he", "--locale", help="en or he."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write profile JSON."),
) -> None:
    """Create a monitoring profile and print a response containing its id."""
    profile = create_profile(name=name, industries=industry, keywords=keyword, locale=locale, environment=_environment(env))
    if output:
        save_profile(output, profile)
    response = profile.to_dict()
    if output:
        response["path"] = str(output)
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command("list-sources")
def list_sources(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="JSON or YAML source config."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """List configured source names."""
    sources = RegulatoryMonitorClient.from_config(config).sources if config else default_sources(_environment(env))
    payload = [
        {
            "name": source.name,
            "regulator": source.regulator,
            "source_type": source.source_type.value,
            "industries": source.industries,
        }
        for source in sources
    ]
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def classify(text: str = typer.Argument(..., help="Text to classify by likely industry.")) -> None:
    """Infer likely industries for a short text."""
    typer.echo(json.dumps({"industries": infer_industries(text)}, ensure_ascii=False, indent=2))


@app.command()
def scan(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="JSON or YAML source config."),
    profile_path: Optional[Path] = typer.Option(None, "--profile", help="Profile JSON from create-profile."),
    profile_id: Optional[str] = typer.Option(None, "--profile-id", help="Expected profile id."),
    industry: list[str] = typer.Option([], "--industry", "-i", help="Industry/profile tag. Repeatable."),
    keyword: list[str] = typer.Option([], "--keyword", "-k", help="Keyword filter. Repeatable."),
    since: Optional[str] = typer.Option(None, "--since", help="Earliest publication date, YYYY-MM-DD or DD/MM/YYYY."),
    minimum_score: int = typer.Option(0, "--minimum-score", "-m", help="Minimum relevance score."),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum updates."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write JSON output."),
    locale: str = typer.Option("he", "--locale", help="en or he."),
    digest_mode: bool = typer.Option(False, "--digest", help="Print Markdown digest instead of JSON."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Scan sources and print matching updates."""
    environment = _environment(env)
    monitor = RegulatoryMonitorClient.from_config(config) if config else RegulatoryMonitorClient(default_sources(environment))
    profile: AlertProfile | None = load_profile(profile_path, profile_id) if profile_path else None
    updates = monitor.collect_updates(
        since=since,
        industries=industry,
        keywords=keyword,
        profile=profile,
        minimum_score=minimum_score,
        limit=limit,
    )
    if output:
        save_updates(output, updates)
    if digest_mode:
        typer.echo(make_digest(updates, locale=profile.locale if profile else locale))
    else:
        typer.echo(json.dumps([update.to_dict() for update in updates], ensure_ascii=False, indent=2))


@app.command()
def digest(
    input_path: Path = typer.Option(..., "--input", "-i", help="JSON updates file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Markdown output path."),
    locale: str = typer.Option("he", "--locale", help="en or he."),
    title: Optional[str] = typer.Option(None, "--title", help="Digest title."),
) -> None:
    """Create a Markdown digest from saved updates."""
    updates = load_updates(input_path)
    markdown = make_digest(updates, locale=locale, title=title)
    if output:
        output.write_text(markdown, encoding="utf-8")
    typer.echo(markdown)


def main() -> None:
    """Run the CLI."""
    app()


if __name__ == "__main__":
    main()
