from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional
import typer
from .client import InvoiceProcessor, ProcessingConfig, format_money, parse_invoice_text

app = typer.Typer(help="Process Israeli invoice OCR text from WhatsApp workflows.", no_args_is_help=True)

def build_config(env: str) -> ProcessingConfig:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    return ProcessingConfig.from_env(env=env)

def _config_from_env(env: str) -> ProcessingConfig:
    return build_config(env)

@app.command()
def parse(path: Path, env: str = typer.Option("sandbox", "--env"), json_output: bool = typer.Option(False, "--json"), ocr_confidence: Optional[float] = None, known_duplicate_key: Optional[str] = typer.Option(None, "--known-duplicate-key")) -> None:
    """Parse a single OCR text fixture."""
    result = InvoiceProcessor(_config_from_env(env)).parse_file(path, ocr_confidence=ocr_confidence, known_duplicate_keys=[known_duplicate_key] if known_duplicate_key else None)
    if json_output:
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    typer.echo(f"Status: {result.status}")
    typer.echo(f"Document type: {result.document_type}")
    typer.echo(f"Vendor: {result.vendor_name}")
    typer.echo(f"Date: {result.issue_date}")
    typer.echo(f"Total: ₪{format_money(result.total_amount)}")
    if result.warnings:
        typer.echo("Warnings: " + ", ".join(result.warnings))
    typer.echo(result.chat_reply_he)

@app.command()
def reply(path: Path, env: str = typer.Option("sandbox", "--env"), lang: str = "he") -> None:
    """Print a chat confirmation message."""
    result = InvoiceProcessor(_config_from_env(env)).parse_file(path)
    typer.echo(result.chat_reply_en if lang.lower().startswith("en") else result.chat_reply_he)

@app.command()
def batch(directory: Path, out: Path = Path("processed"), env: str = typer.Option("sandbox", "--env")) -> None:
    """Parse every .txt file in a directory."""
    if not directory.exists() or not directory.is_dir():
        raise typer.BadParameter(f"Directory does not exist: {directory}")
    out.mkdir(parents=True, exist_ok=True)
    processor = InvoiceProcessor(_config_from_env(env))
    summary: dict[str, int] = {}
    for path in sorted(directory.glob("*.txt")):
        result = processor.parse_file(path)
        summary[result.status] = summary.get(result.status, 0) + 1
        status_dir = out / result.status
        status_dir.mkdir(parents=True, exist_ok=True)
        (status_dir / f"{path.stem}.json").write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(json.dumps(summary, ensure_ascii=False, indent=2))

@app.command("parse-env")
def parse_env(env: str = typer.Option("sandbox", "--env"), source_name: str = "env-ocr.txt", known_duplicate_key: Optional[str] = typer.Option(None, "--known-duplicate-key")) -> None:
    """Parse OCR text from WHATSAPP_INVOICE_OCR_TEXT."""
    result = InvoiceProcessor(_config_from_env(env)).parse_text(os.getenv("WHATSAPP_INVOICE_OCR_TEXT", ""), source_name=source_name, known_duplicate_keys=[known_duplicate_key] if known_duplicate_key else None)
    typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

@app.command()
def demo(env: str = typer.Option("sandbox", "--env")) -> None:
    """Run a bundled sample."""
    text = """א.ב. שירותים בע"מ
ח.פ. 516123456
חשבונית מס/קבלה מס' 8841
תאריך 14/02/2026
סה"כ לפני מע"מ 99.00 ₪
מע"מ 18% 18.00 ₪
סה"כ לתשלום 117.00 ₪
מספר הקצאה 987654321"""
    typer.echo(json.dumps(parse_invoice_text(text).to_dict(), ensure_ascii=False, indent=2))

def main() -> None:
    app()

if __name__ == "__main__":
    main()
