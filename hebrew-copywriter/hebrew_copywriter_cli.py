"""Command line interface for the Hebrew Copywriter helper."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional, Tuple

import click

from hebrew_copywriter import (
    Channel,
    CopyBrief,
    GenderMode,
    HebrewCopywriterClient,
    Register,
    brief_from_json_file,
    brief_template,
    load_saved_brief,
    save_brief,
)


def _decimal_or_none(value: Optional[str]):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise click.BadParameter("price must be numeric") from exc


def _print_result(result, output_format: str) -> None:
    if output_format == "json":
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if "text" in result:
        click.echo(result["text"])
    else:
        for label, key in [
            ("כותרת", "headline"),
            ("כותרת משנה", "subheadline"),
            ("גוף", "body"),
            ("הנעה לפעולה", "cta"),
        ]:
            if result.get(key):
                click.echo(f"{label}: {result[key]}")
        if result.get("headlines"):
            click.echo("כותרות:")
            for item in result["headlines"]:
                click.echo(f"- {item}")
        if result.get("descriptions"):
            click.echo("תיאורים:")
            for item in result["descriptions"]:
                click.echo(f"- {item}")
    if result.get("warnings"):
        click.echo("\nאזהרות:")
        for warning in result["warnings"]:
            click.echo(f"- {warning}")
    if result.get("compliance_issues"):
        click.echo("\nבדיקות ציות:")
        for issue in result["compliance_issues"]:
            click.echo(f"- {issue}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Hebrew copywriter CLI for Israeli marketing briefs."""


@main.command("brief-template")
def brief_template_command() -> None:
    """Print a reusable JSON brief template."""
    click.echo(json.dumps(brief_template(), ensure_ascii=False, indent=2))


@main.command("generate")
@click.argument("brief_json", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
def generate_command(brief_json: Path, output_format: str) -> None:
    """Generate copy from a JSON brief file."""
    brief = brief_from_json_file(str(brief_json))
    result = HebrewCopywriterClient().generate_copy(brief)
    _print_result(result, output_format)


@main.command("generate-id")
@click.argument("brief_id")
@click.option("--store-dir", default=".hebrew-copywriter/briefs", show_default=True)
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
def generate_id_command(brief_id: str, store_dir: str, output_format: str) -> None:
    """Generate copy from a saved brief id."""
    brief = load_saved_brief(brief_id, store_dir)
    result = HebrewCopywriterClient().generate_copy(brief)
    _print_result(result, output_format)


def _brief_from_options(
    business_name: str,
    business_type: str,
    offer: str,
    audience: str,
    channel: str,
    register_: str,
    gender: str,
    price: Optional[str],
    include_vat: Optional[bool],
    location: Optional[str],
    deadline: Optional[str],
    proof: Tuple[str, ...],
    cta: Optional[str],
    include_unsubscribe: bool,
    privacy_policy_url: Optional[str],
) -> CopyBrief:
    return CopyBrief(
        business_name=business_name,
        business_type=business_type,
        offer=offer,
        audience=audience,
        channel=Channel(channel),
        register=Register(register_),
        gender_mode=GenderMode(gender),
        price=_decimal_or_none(price),
        include_vat=include_vat,
        location=location,
        deadline=deadline,
        proof_points=list(proof),
        call_to_action=cta,
        include_unsubscribe=include_unsubscribe,
        privacy_policy_url=privacy_policy_url,
    )


_COMMON_OPTIONS = [
    click.option("--business-name", required=True),
    click.option("--business-type", required=True),
    click.option("--offer", required=True),
    click.option("--audience", required=True),
    click.option("--channel", type=click.Choice([item.value for item in Channel]), default="landing_page", show_default=True),
    click.option("--register", "register_", type=click.Choice([item.value for item in Register]), default="warm", show_default=True),
    click.option("--gender", type=click.Choice([item.value for item in GenderMode]), default="neutral", show_default=True),
    click.option("--price", default=None),
    click.option("--include-vat/--exclude-vat", default=None),
    click.option("--location", default=None),
    click.option("--deadline", default=None),
    click.option("--proof", multiple=True),
    click.option("--cta", default=None),
    click.option("--include-unsubscribe/--no-unsubscribe", default=False, show_default=True),
    click.option("--privacy-policy-url", default=None),
]


def apply_common_options(func):
    for option in reversed(_COMMON_OPTIONS):
        func = option(func)
    return func


@main.command("quick")
@apply_common_options
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
def quick_command(**kwargs) -> None:
    """Generate copy from command-line fields."""
    output_format = kwargs.pop("output_format")
    brief = _brief_from_options(**kwargs)
    result = HebrewCopywriterClient().generate_copy(brief)
    _print_result(result, output_format)


@main.command("create-brief")
@apply_common_options
@click.option("--store-dir", default=".hebrew-copywriter/briefs", show_default=True)
def create_brief_command(store_dir: str, **kwargs) -> None:
    """Create a saved brief and print a JSON response with an id."""
    brief = _brief_from_options(**kwargs)
    response = save_brief(brief, store_dir)
    click.echo(json.dumps(response, ensure_ascii=False, indent=2))


@main.command("prompt")
@click.argument("brief_json", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def prompt_command(brief_json: Path) -> None:
    """Build a detailed Hebrew prompt from a JSON brief file."""
    brief = brief_from_json_file(str(brief_json))
    click.echo(HebrewCopywriterClient().build_prompt(brief))


@main.command("check")
@click.argument("text")
@click.option("--channel", type=click.Choice([item.value for item in Channel]), default="landing_page", show_default=True)
def check_command(text: str, channel: str) -> None:
    """Check copy for common Israeli marketing risks."""
    issues = HebrewCopywriterClient().compliance_check(text, Channel(channel))
    if not issues:
        click.echo("לא נמצאו בעיות נפוצות.")
        return
    for issue in issues:
        click.echo(f"- {issue}")


if __name__ == "__main__":
    main()
