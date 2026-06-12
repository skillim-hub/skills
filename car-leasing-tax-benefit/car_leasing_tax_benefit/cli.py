"""Command-line interface for the car leasing tax benefit calculator."""

from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .client import (
    DEFAULT_STORE_PATH,
    DEFAULT_TABLE_PATH,
    CalculatorError,
    CarLeasingTaxBenefitClient,
    InputValidationError,
    RequestStore,
    VehicleInput,
    decimal_value,
)


def environment_defaults(environment: str) -> dict[str, str]:
    """Return safe defaults for a named environment."""
    if environment not in {"sandbox", "production"}:
        raise InputValidationError("environment must be sandbox or production")
    prefix = "CAR_LEASING_TAX_BENEFIT"
    return {
        "environment": environment,
        "tax_year": os.getenv(f"{prefix}_TAX_YEAR", "2026"),
        "tax_rate": os.getenv(f"{prefix}_MARGINAL_TAX_RATE", "0.35"),
        "category": os.getenv(f"{prefix}_CATEGORY", "private_combustion"),
        "private_use_ratio": os.getenv(f"{prefix}_PRIVATE_USE_RATIO", "1"),
        "months": os.getenv(f"{prefix}_MONTHS_AVAILABLE", "12"),
        "price": os.getenv(f"{prefix}_ORIGINAL_PRICE_ILS", "180000"),
        "employee_name": os.getenv(f"{prefix}_EMPLOYEE_NAME", ""),
        "license_plate": os.getenv(f"{prefix}_LICENSE_PLATE", ""),
    }


def build_vehicle_payload(
    price: Optional[str],
    category: Optional[str],
    year: Optional[int],
    tax_rate: Optional[str],
    months: Optional[int],
    private_use_ratio: Optional[str],
    employee_name: Optional[str],
    license_plate: Optional[str],
    environment: str,
) -> dict[str, Any]:
    """Build a vehicle payload from explicit arguments and environment defaults."""
    defaults = environment_defaults(environment)
    return {
        "original_price_ils": price or defaults["price"],
        "category": category or defaults["category"],
        "tax_year": int(year if year is not None else defaults["tax_year"]),
        "employee_marginal_tax_rate": tax_rate or defaults["tax_rate"],
        "months_available": int(months if months is not None else defaults["months"]),
        "private_use_ratio": private_use_ratio or defaults["private_use_ratio"],
        "employee_name": employee_name or defaults["employee_name"] or None,
        "license_plate": license_plate or defaults["license_plate"] or None,
    }


def read_json_payload(path_or_inline: str) -> Any:
    """Load a JSON payload from a path or inline JSON string."""
    possible = Path(path_or_inline)
    if possible.exists():
        return json.loads(possible.read_text(encoding="utf-8"))
    return json.loads(path_or_inline)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Calculate Israeli Shovi Rechev imputed value for company cars.")
    parser.add_argument("--table", default=str(DEFAULT_TABLE_PATH), help="Path to tax_authority_tables.json")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CAR_LEASING_TAX_BENEFIT_ENV", "sandbox"))
    parser.add_argument("--store", default=str(DEFAULT_STORE_PATH), help="Path to local request store JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a stored calculation request and return its id")
    create.add_argument("--price")
    create.add_argument("--category")
    create.add_argument("--year", type=int)
    create.add_argument("--tax-rate")
    create.add_argument("--months", type=int)
    create.add_argument("--private-use-ratio")
    create.add_argument("--employee-name")
    create.add_argument("--license-plate")

    calc = sub.add_parser("calculate", help="Calculate one vehicle or a stored request")
    calc.add_argument("--request-id", help="Request id returned by create")
    calc.add_argument("--price")
    calc.add_argument("--category")
    calc.add_argument("--year", type=int)
    calc.add_argument("--tax-rate")
    calc.add_argument("--months", type=int)
    calc.add_argument("--private-use-ratio")
    calc.add_argument("--employee-name")
    calc.add_argument("--license-plate")
    calc.add_argument("--json", action="store_true", help="Print JSON result")

    batch = sub.add_parser("batch", help="Calculate vehicles from a JSON file")
    batch.add_argument("input", help="JSON list of vehicle payloads")
    batch.add_argument("--output-csv", help="Optional CSV output path")
    batch.add_argument("--json", action="store_true", help="Print JSON result")

    categories = sub.add_parser("categories", help="List supported categories")
    categories.add_argument("--year", type=int, default=2026)
    return parser


def run_command(args: argparse.Namespace) -> int:
    """Execute a parsed command."""
    client = CarLeasingTaxBenefitClient(args.table)

    if args.command == "categories":
        print(json.dumps(client.categories(args.year), ensure_ascii=False, indent=2))
        return 0

    if args.command == "create":
        payload = build_vehicle_payload(
            args.price,
            args.category,
            args.year,
            args.tax_rate,
            args.months,
            args.private_use_ratio,
            args.employee_name,
            args.license_plate,
            args.env,
        )
        record = RequestStore(args.store).create(payload, environment=args.env)
        print(json.dumps({"id": record["id"], "environment": record["environment"], "vehicle": record["vehicle"]}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "calculate":
        if args.request_id:
            result = client.calculate_request_id(args.request_id, args.store)
        else:
            payload = build_vehicle_payload(
                args.price,
                args.category,
                args.year,
                args.tax_rate,
                args.months,
                args.private_use_ratio,
                args.employee_name,
                args.license_plate,
                args.env,
            )
            result = client.calculate(payload)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Monthly imputed value: ₪{result.monthly_imputed_value_ils}")
            print(f"Annual imputed value: ₪{result.annual_imputed_value_ils}")
            print(f"Estimated monthly tax cost: ₪{result.estimated_monthly_tax_cost_ils}")
        return 0

    if args.command == "batch":
        payload = read_json_payload(args.input)
        if not isinstance(payload, list):
            raise InputValidationError("Batch input must be a JSON list")
        results = client.calculate_many(payload)
        if args.output_csv:
            client.export_csv(results, args.output_csv)
        if args.json or not args.output_csv:
            print(json.dumps([item.to_dict() for item in results], ensure_ascii=False, indent=2))
        else:
            print(f"Wrote {len(results)} rows to {args.output_csv}")
        return 0

    raise InputValidationError(f"Unknown command: {args.command}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_command(args)
    except CalculatorError as exc:
        print(f"error: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
