#!/usr/bin/env python3
"""Command-line interface for the social-media-manager helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import click

from social_media_manager_client import (
    BlackoutPeriod,
    Platform,
    PostDraft,
    SocialMediaManagerClient,
    sample_drafts,
)


def _client(avoid_shabbat: bool, blackout_date: tuple[str, ...] = ()) -> SocialMediaManagerClient:
    periods = tuple(BlackoutPeriod(date_iso=value, reason="cli_blackout") for value in blackout_date)
    return SocialMediaManagerClient(avoid_shabbat=avoid_shabbat, blackout_periods=periods)


def _json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Plan, validate and export Israeli social-media schedules."""


@cli.command()
@click.option("--platform", "platforms", multiple=True, type=click.Choice([p.value for p in Platform]), help="Platform. Repeat for multiple platforms.")
@click.option("--days", default=14, show_default=True, type=int, help="Planning horizon.")
@click.option("--business-type", default="עסק מקומי", show_default=True, help="Business type for sample captions.")
@click.option("--start-date", default=None, help="ISO date such as 2026-06-08.")
@click.option("--blackout-date", multiple=True, help="ISO date to block. Repeat as needed.")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution environment label.")
@click.option("--avoid-shabbat/--allow-shabbat", default=True, show_default=True, help="Avoid Friday afternoon through Saturday evening.")
def plan(platforms: tuple[str, ...], days: int, business_type: str, start_date: str | None, blackout_date: tuple[str, ...], environment: str, avoid_shabbat: bool) -> None:
    """Create a sample content plan as JSON."""

    selected = platforms or tuple(p.value for p in Platform)
    manager = _client(avoid_shabbat=avoid_shabbat, blackout_date=blackout_date)
    drafts = sample_drafts(selected, business_type=business_type)
    posts = manager.schedule_posts(drafts, start_date=start_date, days=days)
    click.echo(_json({"environment": environment, "items": [post.to_dict() for post in posts]}))


@cli.command()
@click.option("--platform", required=True, type=click.Choice([p.value for p in Platform]), help="Platform to create for.")
@click.option("--caption", required=True, help="Caption text.")
@click.option("--format", "post_format", default="text", show_default=True, help="Post format.")
@click.option("--media-count", default=0, show_default=True, type=int, help="Approved media assets attached.")
@click.option("--hashtag", "hashtags", multiple=True, help="Hashtag. Repeat as needed.")
@click.option("--cta", default="", help="Call to action.")
@click.option("--start-date", default=None, help="ISO date such as 2026-06-08.")
@click.option("--blackout-date", multiple=True, help="ISO date to block. Repeat as needed.")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution environment label.")
@click.option("--avoid-shabbat/--allow-shabbat", default=True, show_default=True, help="Avoid Friday afternoon through Saturday evening.")
def create(
    platform: str,
    caption: str,
    post_format: str,
    media_count: int,
    hashtags: tuple[str, ...],
    cta: str,
    start_date: str | None,
    blackout_date: tuple[str, ...],
    environment: str,
    avoid_shabbat: bool,
) -> None:
    """Create one scheduled draft and return its local identifier."""

    manager = _client(avoid_shabbat=avoid_shabbat, blackout_date=blackout_date)
    draft = PostDraft(platform=platform, caption=caption, format=post_format, media_count=media_count, hashtags=hashtags, cta=cta)
    posts = manager.schedule_posts([draft], start_date=start_date, days=14)
    if not posts:
        raise click.ClickException("No schedule item was created")
    item = posts[0].to_dict()
    click.echo(_json({"environment": environment, "local_id": item["local_id"], "item": item}))


@cli.command()
@click.option("--source", "source_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path), help="JSON file produced by plan or create.")
@click.option("--local-id", required=True, help="Local identifier returned by create or plan.")
def show(source_path: Path, local_id: str) -> None:
    """Read a JSON plan and show one scheduled post by local identifier."""

    raw = json.loads(source_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "item" in raw:
        items = [raw["item"]]
    elif isinstance(raw, dict) and "items" in raw:
        items = raw["items"]
    elif isinstance(raw, list):
        items = raw
    else:
        raise click.ClickException("Unsupported JSON shape; use output from create or plan")
    for item in items:
        if item.get("local_id") == local_id:
            click.echo(_json({"found": True, "item": item, "next_step": "owner_review"}))
            return
    raise click.ClickException(f"Local ID not found: {local_id}")


@cli.command()
@click.option("--platform", required=True, type=click.Choice([p.value for p in Platform]), help="Platform to validate.")
@click.option("--caption", required=True, help="Caption text.")
@click.option("--format", "post_format", default="text", show_default=True, help="Post format.")
@click.option("--media-count", default=0, show_default=True, type=int, help="Approved media assets attached.")
@click.option("--hashtag", "hashtags", multiple=True, help="Hashtag. Repeat as needed.")
@click.option("--contains-customer-image", is_flag=True, help="Mark customer image consent risk.")
@click.option("--contains-price", is_flag=True, help="Mark price or discount terms risk.")
@click.option("--offer-terms", default="", help="Offer terms, expiry, exclusions or limitations.")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution environment label.")
def validate(
    platform: str,
    caption: str,
    post_format: str,
    media_count: int,
    hashtags: tuple[str, ...],
    contains_customer_image: bool,
    contains_price: bool,
    offer_terms: str,
    environment: str,
) -> None:
    """Validate a caption and return JSON."""

    manager = _client(avoid_shabbat=True)
    draft = PostDraft(
        platform=platform,
        caption=caption,
        format=post_format,
        hashtags=hashtags,
        media_count=media_count,
        contains_customer_image=contains_customer_image,
        contains_price=contains_price,
        offer_terms=offer_terms,
    )
    valid, issues, risk_flags = manager.validate_post(draft)
    payload = {
        "environment": environment,
        "valid": valid,
        "issues": [issue.to_dict() for issue in issues],
        "risk_flags": list(risk_flags),
        "normalized_caption": manager.normalize_caption(caption),
        "hashtags": list(manager.normalize_hashtags(hashtags)),
    }
    click.echo(_json(payload))
    if not valid:
        raise click.exceptions.Exit(2)


@cli.command()
@click.option("--platform", "platforms", multiple=True, type=click.Choice([p.value for p in Platform]), help="Platform. Repeat for multiple platforms.")
@click.option("--days", default=14, show_default=True, type=int)
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]), default="json", show_default=True)
@click.option("--business-type", default="עסק מקומי", show_default=True)
@click.option("--start-date", default=None)
@click.option("--blackout-date", multiple=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution environment label.")
@click.option("--avoid-shabbat/--allow-shabbat", default=True, show_default=True)
def export(
    platforms: tuple[str, ...],
    days: int,
    output_format: str,
    business_type: str,
    start_date: str | None,
    blackout_date: tuple[str, ...],
    environment: str,
    avoid_shabbat: bool,
) -> None:
    """Export a sample plan as JSON or CSV."""

    selected = platforms or tuple(p.value for p in Platform)
    manager = _client(avoid_shabbat=avoid_shabbat, blackout_date=blackout_date)
    drafts = sample_drafts(selected, business_type=business_type)
    posts = manager.schedule_posts(drafts, start_date=start_date, days=days)
    if output_format == "csv":
        click.echo(manager.export_csv(posts))
    else:
        click.echo(_json({"environment": environment, "items": [post.to_dict() for post in posts]}))


@cli.command("hashtags")
@click.argument("tags", nargs=-1)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution environment label.")
def hashtags_command(tags: tuple[str, ...], environment: str) -> None:
    """Sanitize hashtags."""

    manager = _client(avoid_shabbat=True)
    payload = {"environment": environment, "hashtags": list(manager.normalize_hashtags(tags))}
    click.echo(_json(payload))


@cli.command("next-slots")
@click.option("--platform", "platforms", multiple=True, type=click.Choice([p.value for p in Platform]), required=True)
@click.option("--days", default=7, show_default=True, type=int)
@click.option("--start-date", default=None)
@click.option("--blackout-date", multiple=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution environment label.")
@click.option("--avoid-shabbat/--allow-shabbat", default=True, show_default=True)
def next_slots(platforms: tuple[str, ...], days: int, start_date: str | None, blackout_date: tuple[str, ...], environment: str, avoid_shabbat: bool) -> None:
    """Show upcoming recommended slots."""

    manager = _client(avoid_shabbat=avoid_shabbat, blackout_date=blackout_date)
    slots = manager.recommend_slots(platforms, start_date=start_date, days=days)
    payload = {"environment": environment, "items": [slot.to_dict() for slot in slots]}
    click.echo(_json(payload))


def main(argv: Sequence[str] | None = None) -> int:
    try:
        cli.main(args=list(argv) if argv is not None else None, prog_name="social-media-manager-cli", standalone_mode=True)
        return 0
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
