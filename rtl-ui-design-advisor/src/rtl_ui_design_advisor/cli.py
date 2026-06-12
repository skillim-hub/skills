"""Command-line interface for RTL UI Design Advisor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from .client import RtlAuditClient, format_dd_mm_yyyy, validate_israeli_id


def _read_text(text: str | None, file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if text is not None:
        return text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise click.ClickException("Provide --text, --file, or stdin.")


def _emit_result(result, output_format: str) -> None:
    if output_format == "json":
        click.echo(result.to_json())
    else:
        click.echo(result.to_markdown())


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Audit HTML, CSS, and Tailwind for RTL readiness."""


@main.command("audit-html")
@click.option("--text", help="HTML/JSX/TSX text to audit.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="File to audit.")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json"]), default="markdown")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
def audit_html(text: str | None, file_path: str | None, output_format: str, store_dir: str) -> None:
    """Audit HTML or JSX-like markup."""
    _emit_result(RtlAuditClient(store_dir).audit_html(_read_text(text, file_path)), output_format)


@main.command("audit-css")
@click.option("--text", help="CSS text to audit.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="File to audit.")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json"]), default="markdown")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
def audit_css(text: str | None, file_path: str | None, output_format: str, store_dir: str) -> None:
    """Audit CSS for physical direction properties."""
    _emit_result(RtlAuditClient(store_dir).audit_css(_read_text(text, file_path)), output_format)


@main.command("audit-tailwind")
@click.option("--text", help="Tailwind class string to audit.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="File containing Tailwind classes.")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json"]), default="markdown")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
def audit_tailwind(text: str | None, file_path: str | None, output_format: str, store_dir: str) -> None:
    """Audit Tailwind class strings."""
    _emit_result(RtlAuditClient(store_dir).audit_tailwind(_read_text(text, file_path)), output_format)


@main.command("create-audit")
@click.option("--kind", type=click.Choice(["html", "css", "tailwind"]), required=True)
@click.option("--text", help="Source text to audit.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="File to audit.")
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default="sandbox")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="json")
def create_audit(kind: str, text: str | None, file_path: str | None, env_name: str, store_dir: str, output_format: str) -> None:
    """Create a stored audit and print its id."""
    record = RtlAuditClient(store_dir).create_audit(kind, _read_text(text, file_path), env=env_name)  # type: ignore[arg-type]
    if output_format == "json":
        click.echo(record.to_json())
    else:
        click.echo(f"Audit id: {record.id}\n\n{record.result.to_markdown()}")


@main.command("show-audit")
@click.argument("audit_id")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json"]), default="markdown")
def show_audit(audit_id: str, store_dir: str, output_format: str) -> None:
    """Show a stored audit by id."""
    record = RtlAuditClient(store_dir).get_audit(audit_id)
    if output_format == "json":
        click.echo(record.to_json())
    else:
        click.echo(f"Audit id: {record.id}\nKind: {record.kind}\nEnvironment: {record.env}\n\n{record.result.to_markdown()}")


@main.command("fix-css")
@click.option("--text", help="CSS text to transform.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="CSS file to transform.")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
def fix_css(text: str | None, file_path: str | None, store_dir: str) -> None:
    """Apply safe first-pass logical CSS replacements."""
    click.echo(RtlAuditClient(store_dir).fix_css_logical(_read_text(text, file_path)))


@main.command("checklist")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json"]), default="markdown")
@click.option("--store-dir", type=click.Path(file_okay=False), default=".rtl-advisor-audits")
def checklist(output_format: str, store_dir: str) -> None:
    """Print production checklist."""
    items = RtlAuditClient(store_dir).production_checklist()
    if output_format == "json":
        click.echo(json.dumps({"items": items}, ensure_ascii=False, indent=2))
    else:
        for item in items:
            click.echo(f"- [ ] {item}")


@main.command("date")
@click.argument("year", type=int)
@click.argument("month", type=int)
@click.argument("day", type=int)
def date_command(year: int, month: int, day: int) -> None:
    """Format a date as DD/MM/YYYY."""
    click.echo(format_dd_mm_yyyy(year, month, day))


@main.command("validate-id")
@click.argument("value")
def validate_id(value: str) -> None:
    """Validate an Israeli ID checksum."""
    click.echo("valid" if validate_israeli_id(value) else "invalid")


if __name__ == "__main__":
    main()
