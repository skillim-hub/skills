from __future__ import annotations

import json
from typing import Optional

import typer

from .client import Environment, SupportAgentClient, SupportContext, format_analysis

app = typer.Typer(help="Multilingual support helper for Israeli customer service.")


def _client(env: str, business_name: Optional[str]) -> SupportAgentClient:
    return SupportAgentClient(environment=Environment(env), business_name=business_name)


def _context(
    order_id: Optional[str],
    email: Optional[str],
    phone: Optional[str],
    last4: Optional[str],
    business_name: Optional[str],
) -> SupportContext:
    return SupportContext(
        order_id=order_id,
        email=email,
        phone=phone,
        last4=last4,
        business_name=business_name,
    )


@app.command()
def detect(text: str) -> None:
    """Detect the primary language."""

    client = SupportAgentClient()
    typer.echo(client.detect_language(text).value)


@app.command()
def classify(text: str) -> None:
    """Classify support intent."""

    client = SupportAgentClient()
    typer.echo(client.classify_intent(text))


@app.command()
def draft(
    text: str,
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    business_name: Optional[str] = typer.Option(None),
    order_id: Optional[str] = typer.Option(None),
    email: Optional[str] = typer.Option(None),
    phone: Optional[str] = typer.Option(None),
    last4: Optional[str] = typer.Option(None),
) -> None:
    """Draft a structured support response."""

    client = _client(env, business_name)
    context = _context(order_id, email, phone, last4, business_name)
    result = client.draft_reply(text, context)
    typer.echo(json.dumps(format_analysis(result), ensure_ascii=False, indent=2))


@app.command("create")
def create_case(
    text: str,
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    business_name: Optional[str] = typer.Option(None),
    order_id: Optional[str] = typer.Option(None),
    email: Optional[str] = typer.Option(None),
    phone: Optional[str] = typer.Option(None),
    last4: Optional[str] = typer.Option(None),
) -> None:
    """Create a local case and return a case identifier."""

    client = _client(env, business_name)
    context = _context(order_id, email, phone, last4, business_name)
    result = client.create_case(text, context)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("add-message")
def add_message(
    case_id: str,
    text: str,
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    business_name: Optional[str] = typer.Option(None),
    order_id: Optional[str] = typer.Option(None),
    email: Optional[str] = typer.Option(None),
    phone: Optional[str] = typer.Option(None),
    last4: Optional[str] = typer.Option(None),
) -> None:
    """Analyze a follow-up message in an existing case."""

    client = _client(env, business_name)
    context = _context(order_id, email, phone, last4, business_name)
    result = client.add_message(case_id, text, context)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command()
def scenario(
    name: str,
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    business_name: Optional[str] = typer.Option(None),
) -> None:
    """Run a named scenario."""

    examples = {
        "late_delivery": "המשלוח שלי מאחר",
        "duplicate_charge": "I was charged twice",
        "invoice_ru": "Я не получил чек",
        "refund_ar": "أريد استرداد المبلغ",
        "privacy": "Delete all my personal data",
    }
    if name not in examples:
        raise typer.BadParameter("Unknown scenario. Use late_delivery, duplicate_charge, invoice_ru, refund_ar, or privacy.")
    client = _client(env, business_name)
    result = client.draft_reply(examples[name], SupportContext(business_name=business_name))
    typer.echo(json.dumps(format_analysis(result), ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
