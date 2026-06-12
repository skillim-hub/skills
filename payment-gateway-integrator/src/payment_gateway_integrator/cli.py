"""Command-line helper for the payment gateway integrator."""

from __future__ import annotations

import json
from typing import Any, Mapping

try:
    import click
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install click: pip install click") from exc

from .client import (
    GatewayConfig,
    IsraeliPaymentOrchestrator,
    RefundRequest,
    format_ils,
    load_gateway_config_file,
    nis_to_agorot,
    request_from_dict,
    response_to_dict,
)


def read_json(path: str) -> Mapping[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def echo_json(data: Mapping[str, Any]) -> None:
    click.echo(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Operate a neutral Israeli payment gateway orchestration client."""


@cli.command("init-config")
@click.option("--output", type=click.Path(dir_okay=False), default="config.example.json", show_default=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def init_config(output: str, environment: str) -> None:
    """Write an example gateway configuration file."""
    sandbox = environment == "sandbox"
    endpoint = "https://sandbox.example/grow" if sandbox else "https://api.example/grow"
    data = {
        "environment": environment,
        "gateways": [
            {
                "name": "grow",
                "endpoint_url": endpoint,
                "api_key": "replace-in-secret-manager",
                "terminal_id": "replace-terminal-id",
                "secret": "replace-webhook-secret",
                "sandbox": sandbox,
                "enabled": True,
                "priority": 10,
                "capabilities": ["hosted_checkout", "refund", "partial_refund", "installments", "tokenization", "token_charge", "authorize", "capture"],
                "max_installments": 12,
                "supported_currencies": ["ILS"]
            }
        ]
    }
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    click.echo(output)


@cli.command()
@click.option("--config", "config_path", required=True, type=click.Path(exists=True, dir_okay=False))
def gateways(config_path: str) -> None:
    """List configured gateways and capability flags."""
    configs = load_gateway_config_file(config_path)
    echo_json({
        "gateways": [
            {
                "name": item.normalized_name(),
                "enabled": item.enabled,
                "priority": item.priority,
                "capabilities": sorted(item.capabilities),
                "max_installments": item.max_installments,
                "supported_currencies": sorted(item.supported_currencies),
                "sandbox": item.sandbox,
            }
            for item in configs
        ]
    })


@cli.command()
@click.option("--config", "config_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--request", "request_path", required=True, type=click.Path(exists=True, dir_okay=False))
def charge(config_path: str, request_path: str) -> None:
    """Create a charge or hosted checkout request."""
    configs = load_gateway_config_file(config_path)
    request = request_from_dict(read_json(request_path))
    orchestrator = IsraeliPaymentOrchestrator(configs)
    response = orchestrator.charge(request)
    echo_json(response_to_dict(response))


@cli.command()
@click.option("--config", "config_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--gateway", required=True)
@click.option("--transaction-id", required=True)
@click.option("--amount", required=True, help="Refund amount in NIS, for example 49.90")
@click.option("--reason", default="")
def refund(config_path: str, gateway: str, transaction_id: str, amount: str, reason: str) -> None:
    """Refund a transaction through the original gateway."""
    configs = load_gateway_config_file(config_path)
    request = RefundRequest(transaction_id=transaction_id, amount_agorot=nis_to_agorot(amount), reason=reason)
    orchestrator = IsraeliPaymentOrchestrator(configs)
    response = orchestrator.refund(gateway, request)
    echo_json(response_to_dict(response))


@cli.command()
@click.option("--config", "config_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--gateway", required=True)
@click.option("--transaction-id", required=True)
def status(config_path: str, gateway: str, transaction_id: str) -> None:
    """Query provider transaction status."""
    configs = load_gateway_config_file(config_path)
    orchestrator = IsraeliPaymentOrchestrator(configs)
    response = orchestrator.status(gateway, transaction_id)
    echo_json(response_to_dict(response))


@cli.command("sign-webhook")
@click.option("--config", "config_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--gateway", required=True)
@click.option("--payload", required=True, help="Raw payload string to sign.")
@click.option("--timestamp", default="")
def sign_webhook(config_path: str, gateway: str, payload: str, timestamp: str) -> None:
    """Create an HMAC signature for callback testing."""
    configs = load_gateway_config_file(config_path)
    orchestrator = IsraeliPaymentOrchestrator(configs)
    signature = orchestrator.sign_webhook_payload(gateway, payload.encode("utf-8"), timestamp=timestamp)
    echo_json({"signature": signature})


@cli.command("format-amount")
@click.option("--amount", required=True, help="NIS amount, for example 349.90")
def format_amount(amount: str) -> None:
    """Convert NIS amount to agorot and localized display."""
    agorot = nis_to_agorot(amount)
    echo_json({"amount_agorot": agorot, "display": format_ils(agorot)})


if __name__ == "__main__":
    cli()
