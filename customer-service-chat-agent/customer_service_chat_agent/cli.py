"""Typer command-line interface for the customer-service chat agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from customer_service_chat_agent import (
    CustomerContext,
    CustomerServiceChatAgent,
    Environment,
    classification_to_dict,
    load_business_profile,
    response_to_json,
    ticket_to_dict,
)

app = typer.Typer(help="Hebrew customer-service chat agent CLI.")


def build_agent(profile: Optional[Path] = None) -> CustomerServiceChatAgent:
    """Build an agent from an optional JSON business profile."""
    if profile:
        business = load_business_profile(profile)
        return CustomerServiceChatAgent(business=business)
    return CustomerServiceChatAgent()


def parse_environment(value: str) -> Environment:
    """Parse sandbox or production environment name."""
    if value == "production":
        return Environment.PRODUCTION
    return Environment.SANDBOX


@app.command()
def classify(message: str, profile: Optional[Path] = typer.Option(None, help="Path to business profile JSON.")) -> None:
    """Classify a customer message."""
    agent = build_agent(profile)
    result = agent.classify(message)
    typer.echo(json.dumps(classification_to_dict(result), ensure_ascii=False, indent=2))


@app.command()
def reply(
    message: str,
    profile: Optional[Path] = typer.Option(None, help="Path to business profile JSON."),
    name: Optional[str] = typer.Option(None, help="Customer name."),
    contact: Optional[str] = typer.Option(None, help="Customer contact channel."),
    order_number: Optional[str] = typer.Option(None, help="Order number."),
) -> None:
    """Generate a customer-safe reply."""
    agent = build_agent(profile)
    context = CustomerContext(name=name, contact=contact, order_number=order_number)
    response = agent.reply(message, context)
    typer.echo(response_to_json(response))


@app.command("create-handoff")
def create_handoff(
    message: str,
    profile: Optional[Path] = typer.Option(None, help="Path to business profile JSON."),
    name: Optional[str] = typer.Option(None, help="Customer name."),
    contact: Optional[str] = typer.Option(None, help="Customer contact."),
    order_number: Optional[str] = typer.Option(None, help="Order number."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Create a handoff ticket and print its identifier."""
    agent = build_agent(profile)
    context = CustomerContext(name=name, contact=contact, order_number=order_number)
    ticket = agent.create_ticket(message, context, parse_environment(env))
    typer.echo(json.dumps(ticket_to_dict(ticket), ensure_ascii=False, indent=2))


@app.command("ticket-status")
def ticket_status(ticket_id: str, env: str = typer.Option("sandbox", "--env", help="sandbox or production.")) -> None:
    """Return a deterministic ticket status placeholder for quick-start chaining."""
    typer.echo(json.dumps({
        "ticket_id": ticket_id,
        "environment": parse_environment(env).value,
        "status": "open",
        "customer_safe_message": "הפנייה פתוחה וממתינה לטיפול נציג.",
    }, ensure_ascii=False, indent=2))


SCENARIOS = {
    "hours": "מה שעות הפתיחה היום?",
    "order": "איפה ההזמנה שלי?",
    "refund_damaged": "המוצר הגיע שבור ואני רוצה החזר",
    "invoice": "צריך חשבונית לחברה על הזמנה 10493",
    "privacy": "תמחקו את כל המידע שלי",
    "payment_dispute": "חייבתם אותי פעמיים",
    "accessibility": "האתר לא נגיש עם קורא מסך",
}


@app.command()
def scenario(name: str = typer.Argument(..., help="Scenario name."), env: str = typer.Option("sandbox", "--env", help="sandbox or production.")) -> None:
    """Run a built-in scenario."""
    if name not in SCENARIOS:
        available = ", ".join(sorted(SCENARIOS))
        raise typer.BadParameter(f"Unknown scenario. Available: {available}")
    agent = CustomerServiceChatAgent()
    response = agent.reply(SCENARIOS[name])
    payload = json.loads(response_to_json(response))
    payload["environment"] = parse_environment(env).value
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
