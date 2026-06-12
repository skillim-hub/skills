#!/usr/bin/env python3
"""Command-line interface for the Hebrew sales chatbot helper."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional

try:
    import typer
except Exception:  # noqa: BLE001 - argparse fallback keeps the CLI usable without optional packages
    typer = None

from sales_chatbot_client import (
    CustomerContext,
    SalesChatbotClient,
    load_environment_defaults,
    sample_catalog,
    validate_catalog_data,
)


def _read_json(path: Optional[Path]) -> Any:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_catalog(catalog: Optional[Path]) -> SalesChatbotClient:
    env_catalog = os.environ.get("SALES_CHATBOT_CATALOG")
    selected = catalog or (Path(env_catalog) if env_catalog else None)
    return SalesChatbotClient.from_json(selected) if selected else SalesChatbotClient(sample_catalog())


def _resolve_context(context: Optional[Path], env: str) -> CustomerContext:
    env_context = os.environ.get("SALES_CHATBOT_CONTEXT")
    selected = context or (Path(env_context) if env_context else None)
    raw = _read_json(selected) or {}
    raw.setdefault("channel", os.environ.get("SALES_CHATBOT_CHANNEL", "whatsapp"))
    raw.setdefault("environment", env)
    return CustomerContext.from_mapping(raw)


def _emit_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


if typer is not None:
    app = typer.Typer(help="Hebrew sales chatbot helper for Israeli pricing, upsell, cross-sell, and tashlumim.")

    def _env_option(value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"sandbox", "production"}:
            raise typer.BadParameter("Use sandbox or production.")
        return normalized

    def chat(
        message: str = typer.Argument(..., help="Hebrew customer message."),
        env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production."),
        catalog: Optional[Path] = typer.Option(None, "--catalog", "-c", help="Catalog JSON path."),
        context: Optional[Path] = typer.Option(None, "--context", help="Customer context JSON path."),
        json_output: bool = typer.Option(False, "--json", help="Print structured JSON."),
    ) -> None:
        """Generate one Hebrew response."""
        bot = _resolve_catalog(catalog)
        ctx = _resolve_context(context, env)
        response = bot.recommend(message, ctx)
        if json_output:
            payload = response.to_dict()
            payload["environment"] = env
            _emit_json(payload)
        else:
            typer.echo(response.reply_he)

    def create(
        message: str = typer.Argument(..., help="Hebrew customer message."),
        env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production."),
        catalog: Optional[Path] = typer.Option(None, "--catalog", "-c", help="Catalog JSON path."),
        context: Optional[Path] = typer.Option(None, "--context", help="Customer context JSON path."),
        json_output: bool = typer.Option(True, "--json/--text", help="Print structured JSON by default."),
    ) -> None:
        """Create a quote-like recommendation and return a reusable quote_id."""
        bot = _resolve_catalog(catalog)
        ctx = _resolve_context(context, env)
        response = bot.recommend(message, ctx)
        payload = response.to_dict()
        payload["environment"] = env
        payload["status"] = "created"
        if json_output:
            _emit_json(payload)
        else:
            typer.echo(response.reply_he)
            typer.echo(f"quote_id={response.quote_id}")

    def quote_status(
        quote_id: str = typer.Argument(..., help="Quote ID returned by create."),
        env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production."),
    ) -> None:
        """Return a deterministic local quote status payload."""
        _emit_json({"quote_id": quote_id, "environment": env, "status": "draft", "next_step": "confirm stock, final price, delivery, and invoice details"})

    def quote(
        message: str = typer.Argument(..., help="Hebrew customer message."),
        env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production."),
        catalog: Optional[Path] = typer.Option(None, "--catalog", "-c", help="Catalog JSON path."),
        context: Optional[Path] = typer.Option(None, "--context", help="Customer context JSON path."),
    ) -> None:
        """Generate a quote document in plain text."""
        bot = _resolve_catalog(catalog)
        ctx = _resolve_context(context, env)
        typer.echo(bot.make_quote(bot.recommend(message, ctx)))

    def validate_catalog(catalog: Path = typer.Argument(..., help="Catalog JSON path.")) -> None:
        """Validate catalog references, prices, and installments."""
        data = json.loads(catalog.read_text(encoding="utf-8"))
        products = data.get("products", data) if isinstance(data, dict) else data
        errors = validate_catalog_data(products)
        if errors:
            for error in errors:
                typer.echo(f"ERROR: {error}")
            raise typer.Exit(code=1)
        typer.echo("Catalog is valid.")

    def simulate(
        env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production."),
        catalog: Optional[Path] = typer.Option(None, "--catalog", "-c", help="Catalog JSON path."),
    ) -> None:
        """Run a built-in scenario set."""
        bot = _resolve_catalog(catalog)
        messages = [
            "שלום, יש CRM לעסק קטן?",
            "כמה עולה CRM ואפשר בתשלומים?",
            "אני רוצה להזמין",
            "מה לגבי אחריות?",
        ]
        for message in messages:
            typer.echo(f"\nלקוח: {message}")
            typer.echo(bot.recommend(message, {"has_marketing_consent": True, "preferred_installments": 3, "channel": env}).reply_he)

    def async_chat(
        message: str = typer.Argument(..., help="Hebrew customer message."),
        env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production."),
    ) -> None:
        """Generate a response through the async client method."""
        async def _run() -> None:
            bot = SalesChatbotClient(sample_catalog())
            response = await bot.recommend_async(message, {"has_marketing_consent": True, "channel": env})
            typer.echo(response.reply_he)

        asyncio.run(_run())

    def env_info(env: str = typer.Option("sandbox", "--env", callback=_env_option, help="sandbox or production.")) -> None:
        """Print resolved environment defaults without exposing secrets."""
        _emit_json(load_environment_defaults(env))

    app.command()(chat)
    app.command()(create)
    app.command("quote-status")(quote_status)
    app.command()(quote)
    app.command("validate-catalog")(validate_catalog)
    app.command()(simulate)
    app.command("async-chat")(async_chat)
    app.command("env-info")(env_info)
else:
    app = None

    def _fallback() -> None:
        import argparse

        parser = argparse.ArgumentParser(description="Hebrew sales chatbot helper")
        parser.add_argument("message")
        parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args()
        bot = SalesChatbotClient(sample_catalog())
        response = bot.recommend(args.message, {"has_marketing_consent": True, "channel": args.env})
        print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2, default=str) if args.json else response.reply_he)


def main() -> None:
    if typer is None:
        _fallback()
    else:
        app()


if __name__ == "__main__":
    main()
