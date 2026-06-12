from __future__ import annotations

import json
from typing import Any

import click

from .client import (
    InstallmentCalculationError,
    InstallmentRequest,
    calculate_plan,
    compare_plans,
    estimate_refund,
    gross_from_net,
    format_date_il,
    format_ils,
    money,
    statutory_cancellation_fee_cap,
    vat_components_from_gross,
)


def _request_from_options(**kwargs: Any) -> InstallmentRequest:
    return InstallmentRequest(
        cash_price=kwargs["price"],
        installments=kwargs["installments"],
        down_payment=kwargs.get("down_payment") or "0",
        annual_interest_rate=kwargs.get("annual_rate") or "0",
        upfront_fee=kwargs.get("upfront_fee") or "0",
        upfront_fee_percent=kwargs.get("upfront_fee_percent") or "0",
        per_installment_fee=kwargs.get("per_installment_fee") or "0",
        first_due_date=kwargs.get("first_due_date"),
        payment_day=kwargs.get("payment_day"),
        vat_included=not kwargs.get("vat_excluded", False),
        consumer_context=not kwargs.get("business", False),
        label=kwargs.get("label"),
    )


def _print_schedule(plan: Any) -> None:
    click.echo(plan.disclosure_table())
    click.echo("\nSchedule")
    click.echo("#  Due date    Principal   Interest   Fee      Payment    Balance")
    for line in plan.schedule:
        click.echo(
            f"{line.number:<2} {format_date_il(line.due_date):<10} "
            f"{format_ils(line.principal):>10} "
            f"{format_ils(line.interest):>10} "
            f"{format_ils(line.fee):>8} "
            f"{format_ils(line.payment):>10} "
            f"{format_ils(line.balance):>10}"
        )
    if plan.warnings:
        click.echo("\nWarnings")
        for warning in plan.warnings:
            click.echo(f"- {warning}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True, help="Execution profile label for logs and JSON output.")
@click.pass_context
def main(ctx: click.Context, environment: str) -> None:
    """Calculate Israeli installment plans in shekels."""
    ctx.ensure_object(dict)
    ctx.obj["environment"] = environment


@main.command()
@click.option("--price", required=True, help="Cash price in ILS.")
@click.option("--installments", required=True, type=int, help="Number of monthly payments.")
@click.option("--down-payment", default="0", help="Down payment in ILS.")
@click.option("--annual-rate", default="0", help="Nominal annual interest rate percent.")
@click.option("--upfront-fee", default="0", help="Fixed upfront fee in ILS.")
@click.option("--upfront-fee-percent", default="0", help="Upfront fee percentage of financed amount.")
@click.option("--per-installment-fee", default="0", help="Fixed fee per installment in ILS.")
@click.option("--first-due-date", default=None, help="First due date, DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD.")
@click.option("--payment-day", default=None, type=int, help="Preferred day of month, 1-31.")
@click.option("--vat-excluded", is_flag=True, help="Mark amounts as VAT-exclusive.")
@click.option("--business", is_flag=True, help="Use business context instead of consumer context.")
@click.option("--label", default=None, help="Optional plan label.")
@click.option("--output", "output_format", type=click.Choice(["table", "json"]), default="table", show_default=True)
@click.pass_context
def calculate(ctx: click.Context, **kwargs: Any) -> None:
    """Calculate one installment plan."""
    try:
        plan = calculate_plan(_request_from_options(**kwargs))
    except InstallmentCalculationError as exc:
        raise click.ClickException(f"{exc.code}: {exc.message}") from exc
    if kwargs["output_format"] == "json":
        payload = plan.to_dict()
        payload["environment"] = ctx.obj["environment"]
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_schedule(plan)


@main.command()
@click.option("--price", required=True, help="Cash price in ILS.")
@click.option("--installments", "installment_options", required=True, multiple=True, type=int, help="Repeat for each plan, for example --installments 3 --installments 12.")
@click.option("--annual-rate", "rate_options", multiple=True, default=["0"], help="Repeat to match installment options, or provide one rate for all.")
@click.option("--per-installment-fee", default="0", help="Fixed fee per installment in ILS.")
@click.option("--upfront-fee", default="0", help="Fixed upfront fee in ILS.")
@click.option("--first-due-date", default=None, help="First due date.")
@click.option("--output", "output_format", type=click.Choice(["table", "json"]), default="table", show_default=True)
@click.pass_context
def compare(ctx: click.Context, price: str, installment_options: tuple[int, ...], rate_options: tuple[str, ...], per_installment_fee: str, upfront_fee: str, first_due_date: str | None, output_format: str) -> None:
    """Compare multiple installment counts or rates."""
    if len(rate_options) not in {1, len(installment_options)}:
        raise click.ClickException("Provide one rate for all plans or one rate per installment option")
    requests = []
    for idx, count in enumerate(installment_options):
        rate = rate_options[0] if len(rate_options) == 1 else rate_options[idx]
        requests.append(InstallmentRequest(
            cash_price=price,
            installments=count,
            annual_interest_rate=rate,
            upfront_fee=upfront_fee,
            per_installment_fee=per_installment_fee,
            first_due_date=first_due_date,
            label=f"{count} payments at {rate}%",
        ))
    try:
        plans = compare_plans(requests)
    except InstallmentCalculationError as exc:
        raise click.ClickException(f"{exc.code}: {exc.message}") from exc
    if output_format == "json":
        click.echo(json.dumps({"environment": ctx.obj["environment"], "plans": [plan.to_dict() for plan in plans]}, ensure_ascii=False, indent=2))
    else:
        click.echo("Rank  Installments  Total paid  Finance charge  Regular payment")
        for rank, plan in enumerate(plans, start=1):
            click.echo(f"{rank:<5} {plan.request.installments:<13} {format_ils(plan.total_payments):<11} {format_ils(plan.finance_charge):<15} {format_ils(plan.regular_payment)}")


@main.command()
@click.option("--price", required=True, help="Cash price in ILS.")
@click.option("--installments", required=True, type=int, help="Number of payments in original plan.")
@click.option("--paid", "installments_paid", required=True, type=int, help="Number of installments already paid.")
@click.option("--annual-rate", default="0", help="Nominal annual interest rate percent.")
@click.option("--upfront-fee", default="0", help="Fixed upfront fee in ILS.")
@click.option("--per-installment-fee", default="0", help="Fixed fee per installment in ILS.")
@click.option("--cancellation-fee", default="0", help="Operational cancellation fee estimate.")
@click.pass_context
def refund(ctx: click.Context, **kwargs: Any) -> None:
    """Estimate remaining balance after cancellation."""
    try:
        plan = calculate_plan(_request_from_options(**kwargs))
        result = estimate_refund(plan, kwargs["installments_paid"], kwargs["cancellation_fee"])
    except InstallmentCalculationError as exc:
        raise click.ClickException(f"{exc.code}: {exc.message}") from exc
    result["environment"] = ctx.obj["environment"]
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


@main.command("disclosure-check")
@click.option("--price", required=True, help="Cash price in ILS.")
@click.option("--installments", required=True, type=int, help="Number of monthly payments.")
@click.option("--annual-rate", default="0", help="Nominal annual interest rate percent.")
@click.option("--upfront-fee", default="0", help="Fixed upfront fee in ILS.")
@click.option("--per-installment-fee", default="0", help="Fixed fee per installment in ILS.")
@click.option("--first-due-date", default=None, help="First due date.")
@click.pass_context
def disclosure_check(ctx: click.Context, **kwargs: Any) -> None:
    """Return disclosure checklist JSON."""
    try:
        plan = calculate_plan(_request_from_options(**kwargs))
    except InstallmentCalculationError as exc:
        raise click.ClickException(f"{exc.code}: {exc.message}") from exc
    click.echo(json.dumps({"environment": ctx.obj["environment"], "checks": [check.to_dict() for check in plan.disclosure_checks], "warnings": list(plan.warnings)}, ensure_ascii=False, indent=2))


@main.command("vat")
@click.option("--gross", default=None, help="VAT-inclusive amount in ILS.")
@click.option("--net", default=None, help="VAT-exclusive amount in ILS.")
@click.option("--rate", default="18", help="VAT rate percent. Current Israeli baseline is 18 percent from 01/01/2025.")
@click.pass_context
def vat(ctx: click.Context, gross: str | None, net: str | None, rate: str) -> None:
    """Calculate VAT components for Israeli pricing work."""
    if bool(gross) == bool(net):
        raise click.ClickException("Provide exactly one of --gross or --net")
    try:
        if gross is not None:
            payload = vat_components_from_gross(gross, rate)
        else:
            gross_value = gross_from_net(net, rate)
            payload = vat_components_from_gross(gross_value, rate)
            payload["net_price"] = str(money(net))
        payload["environment"] = ctx.obj["environment"]
    except InstallmentCalculationError as exc:
        raise click.ClickException(f"{exc.code}: {exc.message}") from exc
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@main.command("cancellation-fee-cap")
@click.option("--total", required=True, help="Total transaction amount in ILS.")
@click.pass_context
def cancellation_fee_cap(ctx: click.Context, total: str) -> None:
    """Return the lower of 5 percent of the transaction total or ₪100."""
    try:
        cap = statutory_cancellation_fee_cap(total)
    except InstallmentCalculationError as exc:
        raise click.ClickException(f"{exc.code}: {exc.message}") from exc
    click.echo(json.dumps({"environment": ctx.obj["environment"], "transaction_total": total, "cancellation_fee_cap": str(cap)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
