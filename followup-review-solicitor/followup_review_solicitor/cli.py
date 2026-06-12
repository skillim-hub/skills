from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    Channel,
    ConsentStatus,
    EventType,
    FollowupRequest,
    FollowupSolicitorClient,
    Sentiment,
    Urgency,
    create_request_record,
    load_request_record,
    load_requests_from_json,
    normalize_israeli_mobile,
    plans_to_json,
)


app = typer.Typer(help="Generate Hebrew follow-up and review request plans for Israeli audiences.")


def build_request(
    *,
    business_name: str,
    event_type: str,
    event_date: str,
    channel: str,
    customer_name: Optional[str],
    sentiment: str,
    consent_status: str,
    review_url: Optional[str],
    payment_url: Optional[str],
    amount_ils: Optional[float],
    due_date: Optional[str],
    period_label: Optional[str],
    appointment_time: Optional[str],
    business_type: str,
    phone: Optional[str],
    complaint_open: bool,
    promotional_text: bool,
) -> FollowupRequest:
    return FollowupRequest(
        business_name=business_name,
        customer_name=customer_name,
        event_type=event_type,
        event_date=event_date,
        channel=channel,
        sentiment=sentiment,
        consent_status=consent_status,
        review_url=review_url,
        payment_url=payment_url,
        amount_ils=amount_ils,
        due_date=due_date,
        period_label=period_label,
        appointment_time=appointment_time,
        business_type=business_type,
        phone=phone,
        complaint_open=complaint_open,
        promotional_text=promotional_text,
    )


@app.command()
def create_request(
    business_name: str = typer.Option(..., help="Recognizable business name in Hebrew or brand form."),
    event_type: str = typer.Option(..., help="service_completed, review_request, invoice_due, missing_documents, appointment_reminder, delivery_checkin, consumer_followup"),
    event_date: str = typer.Option(..., help="DD/MM/YYYY"),
    channel: str = typer.Option("whatsapp", help="whatsapp, sms, email, phone_script, crm_task"),
    customer_name: Optional[str] = typer.Option(None, help="Customer first name."),
    sentiment: str = typer.Option("unknown", help="positive, neutral, negative, unknown"),
    consent_status: str = typer.Option("transactional", help="transactional, marketing_opt_in, opted_out, unknown"),
    review_url: Optional[str] = typer.Option(None, help="Public review link."),
    payment_url: Optional[str] = typer.Option(None, help="Payment link."),
    amount_ils: Optional[float] = typer.Option(None, help="Amount in ILS."),
    due_date: Optional[str] = typer.Option(None, help="DD/MM/YYYY due date."),
    period_label: Optional[str] = typer.Option(None, help="Accounting period label, for example מאי 2026."),
    appointment_time: Optional[str] = typer.Option(None, help="Appointment time, for example 10:30."),
    business_type: str = typer.Option("service", help="service, retail, freelancer, accountant, clinic, legal."),
    phone: Optional[str] = typer.Option(None, help="Israeli mobile number for validation."),
    complaint_open: bool = typer.Option(False, help="Block review flow when complaint exists."),
    promotional_text: bool = typer.Option(False, help="Mark message as promotional."),
    directory: Path = typer.Option(Path(".followup-review-solicitor/requests"), help="Directory for saved request records."),
):
    request = build_request(
        business_name=business_name,
        customer_name=customer_name,
        event_type=event_type,
        event_date=event_date,
        channel=channel,
        sentiment=sentiment,
        consent_status=consent_status,
        review_url=review_url,
        payment_url=payment_url,
        amount_ils=amount_ils,
        due_date=due_date,
        period_label=period_label,
        appointment_time=appointment_time,
        business_type=business_type,
        phone=phone,
        complaint_open=complaint_open,
        promotional_text=promotional_text,
    )
    response = create_request_record(request, directory=directory)
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command()
def generate(
    request_id: Optional[str] = typer.Option(None, help="Saved request ID produced by create-request."),
    directory: Path = typer.Option(Path(".followup-review-solicitor/requests"), help="Directory for saved request records."),
    business_name: str = typer.Option("", help="Recognizable business name in Hebrew or brand form."),
    event_type: str = typer.Option("service_completed", help="service_completed, review_request, invoice_due, missing_documents, appointment_reminder, delivery_checkin, consumer_followup"),
    event_date: str = typer.Option("01/01/2026", help="DD/MM/YYYY"),
    channel: str = typer.Option("whatsapp", help="whatsapp, sms, email, phone_script, crm_task"),
    customer_name: Optional[str] = typer.Option(None, help="Customer first name."),
    sentiment: str = typer.Option("unknown", help="positive, neutral, negative, unknown"),
    consent_status: str = typer.Option("transactional", help="transactional, marketing_opt_in, opted_out, unknown"),
    review_url: Optional[str] = typer.Option(None, help="Public review link."),
    payment_url: Optional[str] = typer.Option(None, help="Payment link."),
    amount_ils: Optional[float] = typer.Option(None, help="Amount in ILS."),
    due_date: Optional[str] = typer.Option(None, help="DD/MM/YYYY due date."),
    period_label: Optional[str] = typer.Option(None, help="Accounting period label, for example מאי 2026."),
    appointment_time: Optional[str] = typer.Option(None, help="Appointment time, for example 10:30."),
    business_type: str = typer.Option("service", help="service, retail, freelancer, accountant, clinic, legal."),
    phone: Optional[str] = typer.Option(None, help="Israeli mobile number for validation."),
    complaint_open: bool = typer.Option(False, help="Block review flow when complaint exists."),
    promotional_text: bool = typer.Option(False, help="Mark message as promotional."),
    output: str = typer.Option("json", help="json or text"),
):
    if request_id:
        request = load_request_record(request_id, directory=directory)
    else:
        request = build_request(
            business_name=business_name,
            customer_name=customer_name,
            event_type=event_type,
            event_date=event_date,
            channel=channel,
            sentiment=sentiment,
            consent_status=consent_status,
            review_url=review_url,
            payment_url=payment_url,
            amount_ils=amount_ils,
            due_date=due_date,
            period_label=period_label,
            appointment_time=appointment_time,
            business_type=business_type,
            phone=phone,
            complaint_open=complaint_open,
            promotional_text=promotional_text,
        )
    plan = FollowupSolicitorClient().generate_plan(request)
    if output == "text":
        typer.echo(plan.message_he if plan.should_send else plan.fallback_action)
    else:
        typer.echo(plan.to_json())


@app.command()
def validate_phone(phone: str):
    try:
        typer.echo(normalize_israeli_mobile(phone))
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)


@app.command()
def batch(input_json: Path = typer.Argument(..., exists=True)):
    requests = load_requests_from_json(input_json)
    plans = FollowupSolicitorClient().generate_many(requests)
    typer.echo(plans_to_json(plans))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
