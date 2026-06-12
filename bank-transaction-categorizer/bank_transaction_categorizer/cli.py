from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import json
from pathlib import Path
import sys
from typing import Optional

from .client import (
    BankTransactionCategorizer,
    TransactionCategorizerError,
    create_sample_statement,
    format_decimal,
    parse_israeli_amount,
    resolve_input_id,
    validate_file,
)

try:
    import typer
except Exception:
    typer = None

if typer is not None:
    app = typer.Typer(add_completion=False, help="Categorize Israeli bank transaction exports from CSV files.")

    @app.command("create-sample")
    def create_sample_command(
        output: Path = typer.Option(Path("sample-bank-transactions.csv"), "--output", "-o", help="Sample output path."),
        env: str = typer.Option("sandbox", "--env", help="Environment: sandbox or production."),
    ) -> None:
        response = create_sample_statement(output, env)
        typer.echo(json.dumps(response, ensure_ascii=False, indent=2))

    @app.command("sample")
    def sample_command(
        output: Path = typer.Option(Path("sample-bank-transactions.csv"), "--output", "-o", help="Sample output path."),
        env: str = typer.Option("sandbox", "--env", help="Environment: sandbox or production."),
    ) -> None:
        response = create_sample_statement(output, env)
        typer.echo(json.dumps(response, ensure_ascii=False, indent=2))

    @app.command("categorize")
    def categorize_command(
        input_path: Optional[Path] = typer.Argument(None, help="Input bank statement CSV."),
        input_id: Optional[str] = typer.Option(None, "--input-id", help="Registered input id from create-sample."),
        output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output CSV or JSON path."),
        format: str = typer.Option("csv", "--format", help="Output format: csv or json."),
        rules: Optional[Path] = typer.Option(None, "--rules", help="Optional custom JSON rules."),
        env: str = typer.Option("sandbox", "--env", help="Environment: sandbox or production."),
    ) -> None:
        if input_id:
            resolved_input = resolve_input_id(input_id, env)
        elif input_path:
            resolved_input = input_path
        else:
            raise typer.BadParameter("Pass input_path or --input-id.")
        categorizer = BankTransactionCategorizer.from_rule_file(rules) if rules else BankTransactionCategorizer()
        result = categorizer.categorize_file(resolved_input, output, format)  # type: ignore[arg-type]
        typer.echo(json.dumps({"input": str(resolved_input), "summary": result["summary"]}, ensure_ascii=False, indent=2))

    @app.command("validate")
    def validate_command(
        input_path: Path = typer.Argument(..., help="Input bank statement CSV."),
        env: str = typer.Option("sandbox", "--env", help="Environment: sandbox or production."),
    ) -> None:
        result = validate_file(input_path)
        result["environment"] = env
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))

    @app.command("rules-template")
    def rules_template_command(
        output: Path = typer.Option(Path("custom-rules.json"), "--output", "-o", help="Rules template output path."),
        env: str = typer.Option("sandbox", "--env", help="Environment: sandbox or production."),
    ) -> None:
        template = [
            {
                "id": "example_client_revenue",
                "category": "Income",
                "subcategory": "Client payment",
                "patterns": ["לקוח קבוע", "CLIENT LTD"],
                "direction": "credit",
                "vat_relevant": True,
                "tax_deductibility": "review",
                "confidence": 0.95,
                "priority": 200
            },
            {
                "id": "example_supplier",
                "category": "Professional Services",
                "subcategory": "Consulting",
                "patterns": ["יועץ עסקי"],
                "direction": "debit",
                "vat_relevant": True,
                "tax_deductibility": "likely",
                "confidence": 0.90,
                "priority": 180
            }
        ]
        output.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
        typer.echo(json.dumps({"path": str(output), "environment": env}, ensure_ascii=False, indent=2))

    @app.command("summary")
    def summary_command(
        input_path: Path = typer.Argument(..., help="Categorized CSV or JSON output."),
        env: str = typer.Option("sandbox", "--env", help="Environment: sandbox or production."),
    ) -> None:
        if input_path.suffix.lower() == ".json":
            rows = json.loads(input_path.read_text(encoding="utf-8"))
        else:
            rows = list(csv.DictReader(input_path.read_text(encoding="utf-8-sig").splitlines()))
        totals: dict[str, dict[str, object]] = {}
        for row in rows:
            category = row.get("category", "Unknown")
            amount = parse_israeli_amount(row.get("amount", "0"))
            bucket = totals.setdefault(category, {"count": 0, "total": Decimal("0")})
            bucket["count"] = int(bucket["count"]) + 1
            bucket["total"] = bucket["total"] + amount  # type: ignore[operator]
        response = {
            "environment": env,
            "categories": {
                category: {"count": data["count"], "total": format_decimal(data["total"])}  # type: ignore[arg-type]
                for category, data in sorted(totals.items())
            },
        }
        typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


def argparse_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Categorize Israeli bank transaction exports.")
    sub = parser.add_subparsers(dest="command", required=True)

    for command_name in ("sample", "create-sample"):
        sample_parser = sub.add_parser(command_name)
        sample_parser.add_argument("--output", "-o", default="sample-bank-transactions.csv")
        sample_parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")

    categorize_parser = sub.add_parser("categorize")
    categorize_parser.add_argument("input_path", nargs="?")
    categorize_parser.add_argument("--input-id")
    categorize_parser.add_argument("--output", "-o")
    categorize_parser.add_argument("--format", choices=["csv", "json"], default="csv")
    categorize_parser.add_argument("--rules")
    categorize_parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("input_path")
    validate_parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")

    summary_parser = sub.add_parser("summary")
    summary_parser.add_argument("input_path")
    summary_parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")

    args = parser.parse_args(argv)
    try:
        if args.command in {"sample", "create-sample"}:
            print(json.dumps(create_sample_statement(args.output, args.env), ensure_ascii=False, indent=2))
        elif args.command == "categorize":
            if args.input_id:
                resolved_input = resolve_input_id(args.input_id, args.env)
            elif args.input_path:
                resolved_input = Path(args.input_path)
            else:
                parser.error("categorize requires input_path or --input-id")
            categorizer = BankTransactionCategorizer.from_rule_file(args.rules) if args.rules else BankTransactionCategorizer()
            result = categorizer.categorize_file(resolved_input, args.output, args.format)
            print(json.dumps({"input": str(resolved_input), "summary": result["summary"]}, ensure_ascii=False, indent=2))
        elif args.command == "validate":
            result = validate_file(args.input_path)
            result["environment"] = args.env
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "summary":
            if str(args.input_path).endswith(".json"):
                rows = json.loads(Path(args.input_path).read_text(encoding="utf-8"))
            else:
                rows = list(csv.DictReader(Path(args.input_path).read_text(encoding="utf-8-sig").splitlines()))
            print(json.dumps({"environment": args.env, "rows": len(rows)}, ensure_ascii=False, indent=2))
    except TransactionCategorizerError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    return 0


def main() -> None:
    if typer is not None:
        app()
    else:
        raise SystemExit(argparse_main(sys.argv[1:]))


if __name__ == "__main__":
    main()
