from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import ExplanationOptions, InvoiceContext, InvoiceExplanationClient, InvoiceLine

app = typer.Typer(
    add_completion=False,
    help="Generate plain-language Hebrew or English explanations for Israeli invoice items.",
)


def _load_json(path: Optional[Path]) -> dict:
    if path is None:
        text = typer.get_text_stream("stdin").read()
        if not text.strip():
            raise typer.BadParameter("Provide --input or pipe a JSON payload to standard input.")
        return json.loads(text)
    return json.loads(path.read_text(encoding="utf-8"))


def _context_from_options(
    payload: dict,
    *,
    language: str,
    env: str,
    business_type: str,
    document_type: str,
) -> InvoiceContext:
    raw = dict(payload.get("context", {}))
    raw.setdefault("language", language)
    raw.setdefault("environment", env)
    raw.setdefault("business_type", business_type)
    raw.setdefault("document_type", document_type)
    raw.setdefault("business_name", os.getenv("FTIE_BUSINESS_NAME"))
    return InvoiceContext(**raw)


def _options_from_payload(payload: dict, *, language: str) -> ExplanationOptions:
    raw = dict(payload.get("options", {}))
    raw.setdefault("language", language)
    return ExplanationOptions(**raw)


@app.command()
def explain(
    input: Optional[Path] = typer.Option(None, "--input", "-i", help="Path to a JSON payload. Reads standard input when omitted."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional path for JSON output."),
    language: str = typer.Option("he", "--language", "-l", help="he or en."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    business_type: str = typer.Option("authorized_dealer", "--business-type", help="authorized_dealer, exempt_dealer, company, nonprofit, or consumer."),
    document_type: str = typer.Option("tax_invoice", "--document-type", help="tax_invoice, invoice_receipt, receipt, credit_note, proforma, or invoice."),
) -> None:
    """Explain all line items in an invoice JSON payload."""
    payload = _load_json(input)
    lines = payload.get("lines")
    if not isinstance(lines, list):
        raise typer.BadParameter("JSON payload must include a lines list.")
    context = _context_from_options(
        payload,
        language=language,
        env=env,
        business_type=business_type,
        document_type=document_type,
    )
    options = _options_from_payload(payload, language=language)
    result = InvoiceExplanationClient().explain_invoice(lines, context, options)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
    else:
        typer.echo(text)


@app.command()
def one(
    description: str = typer.Argument(..., help="Line item description."),
    quantity: str = typer.Option("1", "--quantity", "-q"),
    unit_price: str = typer.Option("0", "--unit-price", "-p"),
    vat_rate: str = typer.Option("18", "--vat-rate"),
    language: str = typer.Option("he", "--language", "-l"),
    env: str = typer.Option("sandbox", "--env"),
    exempt_dealer: bool = typer.Option(False, "--exempt-dealer"),
) -> None:
    """Explain a single invoice line from command-line values."""
    business_type = "exempt_dealer" if exempt_dealer else "authorized_dealer"
    context = InvoiceContext(language=language, environment=env, business_type=business_type)
    options = ExplanationOptions(language=language)
    line = InvoiceLine(description=description, quantity=quantity, unit_price=unit_price, vat_rate=vat_rate)
    result = InvoiceExplanationClient().explain_line(line, context, options)
    typer.echo(result.to_json())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
