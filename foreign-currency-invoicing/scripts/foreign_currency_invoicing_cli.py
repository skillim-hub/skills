from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from foreign_currency_invoicing_client import (
    ForeignCurrencyInvoiceClient,
    build_boi_rate_url,
    calculate_invoice,
    fetch_rate,
    load_invoice_result,
    load_lines_from_file,
    parse_boi_rate_response,
    sample_lines,
    save_invoice_result,
)


def _store_dir_from_env(env: str) -> Path:
    explicit = os.getenv("FCI_INVOICE_DIR")
    if explicit:
        return Path(explicit)
    return Path(".foreign-currency-invoicing") / env / "invoices"


def _loads_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise click.BadParameter(f"invalid JSON: {exc}") from exc


def _read_lines(lines_json: str | None, lines_file: str | None) -> Any:
    if lines_json and lines_file:
        raise click.UsageError("use either --lines-json or --lines-file, not both")
    if lines_file:
        return load_lines_from_file(lines_file)
    if lines_json:
        return _loads_json(lines_json)
    env_value = os.getenv("FCI_LINES_JSON")
    if env_value:
        return _loads_json(env_value)
    return sample_lines()


def _print_json(payload: Any) -> None:
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def build_cli() -> click.Group:
    group = click.Group(help="Foreign-currency invoicing helper for Israeli VAT calculations.")

    def create(
        env: str,
        currency: str,
        issue_date: str,
        exchange_rate: str | None,
        vat_rate: str | None,
        lines_json: str | None,
        lines_file: str | None,
        round_per_line: bool,
        save: bool,
    ) -> None:
        resolved_currency = currency or os.getenv("FCI_CURRENCY", "USD")
        resolved_date = issue_date or os.getenv("FCI_ISSUE_DATE", "02/06/2026")
        resolved_rate = exchange_rate or os.getenv("FCI_EXCHANGE_RATE")
        if resolved_rate is None and resolved_currency.upper() != "ILS":
            raise click.UsageError("provide --exchange-rate or set FCI_EXCHANGE_RATE for non-ILS invoices")
        lines = _read_lines(lines_json, lines_file)
        result = calculate_invoice(
            lines,
            resolved_currency,
            resolved_date,
            resolved_rate,
            vat_rate=vat_rate or os.getenv("FCI_VAT_RATE"),
            round_per_line=round_per_line,
        )
        output = result.to_dict()
        if save:
            path = save_invoice_result(result, _store_dir_from_env(env))
            output["stored_at"] = str(path)
        _print_json(output)

    create_cmd = click.Command(
        "create",
        callback=create,
        params=[
            click.Option(["--env"], type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True),
            click.Option(["--currency"], default=None, help="ISO currency code. Defaults to FCI_CURRENCY or USD."),
            click.Option(["--issue-date"], default=None, help="DD/MM/YYYY or YYYY-MM-DD. Defaults to FCI_ISSUE_DATE."),
            click.Option(["--exchange-rate"], default=None, help="ILS per currency unit. Defaults to FCI_EXCHANGE_RATE."),
            click.Option(["--vat-rate"], default=None, help="Decimal VAT rate, for example 0.18."),
            click.Option(["--lines-json"], default=None, help="JSON array of invoice lines."),
            click.Option(["--lines-file"], default=None, help="Path to a JSON array of invoice lines."),
            click.Option(["--round-per-line"], is_flag=True, default=False),
            click.Option(["--save/--no-save"], default=True, show_default=True),
        ],
        help="Create a calculated invoice JSON payload and optionally store it locally.",
    )

    def show(env: str, invoice_id: str) -> None:
        _print_json(load_invoice_result(invoice_id, _store_dir_from_env(env)))

    show_cmd = click.Command(
        "show",
        callback=show,
        params=[
            click.Option(["--env"], type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True),
            click.Argument(["invoice_id"]),
        ],
        help="Read a locally stored invoice by id.",
    )

    def rate_url(env: str, currency: str, as_of_date: str) -> None:
        _print_json({"env": env, "url": build_boi_rate_url(currency, as_of_date)})

    rate_url_cmd = click.Command(
        "rate-url",
        callback=rate_url,
        params=[
            click.Option(["--env"], type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True),
            click.Option(["--currency"], default="USD", show_default=True),
            click.Option(["--as-of-date"], default="02/06/2026", show_default=True),
        ],
        help="Print a Bank of Israel representative-rate URL.",
    )

    def parse_rate(env: str, currency: str, payload_file: str) -> None:
        text = Path(payload_file).read_text(encoding="utf-8")
        rate = parse_boi_rate_response(text, currency)
        _print_json({"env": env, "rate": rate.to_dict()})

    parse_rate_cmd = click.Command(
        "parse-rate",
        callback=parse_rate,
        params=[
            click.Option(["--env"], type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True),
            click.Option(["--currency"], default="USD", show_default=True),
            click.Argument(["payload_file"]),
        ],
        help="Parse a saved Bank of Israel JSON or XML response.",
    )

    def get_rate(env: str, currency: str, as_of_date: str) -> None:
        client = ForeignCurrencyInvoiceClient(store_dir=_store_dir_from_env(env))
        rate = fetch_rate(currency, as_of_date, base_url=client.base_url, timeout=client.timeout)
        _print_json({"env": env, "rate": rate.to_dict()})

    get_rate_cmd = click.Command(
        "fetch-rate",
        callback=get_rate,
        params=[
            click.Option(["--env"], type=click.Choice(["sandbox", "production"]), default="production", show_default=True),
            click.Option(["--currency"], default="USD", show_default=True),
            click.Option(["--as-of-date"], default="02/06/2026", show_default=True),
        ],
        help="Fetch a representative rate from the Bank of Israel endpoint.",
    )

    def sample(env: str) -> None:
        _print_json({"env": env, "lines": sample_lines()})

    sample_cmd = click.Command(
        "sample-lines",
        callback=sample,
        params=[click.Option(["--env"], type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)],
        help="Print a sample invoice-line JSON array.",
    )

    group.add_command(create_cmd)
    group.add_command(show_cmd)
    group.add_command(rate_url_cmd)
    group.add_command(parse_rate_cmd)
    group.add_command(get_rate_cmd)
    group.add_command(sample_cmd)
    return group


main = build_cli()


if __name__ == "__main__":
    main()
