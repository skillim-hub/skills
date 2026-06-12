"""Command-line interface for Brand Reputation Monitor."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

try:
    import typer
except ImportError:  # pragma: no cover
    typer = None

from .client import (
    BrandReputationMonitor,
    Mention,
    MonitorConfig,
    create_monitor_config,
    dump_results,
    load_mentions,
    load_monitor_config,
    normalize_source,
    redact_private_data,
)

def _split_env_terms(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

def _config_from_args(
    env: str,
    config_id: str | None,
    brand_terms: list[str],
    exclude_terms: list[str],
    require_brand_match: bool,
) -> MonitorConfig:
    if config_id:
        config = load_monitor_config(config_id, env=env)
        if brand_terms:
            config.brand_terms.extend(brand_terms)
        if exclude_terms:
            config.exclude_terms.extend(exclude_terms)
        if require_brand_match:
            config.require_brand_match = True
        return config
    env_brand_terms = _split_env_terms(os.environ.get("BRM_BRAND_TERMS"))
    env_exclude_terms = _split_env_terms(os.environ.get("BRM_EXCLUDE_TERMS"))
    return MonitorConfig(
        brand_terms=list(brand_terms or env_brand_terms),
        exclude_terms=list(exclude_terms or env_exclude_terms),
        require_brand_match=require_brand_match,
    )

if typer:
    app = typer.Typer(help="Analyze Hebrew brand reputation mentions from permitted exports.")

    @app.command()
    def config_create(
        name: str = typer.Option("default-monitor", "--name", help="Human-readable monitor name."),
        env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
        brand_term: List[str] = typer.Option([], "--brand-term", help="Brand keyword. Repeatable."),
        exclude_term: List[str] = typer.Option([], "--exclude-term", help="Exclusion keyword. Repeatable."),
        require_brand_match: bool = typer.Option(False, "--require-brand-match", help="Exclude rows without a brand match."),
    ) -> None:
        """Create a local monitor configuration and print a JSON response containing id."""
        brand_terms = list(brand_term) or _split_env_terms(os.environ.get("BRM_BRAND_TERMS"))
        exclude_terms = list(exclude_term) or _split_env_terms(os.environ.get("BRM_EXCLUDE_TERMS"))
        payload = create_monitor_config(
            name=name,
            env=env,
            brand_terms=brand_terms,
            exclude_terms=exclude_terms,
            require_brand_match=require_brand_match,
        )
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))

    @app.command()
    def analyze(
        input_file: Path = typer.Argument(..., help="CSV, JSON, or JSONL file with mention records."),
        output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write analyzed records to file."),
        output_format: str = typer.Option("json", "--format", "-f", help="json, jsonl, or csv."),
        text_field: str = typer.Option("text", "--text-field", help="Field/column containing mention text."),
        env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
        config_id: Optional[str] = typer.Option(None, "--config-id", help="Identifier returned by config-create."),
        brand_term: List[str] = typer.Option([], "--brand-term", help="Brand keyword. Repeatable."),
        exclude_term: List[str] = typer.Option([], "--exclude-term", help="Exclusion keyword. Repeatable."),
        require_brand_match: bool = typer.Option(False, "--require-brand-match", help="Exclude rows without a brand-term match."),
        report: Optional[Path] = typer.Option(None, "--report", help="Write markdown report."),
    ) -> None:
        """Analyze mentions and print a JSON summary."""
        config = _config_from_args(env, config_id, list(brand_term), list(exclude_term), require_brand_match)
        mentions = load_mentions(input_file, text_field=text_field)
        monitor = BrandReputationMonitor(config)
        results = monitor.analyze_many(mentions)
        summary = monitor.summarize(results)
        typer.echo(json.dumps(summary, ensure_ascii=False, indent=2))
        if output:
            dump_results(results, output, output_format)
            typer.echo(json.dumps({"wrote": str(output), "format": output_format}, ensure_ascii=False, indent=2))
        if report:
            report.write_text(monitor.generate_markdown_report(results), encoding="utf-8")
            typer.echo(json.dumps({"wrote": str(report), "format": "markdown"}, ensure_ascii=False, indent=2))

    @app.command()
    def single(
        text: str = typer.Argument(..., help="Mention text to analyze."),
        source: str = typer.Option("manual", "--source", help="Source name."),
        engagement: int = typer.Option(0, "--engagement", help="Engagement count."),
        env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
        config_id: Optional[str] = typer.Option(None, "--config-id", help="Identifier returned by config-create."),
    ) -> None:
        """Analyze a single mention."""
        config = load_monitor_config(config_id, env=env) if config_id else MonitorConfig()
        mention = Mention(text=text, source=normalize_source(source), engagement=engagement)
        result = BrandReputationMonitor(config).analyze_mention(mention)
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

    @app.command()
    def redact(text: str = typer.Argument(..., help="Text containing possible personal data.")) -> None:
        """Redact common Israeli personal-data patterns."""
        typer.echo(redact_private_data(text))

    @app.command()
    def report(
        input_file: Path = typer.Argument(..., help="CSV, JSON, or JSONL input."),
        output: Path = typer.Argument(..., help="Markdown report output path."),
        text_field: str = typer.Option("text", "--text-field", help="Field/column containing mention text."),
        env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
        config_id: Optional[str] = typer.Option(None, "--config-id", help="Identifier returned by config-create."),
    ) -> None:
        """Generate a markdown report."""
        config = load_monitor_config(config_id, env=env) if config_id else MonitorConfig()
        mentions = load_mentions(input_file, text_field=text_field)
        monitor = BrandReputationMonitor(config)
        results = monitor.analyze_many(mentions)
        output.write_text(monitor.generate_markdown_report(results), encoding="utf-8")
        typer.echo(json.dumps({"wrote": str(output), "format": "markdown"}, ensure_ascii=False, indent=2))

    def main() -> None:
        app()

else:
    app = None

    def main() -> None:
        import argparse
        parser = argparse.ArgumentParser(description="Analyze Hebrew brand reputation mentions.")
        sub = parser.add_subparsers(dest="command", required=True)
        create = sub.add_parser("config-create")
        create.add_argument("--name", default="default-monitor")
        create.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
        create.add_argument("--brand-term", action="append", default=[])
        create.add_argument("--exclude-term", action="append", default=[])
        create.add_argument("--require-brand-match", action="store_true")
        single = sub.add_parser("single")
        single.add_argument("text")
        single.add_argument("--source", default="manual")
        single.add_argument("--engagement", type=int, default=0)
        single.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
        single.add_argument("--config-id")
        analyze_cmd = sub.add_parser("analyze")
        analyze_cmd.add_argument("input_file")
        analyze_cmd.add_argument("--output")
        analyze_cmd.add_argument("--format", default="json")
        analyze_cmd.add_argument("--text-field", default="text")
        analyze_cmd.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
        analyze_cmd.add_argument("--config-id")
        args = parser.parse_args()

        if args.command == "config-create":
            payload = create_monitor_config(
                name=args.name,
                env=args.env,
                brand_terms=args.brand_term or _split_env_terms(os.environ.get("BRM_BRAND_TERMS")),
                exclude_terms=args.exclude_term or _split_env_terms(os.environ.get("BRM_EXCLUDE_TERMS")),
                require_brand_match=args.require_brand_match,
            )
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        elif args.command == "single":
            config = load_monitor_config(args.config_id, env=args.env) if args.config_id else MonitorConfig()
            mention = Mention(text=args.text, source=normalize_source(args.source), engagement=args.engagement)
            result = BrandReputationMonitor(config).analyze_mention(mention)
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        elif args.command == "analyze":
            config = load_monitor_config(args.config_id, env=args.env) if args.config_id else MonitorConfig()
            mentions = load_mentions(args.input_file, text_field=args.text_field)
            monitor = BrandReputationMonitor(config)
            results = monitor.analyze_many(mentions)
            print(json.dumps(monitor.summarize(results), ensure_ascii=False, indent=2))
            if args.output:
                dump_results(results, args.output, args.format)

if __name__ == "__main__":
    main()
