#!/usr/bin/env python3
"""CLI for customer-feedback collection planning and validation."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Optional

import typer

import customer_feedback_collector as C

APP = typer.Typer(help="Plan Hebrew customer-feedback, testimonial, and review requests.")
app = APP


def _business(
    business_name: str,
    city: Optional[str],
    google_place_id: Optional[str],
    facebook_page_url: Optional[str],
    zap_url: Optional[str],
    easy_url: Optional[str],
    midrag_url: Optional[str],
    b144_url: Optional[str],
    custom_review_url: Optional[str],
    private_feedback_url: Optional[str],
):
    return C.BusinessProfile(
        display_name=business_name,
        city=city,
        google_place_id=google_place_id,
        facebook_page_url=facebook_page_url,
        zap_url=zap_url,
        easy_url=easy_url,
        midrag_url=midrag_url,
        b144_url=b144_url,
        custom_review_url=custom_review_url,
        private_feedback_url=private_feedback_url,
    )


@APP.command("sample-message")
def sample_message(
    business_name: str = typer.Option(..., help="Hebrew business name."),
    customer_name: str = typer.Option("דנה כהן", help="Customer name."),
    channel: str = typer.Option("whatsapp", help="whatsapp, email, or sms."),
    platform: str = typer.Option("google", help="google, facebook, zap, easy, midrag, b144, custom."),
    phone: str = typer.Option("050-123-4567", help="Israeli phone for WhatsApp/SMS samples."),
    email: str = typer.Option("dana@example.co.il", help="Email for email samples."),
    city: Optional[str] = typer.Option(None),
    google_place_id: Optional[str] = typer.Option(None),
    facebook_page_url: Optional[str] = typer.Option(None),
    zap_url: Optional[str] = typer.Option(None),
    easy_url: Optional[str] = typer.Option(None),
    midrag_url: Optional[str] = typer.Option(None),
    b144_url: Optional[str] = typer.Option(None),
    custom_review_url: Optional[str] = typer.Option(None),
    private_feedback_url: Optional[str] = typer.Option(None),
    private_first: bool = typer.Option(False, help="Use private feedback URL instead of public review URL."),
):
    """Print one rendered Hebrew message."""

    business = _business(
        business_name,
        city,
        google_place_id,
        facebook_page_url,
        zap_url,
        easy_url,
        midrag_url,
        b144_url,
        custom_review_url,
        private_feedback_url,
    )
    contact = C.Contact(full_name=customer_name, phone=phone, email=email)
    try:
        msg = C.render_message(
            contact,
            business,
            platform=C.ReviewPlatform(platform),
            channel=C.Channel(channel),
            private_first=private_first,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
    if msg.subject:
        typer.echo(f"Subject: {msg.subject}\n")
    typer.echo(msg.body)


@APP.command("validate-message")
def validate_message(
    text: str = typer.Argument(..., help="Message text to validate."),
    channel: str = typer.Option("whatsapp", help="whatsapp, email, or sms."),
    to: str = typer.Option("+972501234567", help="Recipient placeholder."),
    subject: Optional[str] = typer.Option(None),
):
    """Validate Hebrew, unsubscribe, SMS length, incentive risk, and RTL structure."""

    msg = C.Message(channel=C.Channel(channel), to=to, subject=subject, body=text)
    issues = C.validate_message(msg)
    if not issues:
        typer.echo("OK: no issues found")
        return
    for issue in issues:
        typer.echo(f"{issue.severity.value.upper()} {issue.code}: {issue.message}")


@APP.command("plan")
def plan(
    contacts: Path = typer.Option(..., exists=True, readable=True, help="UTF-8 CSV of contacts."),
    business_name: str = typer.Option(..., help="Hebrew business name."),
    channel: Optional[str] = typer.Option(None, help="Force whatsapp, email, or sms."),
    platform: str = typer.Option("google"),
    output: Optional[Path] = typer.Option(None, help="Write JSON plan to this path."),
    city: Optional[str] = typer.Option(None),
    google_place_id: Optional[str] = typer.Option(None),
    facebook_page_url: Optional[str] = typer.Option(None),
    zap_url: Optional[str] = typer.Option(None),
    easy_url: Optional[str] = typer.Option(None),
    midrag_url: Optional[str] = typer.Option(None),
    b144_url: Optional[str] = typer.Option(None),
    custom_review_url: Optional[str] = typer.Option(None),
    private_feedback_url: Optional[str] = typer.Option(None),
    private_first: bool = typer.Option(False),
):
    """Plan a campaign from CSV and print a machine-readable create response."""

    business = _business(
        business_name,
        city,
        google_place_id,
        facebook_page_url,
        zap_url,
        easy_url,
        midrag_url,
        b144_url,
        custom_review_url,
        private_feedback_url,
    )
    loaded = C.read_contacts_csv(contacts)
    chosen_channel = C.Channel(channel) if channel else None
    campaign = C.plan_campaign(
        loaded,
        business,
        platform=C.ReviewPlatform(platform),
        channel=chosen_channel,
        private_first=private_first,
    )
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    text = C.export_plan_json(campaign, output)
    response = {
        "plan_id": plan_id,
        "output": str(output) if output else None,
        "summary": C.summarize_plan(campaign),
    }
    if not output:
        response["items"] = json.loads(text)
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@APP.command("next-safe-time")
def next_safe_time(
    moment: Optional[str] = typer.Argument(None, help="ISO datetime. Defaults to now in Asia/Jerusalem."),
):
    """Print the next default safe Israeli send time."""

    typer.echo(C.next_safe_send_time(moment).isoformat())


@APP.command("send")
def send(
    plan_json: Path = typer.Option(..., exists=True, readable=True, help="Plan JSON returned from the plan command."),
    plan_id: Optional[str] = typer.Option(None, help="Plan identifier returned by the plan command."),
    dry_run: bool = typer.Option(True, help="Keep true unless a custom provider adapter is wired in code."),
):
    """Dry-run send planned messages from a plan JSON file."""

    raw = json.loads(plan_json.read_text(encoding="utf-8"))
    messages = []
    for item in raw:
        message = item.get("message")
        if not message:
            continue
        messages.append(
            C.Message(
                channel=C.Channel(message["channel"]),
                to=message["to"],
                subject=message.get("subject"),
                body=message["body"],
                review_url=message.get("review_url"),
                contact_name=message.get("contact_name"),
            )
        )
    client = C.FeedbackCollectorClient(C.BusinessProfile(display_name="dry-run"), platform=C.ReviewPlatform.CUSTOM)
    results = client.send_sync(messages, dry_run=dry_run)
    response = {"plan_id": plan_id, "result_count": len(results), "results": C.to_jsonable(results)}
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    APP()
