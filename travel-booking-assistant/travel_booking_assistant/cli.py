"""Command-line interface for Travel-Booking Assistant."""

from __future__ import annotations

import json
import os
from decimal import Decimal
from typing import Optional

import typer

from .client import (
    CostLine,
    Money,
    TravelBookingClient,
    TravelRequest,
    Traveler,
    TripType,
    cancellation_request,
    duplicate_charge_triage,
    invoice_request_he,
)

app = typer.Typer(help="Travel-booking helper for Israeli domestic and international workflows.")


def _travelers(adults: int, children: int, infants: int) -> list[Traveler]:
    travelers: list[Traveler] = []
    if adults:
        travelers.append(Traveler("adult", adults))
    if children:
        travelers.append(Traveler("child", children))
    if infants:
        travelers.append(Traveler("infant", infants))
    if not travelers:
        travelers = [Traveler("adult", 0)]
    return travelers


def _client(env: str) -> TravelBookingClient:
    rates = {
        "EUR": Decimal(os.getenv("TRAVEL_BOOKING_EUR_ILS", "3.3365")),
        "USD": Decimal(os.getenv("TRAVEL_BOOKING_USD_ILS", "2.8720")),
        "GBP": Decimal(os.getenv("TRAVEL_BOOKING_GBP_ILS", "3.8629")),
    }
    markup = Decimal(os.getenv("TRAVEL_BOOKING_CARD_MARKUP", "2.8"))
    return TravelBookingClient(default_fx_rates=rates, default_card_markup_percent=markup, environment=env)


def _request_from_options(
    trip_type: str,
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    adults: int,
    children: int,
    infants: int,
    business: bool,
    needs_vat_invoice: bool,
    passport_expiry: Optional[str],
    nationality: Optional[str],
    separate_tickets: bool,
    locale: str,
    env: str,
    request_id: Optional[str],
) -> TravelRequest:
    return TravelRequest(
        trip_type=TripType(trip_type),
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travelers=_travelers(adults, children, infants),
        request_id=request_id,
        business=business,
        needs_vat_invoice=needs_vat_invoice,
        passport_expiry=passport_expiry,
        nationality=nationality,
        separate_tickets=separate_tickets,
        locale="he" if locale == "he" else "en",
        environment="production" if env == "production" else "sandbox",
    )


@app.command("create-request")
def create_request_command(
    trip_type: str = typer.Option(..., "--trip-type", help="domestic, international, or mixed"),
    origin: str = typer.Option(..., "--origin"),
    destination: str = typer.Option(..., "--destination"),
    start_date: str = typer.Option(..., "--start-date", help="DD/MM/YYYY"),
    end_date: str = typer.Option(..., "--end-date", help="DD/MM/YYYY"),
    adults: int = typer.Option(1, "--adults", min=0),
    children: int = typer.Option(0, "--children", min=0),
    infants: int = typer.Option(0, "--infants", min=0),
    business: bool = typer.Option(False, "--business"),
    needs_vat_invoice: bool = typer.Option(False, "--needs-vat-invoice"),
    passport_expiry: Optional[str] = typer.Option(None, "--passport-expiry"),
    nationality: Optional[str] = typer.Option(None, "--nationality"),
    separate_tickets: bool = typer.Option(False, "--separate-tickets"),
    locale: str = typer.Option("en", "--locale", help="en or he"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    request = _request_from_options(
        trip_type, origin, destination, start_date, end_date, adults, children, infants,
        business, needs_vat_invoice, passport_expiry, nationality, separate_tickets, locale, env, None
    )
    typer.echo(_client(env).to_json(_client(env).create_request(request)))


@app.command()
def quote(
    trip_type: str = typer.Option(..., "--trip-type", help="domestic, international, or mixed"),
    origin: str = typer.Option(..., "--origin"),
    destination: str = typer.Option(..., "--destination"),
    start_date: str = typer.Option(..., "--start-date", help="DD/MM/YYYY"),
    end_date: str = typer.Option(..., "--end-date", help="DD/MM/YYYY"),
    adults: int = typer.Option(1, "--adults", min=0),
    children: int = typer.Option(0, "--children", min=0),
    infants: int = typer.Option(0, "--infants", min=0),
    business: bool = typer.Option(False, "--business"),
    needs_vat_invoice: bool = typer.Option(False, "--needs-vat-invoice"),
    passport_expiry: Optional[str] = typer.Option(None, "--passport-expiry"),
    nationality: Optional[str] = typer.Option(None, "--nationality"),
    separate_tickets: bool = typer.Option(False, "--separate-tickets"),
    locale: str = typer.Option("en", "--locale", help="en or he"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    request_id: Optional[str] = typer.Option(None, "--request-id"),
    supplier_currency: Optional[str] = typer.Option(None, "--supplier-currency"),
    supplier_amount: Optional[Decimal] = typer.Option(None, "--supplier-amount"),
    fx_rate: Decimal = typer.Option(Decimal("1"), "--fx-rate"),
    card_markup: Decimal = typer.Option(Decimal("0"), "--card-markup"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    request = _request_from_options(
        trip_type, origin, destination, start_date, end_date, adults, children, infants,
        business, needs_vat_invoice, passport_expiry, nationality, separate_tickets, locale, env, request_id
    )
    client = _client(env)
    costs = None
    if supplier_currency and supplier_amount is not None:
        fx = client.convert_to_ils(supplier_amount, supplier_currency, rate_to_ils=fx_rate, card_markup_percent=card_markup)
        costs = [CostLine("Supplier quote", fx.supplier, fx, "User-provided supplier amount.")]
    recommendation = client.build_recommendation(request, costs=costs)
    typer.echo(client.to_json(recommendation) if json_output else recommendation.to_markdown(locale="he" if locale == "he" else "en"))


@app.command("fx")
def fx_command(
    amount: Decimal = typer.Option(..., "--amount"),
    currency: str = typer.Option(..., "--currency"),
    rate: Decimal = typer.Option(..., "--rate-to-ils"),
    card_markup: Decimal = typer.Option(Decimal("0"), "--card-markup"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    quote_obj = _client(env).convert_to_ils(amount, currency, rate_to_ils=rate, card_markup_percent=card_markup)
    typer.echo(json.dumps(quote_obj.as_dict(), ensure_ascii=False, indent=2))


@app.command("invoice-request")
def invoice_request_command(
    booking_reference: str = typer.Option(..., "--booking-reference"),
    business_name: str = typer.Option(..., "--business-name"),
    tax_id: str = typer.Option(..., "--tax-id"),
    email: str = typer.Option(..., "--email"),
) -> None:
    typer.echo(invoice_request_he(booking_reference, business_name, tax_id, email))


@app.command("cancel-message")
def cancel_message_command(
    booking_reference: str = typer.Option(..., "--booking-reference"),
    traveler_name: str = typer.Option(..., "--traveler-name"),
    check_in: str = typer.Option(..., "--check-in"),
) -> None:
    typer.echo(cancellation_request(booking_reference, traveler_name, check_in))


@app.command("duplicate-charge")
def duplicate_charge_command(
    supplier: str = typer.Option(..., "--supplier"),
    amount_a: Decimal = typer.Option(..., "--amount-a"),
    currency_a: str = typer.Option(..., "--currency-a"),
    amount_b: Decimal = typer.Option(..., "--amount-b"),
    currency_b: str = typer.Option(..., "--currency-b"),
) -> None:
    result = duplicate_charge_triage([Money(amount_a, currency_a), Money(amount_b, currency_b)], supplier)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
