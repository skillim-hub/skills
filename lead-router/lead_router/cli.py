from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import LeadRouterClient, default_config, route_csv

app = typer.Typer(help="Route Israeli inbound leads by language, region, product interest, urgency, channel, and consent.")


def _validate_env(env: str) -> str:
    normalized = env.strip().lower()
    if normalized not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be 'sandbox' or 'production'")
    return normalized


def _store_path(value: Optional[Path]) -> Path:
    if value is not None:
        return value
    return Path(os.getenv("LEAD_ROUTER_STORE", ".lead-router-leads.json"))


def _client(config: Optional[Path]) -> LeadRouterClient:
    config_path = config or (Path(os.environ["LEAD_ROUTER_CONFIG"]) if os.getenv("LEAD_ROUTER_CONFIG") else None)
    return LeadRouterClient.from_json_file(config_path) if config_path else LeadRouterClient()


def _print_json(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def route(
    name: Optional[str] = typer.Option(None, help="Lead name."),
    phone: Optional[str] = typer.Option(None, help="Phone number."),
    email: Optional[str] = typer.Option(None, help="Email address."),
    message: Optional[str] = typer.Option(None, help="Free-text message."),
    language: Optional[str] = typer.Option(None, help="Preferred language: HE, EN, RU, AR, or alias."),
    city: Optional[str] = typer.Option(None, help="City or locality."),
    region: Optional[str] = typer.Option(None, help="Region hint."),
    product_interest: Optional[str] = typer.Option(None, "--product", help="Product or service hint."),
    channel: Optional[str] = typer.Option(None, help="Source channel."),
    budget: Optional[float] = typer.Option(None, help="Estimated budget in ILS."),
    urgent: bool = typer.Option(False, "--urgent", help="Mark as urgent."),
    marketing_consent: Optional[bool] = typer.Option(None, "--marketing-consent/--no-marketing-consent", help="Marketing consent flag."),
    config: Optional[Path] = typer.Option(None, help="Optional routing config JSON."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Route a single lead from command-line flags."""
    _validate_env(env)
    client = _client(config)
    result = client.route_lead({
        "name": name,
        "phone": phone,
        "email": email,
        "message": message,
        "language": language,
        "city": city,
        "region": region,
        "product_interest": product_interest,
        "channel": channel,
        "budget": budget,
        "is_urgent": urgent,
        "consent_marketing": marketing_consent,
    })
    _print_json(result.to_dict())


@app.command("route-json")
def route_json(
    payload: str = typer.Argument(..., help="JSON object containing one lead."),
    config: Optional[Path] = typer.Option(None, help="Optional routing config JSON."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Route one lead from a JSON object."""
    _validate_env(env)
    result = _client(config).route_lead(json.loads(payload))
    _print_json(result.to_dict())


@app.command()
def create(
    payload: str = typer.Argument(..., help="JSON object containing one lead."),
    store: Optional[Path] = typer.Option(None, help="Lead store JSON path. Defaults to LEAD_ROUTER_STORE or .lead-router-leads.json."),
    config: Optional[Path] = typer.Option(None, help="Optional routing config JSON."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Create a local lead record and return a lead ID for follow-up commands."""
    selected_env = _validate_env(env)
    response = _client(config).create_lead(json.loads(payload), _store_path(store))
    response["env"] = selected_env
    _print_json(response)


@app.command("route-stored")
def route_stored(
    lead_id: str = typer.Option(..., "--id", help="Lead ID returned by the create command."),
    store: Optional[Path] = typer.Option(None, help="Lead store JSON path. Defaults to LEAD_ROUTER_STORE or .lead-router-leads.json."),
    config: Optional[Path] = typer.Option(None, help="Optional routing config JSON."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Route a previously created local lead record."""
    _validate_env(env)
    result = _client(config).route_stored_lead(lead_id, _store_path(store))
    _print_json(result.to_dict())


@app.command()
def explain(
    payload: str = typer.Argument(..., help="JSON object containing one lead."),
    config: Optional[Path] = typer.Option(None, help="Optional routing config JSON."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Show normalized values, rule scores, and selected route."""
    _validate_env(env)
    _print_json(_client(config).explain(json.loads(payload)))


@app.command()
def batch(
    input_csv: Path = typer.Argument(..., help="Input CSV path."),
    output_jsonl: Path = typer.Argument(..., help="Output JSONL path."),
    config: Optional[Path] = typer.Option(None, help="Optional routing config JSON."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Route a CSV file and write JSONL results."""
    _validate_env(env)
    config_path = config or (Path(os.environ["LEAD_ROUTER_CONFIG"]) if os.getenv("LEAD_ROUTER_CONFIG") else None)
    results = route_csv(input_csv, output_jsonl, config_path)
    _print_json({"routed": len(results), "output_jsonl": str(output_jsonl)})


@app.command("validate-config")
def validate_config(
    config: Path = typer.Argument(..., help="Routing config JSON to validate."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Validate a routing config JSON file."""
    _validate_env(env)
    data = json.loads(config.read_text(encoding="utf-8"))
    errors = LeadRouterClient.validate_config(data)
    if errors:
        for error in errors:
            typer.echo(f"ERROR: {error}", err=True)
        raise typer.Exit(code=1)
    _print_json({"status": "valid"})


@app.command("default-config")
def default_config_command(
    output: Optional[Path] = typer.Option(None, help="Write default config JSON to this path."),
    env: str = typer.Option("sandbox", "--env", help="Runtime profile: sandbox or production."),
) -> None:
    """Print or write the default routing configuration."""
    _validate_env(env)
    text = json.dumps(default_config(), ensure_ascii=False, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
        _print_json({"status": "written", "output": str(output)})
    else:
        typer.echo(text)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
