"""Typer CLI for the prepayment/deposit handler."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer

from prepayment_deposit_handler_client import (
    AsyncPrepaymentDepositClient,
    BusinessType,
    DepositNature,
    LineItem,
    PaymentMethod,
    PrepaymentDepositClient,
)

app = typer.Typer(
    name="prepayment-deposit-handler",
    help="CLI helper for Israeli deposits, advances, receipts, and final invoice settlement.",
    no_args_is_help=True,
)


def _print_json(obj: object) -> None:
    data = obj.as_dict() if hasattr(obj, "as_dict") else obj
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


@app.command()
def classify(
    nature: DepositNature = typer.Option(..., help="Deposit nature."),
    business_type: BusinessType = typer.Option(BusinessType.VAT_REGISTERED, help="Business tax/accounting type."),
    refundable: bool = typer.Option(False, help="Whether the amount is refundable."),
    customer_has_invoice_requirement: bool = typer.Option(False, help="Whether customer demands VAT invoice documentation."),
) -> None:
    """Recommend documents and controls for the deposit event."""
    client = PrepaymentDepositClient()
    _print_json(
        client.classify(
            nature,
            business_type,
            refundable=refundable,
            customer_has_invoice_requirement=customer_has_invoice_requirement,
        )
    )


@app.command()
def settle(
    line: list[str] = typer.Option(..., "--line", help="description:quantity:unit_price_ex_vat[:vat_rate]"),
    deposit: str = typer.Option("0.00", help="Deposit amount to apply."),
    currency: str = typer.Option("ILS", help="Currency code."),
    business_type: BusinessType = typer.Option(BusinessType.VAT_REGISTERED, help="Business tax/accounting type."),
    vat_rate: str = typer.Option("0.18", help="VAT rate override, e.g. 0.18."),
    deposit_already_tax_invoiced: bool = typer.Option(False, help="Mark if deposit already had VAT invoice treatment."),
    deposit_reference: Optional[str] = typer.Option(None, help="Deposit ID or receipt reference to carry into settlement output."),
) -> None:
    """Calculate final invoice settlement after applying a deposit."""
    items: list[LineItem] = []
    for raw in line:
        parts = raw.split(":")
        if len(parts) not in (3, 4):
            raise typer.BadParameter("Each --line must be description:quantity:unit_price_ex_vat[:vat_rate]")
        desc, qty, price = parts[:3]
        rate = parts[3] if len(parts) == 4 else vat_rate
        items.append(LineItem(desc, qty, price, rate))
    client = PrepaymentDepositClient()
    _print_json(
        client.settle(
            items,
            deposit,
            currency=currency,
            business_type=business_type,
            vat_rate_override=vat_rate,
            deposit_already_tax_invoiced=deposit_already_tax_invoiced,
            deposit_reference=deposit_reference,
        )
    )


@app.command()
def record(
    deposit_id: str = typer.Option(...),
    contract_id: str = typer.Option(...),
    received_date: str = typer.Option(..., help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY."),
    amount: str = typer.Option(...),
    payer_name: str = typer.Option(...),
    payee_name: str = typer.Option(...),
    nature: DepositNature = typer.Option(...),
    payment_method: PaymentMethod = typer.Option(PaymentMethod.BANK_TRANSFER),
    currency: str = typer.Option("ILS"),
    refundable: bool = typer.Option(False),
    applied_amount: str = typer.Option("0.00"),
    payer_tax_id: Optional[str] = typer.Option(None),
    payee_tax_id: Optional[str] = typer.Option(None),
    reference: Optional[str] = typer.Option(None),
    notes: Optional[str] = typer.Option(None),
    output_csv: Optional[Path] = typer.Option(None, help="Optional path to export one-row CSV."),
) -> None:
    """Create a validated deposit record."""
    client = PrepaymentDepositClient()
    rec = client.create_record(
        deposit_id=deposit_id,
        contract_id=contract_id,
        received_date=received_date,
        amount=amount,
        payer_name=payer_name,
        payee_name=payee_name,
        nature=nature,
        payment_method=payment_method,
        currency=currency,
        refundable=refundable,
        applied_amount=applied_amount,
        payer_tax_id=payer_tax_id,
        payee_tax_id=payee_tax_id,
        reference=reference,
        notes=notes,
    )
    if output_csv:
        path = client.export_records_csv([rec], output_csv)
        typer.echo(str(path))
    else:
        _print_json(rec)


@app.command("async-demo")
def async_demo() -> None:
    """Run the async facade with a sample final settlement."""
    async def _run() -> None:
        client = AsyncPrepaymentDepositClient()
        result = await client.settle([LineItem("שירות ייעוץ", 1, "1000")], "200")
        _print_json(result)

    asyncio.run(_run())


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":
    main()
