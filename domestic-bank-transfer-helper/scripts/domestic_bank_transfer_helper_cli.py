from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from domestic_bank_transfer_helper_client import (
    RuntimeEnvironment,
    TransferRequest,
    TransferValidationError,
    build_bank_form_payload,
    create_transfer_record,
    format_report,
    get_transfer_record,
    list_transfer_records,
    load_transfers_csv,
    record_payload,
    validate_transfer,
    validate_transfers,
)


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _env_default() -> str:
    return os.getenv("DOMESTIC_TRANSFER_ENV", RuntimeEnvironment.SANDBOX.value)


def _storage_default() -> str:
    return os.getenv("DOMESTIC_TRANSFER_STATE_DIR", ".domestic-bank-transfer-helper")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--env", "env_name", type=click.Choice([item.value for item in RuntimeEnvironment]), default=_env_default, show_default=True, help="Runtime environment.")
@click.option("--state-dir", type=click.Path(file_okay=False, path_type=Path), default=_storage_default, show_default=True, help="Directory for local transfer records.")
@click.pass_context
def cli(ctx: click.Context, env_name: str, state_dir: Path) -> None:
    """Validate and stage Israeli domestic bank-transfer form data."""
    ctx.obj = {"env": env_name, "state_dir": state_dir}


def _request_from_options(**kwargs: Any) -> TransferRequest:
    return TransferRequest(
        payer_name=kwargs.get("payer_name", ""),
        recipient_name=kwargs["recipient_name"],
        bank_code=kwargs["bank_code"],
        branch_code=kwargs["branch_code"],
        account_number=kwargs["account_number"],
        amount_ils=kwargs["amount_ils"],
        method=kwargs.get("method", "auto"),
        value_date=kwargs.get("value_date"),
        purpose=kwargs.get("purpose", ""),
        reference=kwargs.get("reference", ""),
        urgent=kwargs.get("urgent", False),
        same_day=kwargs.get("same_day", False),
        recurring=kwargs.get("recurring", False),
        bulk_count=kwargs.get("bulk_count", 1),
        approved_by=kwargs.get("approved_by", ""),
        source_document_id=kwargs.get("source_document_id", ""),
    )


def transfer_options(func: Any) -> Any:
    options = [
        click.option("--source-document-id", default="", help="Invoice, payslip, refund, or approval document identifier."),
        click.option("--approved-by", default="", help="Approver name or approval ticket."),
        click.option("--bulk-count", default=1, type=int, show_default=True, help="Number of transfers represented by the request."),
        click.option("--recurring/--not-recurring", default=False, show_default=True, help="Mark the transfer as recurring."),
        click.option("--same-day/--not-same-day", default=False, show_default=True, help="Mark same-day settlement as required."),
        click.option("--urgent/--not-urgent", default=False, show_default=True, help="Mark the transfer as urgent."),
        click.option("--reference", default="", help="Bank reference or internal reference."),
        click.option("--purpose", default="", help="Purpose such as invoice, salary month, rent, refund, or tax payment."),
        click.option("--value-date", default=None, help="Value date in YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY."),
        click.option("--method", type=click.Choice(["auto", "masav", "zahav"]), default="auto", show_default=True),
        click.option("--amount-ils", required=True, help="Amount in Israeli shekels."),
        click.option("--account-number", required=True, help="Recipient account number."),
        click.option("--branch-code", required=True, help="Recipient branch code."),
        click.option("--bank-code", required=True, help="Recipient bank code."),
        click.option("--recipient-name", required=True, help="Recipient legal or account name."),
        click.option("--payer-name", default="", help="Payer name."),
    ]
    for option in reversed(options):
        func = option(func)
    return func


@cli.command()
@transfer_options
@click.option("--language", type=click.Choice(["en", "he"]), default="en", show_default=True)
@click.option("--json-output", is_flag=True, help="Print JSON instead of text.")
@click.pass_context
def validate(ctx: click.Context, language: str, json_output: bool, **kwargs: Any) -> None:
    """Validate a single transfer request."""
    request = _request_from_options(**kwargs)
    report = validate_transfer(request, env=ctx.obj["env"])
    click.echo(_json(report.to_dict()) if json_output else format_report(report, language=language))
    if not report.valid:
        raise click.exceptions.Exit(2)


@cli.command()
@transfer_options
@click.pass_context
def create(ctx: click.Context, **kwargs: Any) -> None:
    """Create a local transfer record and print its identifier."""
    request = _request_from_options(**kwargs)
    record = create_transfer_record(request, env=ctx.obj["env"], storage_dir=ctx.obj["state_dir"])
    click.echo(_json(record))


@cli.command("show")
@click.argument("record_id")
@click.pass_context
def show_record(ctx: click.Context, record_id: str) -> None:
    """Show a previously created transfer record."""
    click.echo(_json(get_transfer_record(record_id, env=ctx.obj["env"], storage_dir=ctx.obj["state_dir"])))


@cli.command("payload")
@click.argument("record_id")
@click.pass_context
def payload_record(ctx: click.Context, record_id: str) -> None:
    """Build a bank-form payload for a previously created valid record."""
    try:
        click.echo(_json(record_payload(record_id, env=ctx.obj["env"], storage_dir=ctx.obj["state_dir"])))
    except TransferValidationError as exc:
        click.echo(_json({"valid": False, "errors": [issue.to_dict() for issue in exc.issues]}))
        raise click.exceptions.Exit(2)


@cli.command("list")
@click.pass_context
def list_records(ctx: click.Context) -> None:
    """List local transfer records for the selected environment."""
    click.echo(_json({"records": list_transfer_records(env=ctx.obj["env"], storage_dir=ctx.obj["state_dir"])}))


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json-output", is_flag=True, help="Print full JSON reports instead of a compact summary.")
@click.pass_context
def batch(ctx: click.Context, csv_path: Path, json_output: bool) -> None:
    """Validate transfers from a CSV file."""
    requests = load_transfers_csv(csv_path)
    reports = validate_transfers(requests, env=ctx.obj["env"])
    if json_output:
        click.echo(_json({"reports": [report.to_dict() for report in reports]}))
        return
    valid_count = sum(1 for report in reports if report.valid)
    click.echo(f"Valid: {valid_count}/{len(reports)}")
    for index, report in enumerate(reports, start=1):
        status = "valid" if report.valid else "fix"
        recipient = report.normalized.get("recipient_name", "")
        method = report.decision.method.value
        click.echo(f"{index}. {status} {recipient} {method}")


@cli.command("direct-payload")
@transfer_options
@click.pass_context
def direct_payload(ctx: click.Context, **kwargs: Any) -> None:
    """Build a payload directly from command-line fields without storing a record."""
    request = _request_from_options(**kwargs)
    try:
        payload = build_bank_form_payload(request, env=ctx.obj["env"])
    except TransferValidationError as exc:
        click.echo(_json({"valid": False, "errors": [issue.to_dict() for issue in exc.issues]}))
        raise click.exceptions.Exit(2)
    click.echo(_json(payload))


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
