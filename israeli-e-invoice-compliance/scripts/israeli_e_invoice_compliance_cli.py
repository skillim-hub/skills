from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

try:
    from .israeli_e_invoice_compliance_client import (
        Environment,
        InvoiceApprovalRequest,
        InvoiceComplianceClient,
        calculate_vat_amount,
        requires_allocation,
        threshold_for,
        validate_invoice_payload,
    )
except ImportError:  # pragma: no cover - direct script execution
    from israeli_e_invoice_compliance_client import (
        Environment,
        InvoiceApprovalRequest,
        InvoiceComplianceClient,
        calculate_vat_amount,
        requires_allocation,
        threshold_for,
        validate_invoice_payload,
    )

app = typer.Typer(help="Validate Israeli Chashbonit Yisrael e-invoice payloads and call allocation APIs.")


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise typer.BadParameter("JSON file must contain an object")
    return data


def _print_json(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


@app.command()
def validate(invoice_file: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Validate invoice JSON locally without making a network call."""
    payload = _load_json(invoice_file)
    issues = validate_invoice_payload(payload)
    if issues:
        _print_json({"valid": False, "issues": issues})
        raise typer.Exit(code=1)
    request = InvoiceApprovalRequest.from_payload(payload)
    _print_json({"valid": True, "needs_allocation": request.needs_allocation()})


@app.command()
def threshold(
    invoice_date: str = typer.Option(..., help="Invoice date as YYYY-MM-DD or DD-MM-YYYY."),
    amount: float = typer.Option(..., help="Amount before VAT."),
    invoice_type: int = typer.Option(305, help="Official document type code."),
    israeli_b2b: bool = typer.Option(True, help="Set false for foreign/customer/non-B2B cases."),
) -> None:
    """Show the applicable threshold and whether allocation is required."""
    required = requires_allocation(
        invoice_type=invoice_type,
        payment_amount=amount,
        invoice_date=invoice_date,
        israeli_b2b=israeli_b2b,
    )
    _print_json(
        {
            "invoice_date": invoice_date,
            "threshold_before_vat": float(threshold_for(invoice_date)),
            "amount_before_vat": amount,
            "invoice_type": invoice_type,
            "requires_allocation": required,
        }
    )


@app.command()
def vat(amount: float = typer.Argument(..., help="Amount before VAT.")) -> None:
    """Calculate Israeli VAT at the current standard rate."""
    vat_amount = calculate_vat_amount(amount)
    _print_json({"amount_before_vat": amount, "vat_rate": 0.18, "vat_amount": float(vat_amount), "total": float(amount + float(vat_amount))})


@app.command()
def approve(
    invoice_file: Path = typer.Argument(..., exists=True, readable=True),
    token: str = typer.Option(..., envvar="ITA_TOKEN", help="Tax Authority access token."),
    environment: Environment = typer.Option(Environment.SANDBOX, help="sandbox or production."),
) -> None:
    """Send an allocation approval request."""
    payload = _load_json(invoice_file)
    request = InvoiceApprovalRequest.from_payload(payload)
    client = InvoiceComplianceClient(access_token=token, environment=environment)
    response = client.request_approval(request)
    _print_json({"approved": response.approved, "confirmation_number": response.confirmation_number, "status": response.status, "message": response.message})


@app.command("multi-approve")
def multi_approve(
    invoice_files: list[Path] = typer.Argument(..., exists=True, readable=True),
    token: str = typer.Option(..., envvar="ITA_TOKEN", help="Tax Authority access token."),
    environment: Environment = typer.Option(Environment.SANDBOX, help="sandbox or production."),
) -> None:
    """Send a batch allocation approval request."""
    requests = [InvoiceApprovalRequest.from_payload(_load_json(path)) for path in invoice_files]
    client = InvoiceComplianceClient(access_token=token, environment=environment)
    _print_json(client.request_multi_approval(requests))


@app.command("details")
def details(
    customer_vat_number: str = typer.Option(..., help="Customer VAT number."),
    confirmation_number: str = typer.Option(..., help="Allocation number."),
    vat_number: Optional[str] = typer.Option(None, help="Supplier VAT number."),
    token: str = typer.Option(..., envvar="ITA_TOKEN", help="Tax Authority access token."),
    environment: Environment = typer.Option(Environment.SANDBOX, help="sandbox or production."),
) -> None:
    """Retrieve invoice details by allocation number."""
    client = InvoiceComplianceClient(access_token=token, environment=environment)
    _print_json(client.get_invoice_details(customer_vat_number=customer_vat_number, confirmation_number=confirmation_number, vat_number=vat_number))


@app.command("confirmation-number")
def confirmation_number(
    customer_vat_number: str = typer.Option(..., help="Customer VAT number."),
    vat_number: str = typer.Option(..., help="Supplier VAT number."),
    payment_amount: float = typer.Option(..., help="Amount before VAT."),
    vat_amount: float = typer.Option(..., help="VAT amount."),
    invoice_date: str = typer.Option(..., help="Invoice date."),
    invoice_reference_number: Optional[str] = typer.Option(None, help="Invoice reference number."),
    token: str = typer.Option(..., envvar="ITA_TOKEN", help="Tax Authority access token."),
    environment: Environment = typer.Option(Environment.SANDBOX, help="sandbox or production."),
) -> None:
    """Retrieve an allocation number by invoice details."""
    client = InvoiceComplianceClient(access_token=token, environment=environment)
    _print_json(
        client.get_confirmation_number(
            customer_vat_number=customer_vat_number,
            vat_number=vat_number,
            payment_amount=payment_amount,
            vat_amount=vat_amount,
            invoice_date=invoice_date,
            invoice_reference_number=invoice_reference_number,
        )
    )


@app.command()
def decision(
    decision_value: str = typer.Argument(..., help="cancel, continue, or further_objection."),
    invoice_id: str = typer.Option(..., help="Original invoice ID."),
    vat_number: str = typer.Option(..., help="Supplier VAT number."),
    accounting_software_number: str = typer.Option(..., help="Software registration number."),
    token: str = typer.Option(..., envvar="ITA_TOKEN", help="Tax Authority access token."),
    environment: Environment = typer.Option(Environment.SANDBOX, help="sandbox or production."),
    user_name: Optional[str] = typer.Option(None, help="Service operator username."),
) -> None:
    """Submit a decision for a held invoice."""
    if decision_value not in {"cancel", "continue", "further_objection"}:
        raise typer.BadParameter("decision must be cancel, continue, or further_objection")
    client = InvoiceComplianceClient(access_token=token, environment=environment)
    _print_json(
        client.submit_decision(
            decision=decision_value,  # type: ignore[arg-type]
            invoice_id=invoice_id,
            vat_number=vat_number,
            accounting_software_number=accounting_software_number,
            user_name=user_name,
        )
    )


if __name__ == "__main__":
    app()
