#!/usr/bin/env python3
"""Command-line interface for the chat data analyzer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

import chat_data_analyzer_client as client_mod


def _write_output(text: str, output: Optional[str]) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
        click.echo(f"Wrote {output}")
    else:
        click.echo(text)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Analyze Hebrew and mixed-language customer chats."""


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["json", "csv", "summary"], case_sensitive=False), default="summary", show_default=True)
@click.option("-o", "--output", type=click.Path(dir_okay=False), default=None, help="Write output to a file.")
@click.option("--pretty/--compact", default=True, show_default=True, help="Pretty-print JSON output.")
def analyze(input_file: Path, output_format: str, output: Optional[str], pretty: bool) -> None:
    """Analyze a JSON, JSONL, or CSV chat export."""

    analyzer = client_mod.ChatDataAnalyzerClient()
    payload = client_mod.load_any(input_file)
    dataset = analyzer.analyze_dataset(payload)

    if output_format == "json":
        text = analyzer.to_json(dataset, indent=2 if pretty else None)
    elif output_format == "csv":
        text = analyzer.to_csv(dataset)
    else:
        lines = [
            f"conversations: {dataset.conversation_count}",
            f"messages: {dataset.total_messages}",
            f"drop_off_rate: {dataset.drop_off_rate:.1%}",
            f"unresolved_rate: {dataset.unresolved_rate:.1%}",
            f"escalation_rate: {dataset.escalation_rate:.1%}",
            f"intent_distribution: {json.dumps(dataset.intent_distribution, ensure_ascii=False)}",
            f"sentiment_distribution: {json.dumps(dataset.sentiment_distribution, ensure_ascii=False)}",
            "recommendations:",
        ]
        lines.extend(f"- {item}" for item in dataset.recommendations)
        text = "\n".join(lines)
    _write_output(text, output)


@cli.command(name="create")
@click.argument("output_file", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--session-id", default=None, help="Optional session identifier. Generated deterministically when omitted.")
@click.option("--text", default="שלום, אפשר לקבל חשבונית מס על 350 ₪?", show_default=True, help="User message text for the created sample conversation.")
def create(output_file: Path, session_id: Optional[str], text: str) -> None:
    """Create one normalized conversation file and print its create response."""

    analyzer = client_mod.ChatDataAnalyzerClient()
    response = analyzer.create_conversation([{"sender": "user", "text": text}], session_id=session_id)
    output_file.write_text(json.dumps([response], ensure_ascii=False, indent=2), encoding="utf-8")
    click.echo(json.dumps({"session_id": response["session_id"], "path": str(output_file)}, ensure_ascii=False, indent=2))


@cli.command()
@click.argument("text", nargs=-1)
@click.option("--json-output", is_flag=True, help="Return structured JSON.")
def text(text: tuple[str, ...], json_output: bool) -> None:
    """Analyze one text snippet from the command line."""

    raw = " ".join(text)
    if not raw:
        raise click.ClickException("Provide text to analyze.")
    analyzer = client_mod.ChatDataAnalyzerClient()
    result = analyzer.analyze_text(raw)
    if json_output:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        top_intent = result["intents"][0]["intent"]
        click.echo(f"language: {result['language']}")
        click.echo(f"sentiment: {result['sentiment']['label']} ({result['sentiment']['score']})")
        click.echo(f"top_intent: {top_intent}")
        if result["risk_flags"]:
            click.echo(f"risk_flags: {json.dumps(result['risk_flags'], ensure_ascii=False)}")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate an input file without producing analytics."""

    payload = client_mod.load_any(input_file)
    normalized = client_mod.normalize_dataset(payload)
    for item in normalized:
        client_mod.validate_conversation(item["messages"])
    click.echo(f"valid conversations: {len(normalized)}")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("output_file", type=click.Path(dir_okay=False, path_type=Path))
def anonymize(input_file: Path, output_file: Path) -> None:
    """Mask emails, Israeli ID-like values, phone numbers, and card-like values."""

    payload = client_mod.load_any(input_file)
    normalized = client_mod.normalize_dataset(payload)
    masked = []
    for item in normalized:
        messages = []
        for message in item["messages"]:
            copied = dict(message)
            copied["text"] = client_mod.anonymize_text(str(copied.get("text", "")))
            messages.append(copied)
        masked.append({"session_id": item["session_id"], "messages": messages})
    output_file.write_text(json.dumps(masked, ensure_ascii=False, indent=2), encoding="utf-8")
    click.echo(f"Wrote {output_file}")


@cli.command()
@click.argument("output_file", type=click.Path(dir_okay=False, path_type=Path))
def sample(output_file: Path) -> None:
    """Create a small Hebrew sample dataset."""

    path = client_mod.write_sample_dataset(output_file)
    click.echo(f"Wrote {path}")


if __name__ == "__main__":
    cli()
