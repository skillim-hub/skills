"""Command-line interface for the Bituach Leumi payment scheduler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from . import client


def _environment(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"sandbox", "production"}:
        raise click.BadParameter("must be sandbox or production")
    return normalized


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--env", "environment", default="sandbox", show_default=True, callback=lambda _, __, v: _environment(v), help="Execution context label stored in JSON records.")
@click.version_option(client.VERSION)
@click.pass_context
def cli(ctx: click.Context, environment: str) -> None:
    """Create payment schedules, reminders, and exports for Bituach Leumi payments."""
    ctx.ensure_object(dict)
    ctx.obj["environment"] = environment


def _build_plan(
    payer_name: str,
    payer_type: str,
    start_month: str,
    months: int,
    income: float | None,
    payroll: float | None,
    amount: float | None,
    due_day: int,
    adjust: str,
    holiday: tuple[str, ...],
    reminder_days: str,
) -> client.PaymentPlan:
    holidays = frozenset(client.parse_date(item) for item in holiday)
    profile = client.BusinessProfile(
        payer_name=payer_name,
        business_type=client.parse_business_type(payer_type),
        monthly_income_nis=income,
        monthly_payroll_nis=payroll,
        amount_override_nis=amount,
    )
    options = client.ScheduleOptions(
        start_month=client.first_day_of_month(client.parse_date(start_month)),
        months=months,
        due_day=due_day,
        adjustment_policy=client.parse_adjustment_policy(adjust),
        holidays=holidays,
        reminder_days_before=client.parse_int_list(reminder_days),
    )
    return client.generate_payment_plan(profile, options)


def _render_plan(plan_obj: client.PaymentPlan, output_format: str) -> str:
    if output_format == "json":
        return client.to_json(plan_obj)
    if output_format == "csv":
        return client.to_csv(plan_obj)
    if output_format == "ics":
        return client.to_ics(plan_obj)
    return client.to_text(plan_obj)


def _write_or_echo(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
        click.echo(f"Wrote output to {output}")
    else:
        click.echo(content, nl=False)


COMMON_OPTIONS = [
    click.option("--payer-name", default="payer", show_default=True, help="Name shown in exports."),
    click.option("--payer-type", default="self-employed", type=click.Choice(["self-employed", "employer", "small-business", "consumer"]), show_default=True),
    click.option("--start-month", required=True, help="Coverage month: YYYY-MM, YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY."),
    click.option("--months", default=12, show_default=True, type=click.IntRange(1, 60)),
    click.option("--income", type=float, help="Monthly self-employed income estimate in NIS."),
    click.option("--payroll", type=float, help="Monthly payroll estimate in NIS for employer schedules."),
    click.option("--amount", type=float, help="Override monthly amount in NIS."),
    click.option("--due-day", default=15, show_default=True, type=click.IntRange(1, 28)),
    click.option("--adjust", default="next-business-day", type=click.Choice(["next-business-day", "previous-business-day", "keep-date"]), show_default=True),
    click.option("--holiday", multiple=True, help="Additional non-business date: YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY."),
    click.option("--reminder-days", default="14,7,3,1", show_default=True, help="Comma-separated reminder offsets."),
]


def apply_common_options(function: Any) -> Any:
    for option in reversed(COMMON_OPTIONS):
        function = option(function)
    return function


@cli.command("plan")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json", "csv", "ics"]))
@click.option("--output", type=click.Path(dir_okay=False, writable=True), help="Write output to file.")
@apply_common_options
def plan(**kwargs: Any) -> None:
    """Generate a schedule for monthly obligations."""
    try:
        output_format = kwargs.pop("output_format")
        output = kwargs.pop("output")
        plan_obj = _build_plan(**kwargs)
        _write_or_echo(_render_plan(plan_obj, output_format), output)
    except client.SchedulerError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("create")
@click.option("--storage-dir", default=".bituach-leumi-payment-scheduler", show_default=True, type=click.Path(file_okay=False, writable=True), help="Directory for local plan records.")
@apply_common_options
@click.pass_context
def create(ctx: click.Context, storage_dir: str, **kwargs: Any) -> None:
    """Create a local JSON plan record and print a response containing plan_id."""
    try:
        plan_obj = _build_plan(**kwargs)
        environment = ctx.obj.get("environment", "sandbox") if ctx.obj else "sandbox"
        path = client.save_plan_record(plan_obj, storage_dir, environment=environment)
        record = client.plan_record(plan_obj, environment=environment)
        response = {
            "plan_id": record["plan_id"],
            "environment": environment,
            "path": str(path),
            "first_adjusted_due_date": plan_obj.obligations[0].adjusted_due_date.isoformat() if plan_obj.obligations else None,
            "obligation_count": len(plan_obj.obligations),
        }
        click.echo(json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True))
    except client.SchedulerError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("show")
@click.argument("plan_id")
@click.option("--storage-dir", default=".bituach-leumi-payment-scheduler", show_default=True, type=click.Path(file_okay=False), help="Directory for local plan records.")
@click.option("--format", "output_format", default="json", type=click.Choice(["text", "json", "csv", "ics"]))
def show(plan_id: str, storage_dir: str, output_format: str) -> None:
    """Show a saved plan record by id."""
    try:
        record = client.load_plan_record(plan_id, storage_dir)
        if output_format == "json":
            click.echo(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
            return
        plan_obj = client.plan_from_record(record)
        click.echo(_render_plan(plan_obj, output_format), nl=False)
    except client.SchedulerError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("next-due")
@apply_common_options
def next_due(**kwargs: Any) -> None:
    """Print the next unpaid obligation in text form."""
    try:
        plan_obj = _build_plan(**kwargs)
        due = client.next_due_obligation(plan_obj)
        if due is None:
            click.echo("No future due date in generated range.")
            return
        click.echo(f"{due.adjusted_due_date.isoformat()} {client.format_nis(due.amount_nis)} {due.obligation_id}")
    except client.SchedulerError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("validate")
@click.option("--config", type=click.Path(exists=True, dir_okay=False), required=True, help="JSON config with profile/options.")
def validate(config: str) -> None:
    """Validate a JSON config and print the first generated obligation."""
    try:
        data = json.loads(Path(config).read_text(encoding="utf-8"))
        plan_obj = client.plan_from_mapping(data)
        first = plan_obj.obligations[0]
        click.echo(f"Valid: {first.obligation_id} due {first.adjusted_due_date.isoformat()}")
    except (json.JSONDecodeError, OSError, client.SchedulerError) as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
