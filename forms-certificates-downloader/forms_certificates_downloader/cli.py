"""Command-line interface for public form and certificate downloads."""
from __future__ import annotations

import json
from typing import Optional

import click

from .client import FormsCertificatesClient, load_registry, validate_mikud, validate_teudat_zehut, normalize_israeli_phone


def _emit_json(value: object) -> None:
    click.echo(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _client(download_dir: str, registry: Optional[str], manifest: Optional[str], env: str) -> FormsCertificatesClient:
    kwargs = {}
    if registry:
        kwargs["registry"] = load_registry(registry)
    return FormsCertificatesClient(download_dir=download_dir, manifest_path=manifest, env=env, **kwargs)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("2.2.0")
def cli() -> None:
    """Download and version-track public Israeli forms and certificates."""


_common_options = [
    click.option("--env", type=click.Choice(["sandbox", "production"]), default="production", show_default=True),
    click.option("--download-dir", default="downloads", show_default=True, help="Local download directory."),
    click.option("--registry", type=click.Path(exists=True, dir_okay=False), help="Custom portal registry JSON."),
    click.option("--manifest", type=click.Path(dir_okay=False), help="Manifest JSON path."),
]


def add_common_options(function):
    for option in reversed(_common_options):
        function = option(function)
    return function


@cli.command("list-sources")
@add_common_options
@click.option("--json-output", is_flag=True, help="Print machine-readable JSON.")
def list_sources(env: str, download_dir: str, registry: Optional[str], manifest: Optional[str], json_output: bool) -> None:
    """List configured public portal sources."""
    client = _client(download_dir, registry, manifest, env)
    sources = [source.to_dict() for source in client.list_sources()]
    if json_output:
        _emit_json(sources)
        return
    for source in sources:
        click.echo(f"{source['name']} - {source['authority']} - {source['index_url']}")


@cli.command()
@click.argument("source")
@click.option("-q", "--query", help="Filter links by title or URL.")
@click.option("--max-results", default=50, show_default=True, type=int)
@click.option("--json-output", is_flag=True)
@add_common_options
def discover(
    source: str,
    query: Optional[str],
    max_results: int,
    json_output: bool,
    env: str,
    download_dir: str,
    registry: Optional[str],
    manifest: Optional[str],
) -> None:
    """Discover downloadable documents without saving them."""
    client = _client(download_dir, registry, manifest, env)
    records = client.discover(source, query=query, max_results=max_results)
    payload = [record.to_dict() for record in records]
    if json_output:
        _emit_json(payload)
        return
    if not records:
        click.echo("No matching documents found.")
        return
    for index, record in enumerate(records, start=1):
        hint = f" [{record.version_hint}]" if record.version_hint else ""
        click.echo(f"{index}. {record.title}{hint}\n   {record.document_url}")


@cli.command()
@click.argument("source")
@click.option("-q", "--query", help="Filter links by title or URL.")
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--track/--no-track", default=True, show_default=True, help="Update manifest after download.")
@click.option("--json-output", is_flag=True)
@add_common_options
def download(
    source: str,
    query: Optional[str],
    limit: int,
    track: bool,
    json_output: bool,
    env: str,
    download_dir: str,
    registry: Optional[str],
    manifest: Optional[str],
) -> None:
    """Discover, download, and optionally track matching documents."""
    client = _client(download_dir, registry, manifest, env)
    records = client.discover(source, query=query, max_results=limit)
    downloaded = [client.download(record) for record in records]
    changes = client.track_records(downloaded) if track else []
    payload = {"downloaded": [record.to_dict() for record in downloaded], "changes": [change.to_dict() for change in changes]}
    if json_output:
        _emit_json(payload)
        return
    click.echo(f"Downloaded {len(downloaded)} document(s).")
    for change in changes:
        click.echo(f"{change.status}: {change.title}")


@cli.command("create-request")
@click.argument("source")
@click.option("-q", "--query", help="Filter links by title or URL.")
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--json-output", is_flag=True, help="Print request JSON.")
@add_common_options
def create_request(
    source: str,
    query: Optional[str],
    limit: int,
    json_output: bool,
    env: str,
    download_dir: str,
    registry: Optional[str],
    manifest: Optional[str],
) -> None:
    """Create a saved download request and print its request id."""
    client = _client(download_dir, registry, manifest, env)
    request = client.create_download_request(source, query=query, limit=limit, env=env)
    payload = request.to_dict()
    if json_output:
        _emit_json(payload)
    else:
        click.echo(request.request_id)


@cli.command("run-request")
@click.argument("request_id")
@click.option("--track/--no-track", default=True, show_default=True)
@click.option("--json-output", is_flag=True)
@add_common_options
def run_request(
    request_id: str,
    track: bool,
    json_output: bool,
    env: str,
    download_dir: str,
    registry: Optional[str],
    manifest: Optional[str],
) -> None:
    """Run a previously created download request by id."""
    client = _client(download_dir, registry, manifest, env)
    payload = client.run_download_request(request_id, track=track)
    if json_output:
        _emit_json(payload)
        return
    click.echo(f"Downloaded {len(payload['downloaded'])} document(s).")


@cli.command()
@click.option("--json-output", is_flag=True)
@add_common_options
def manifest(json_output: bool, env: str, download_dir: str, registry: Optional[str], manifest: Optional[str]) -> None:
    """Print the current manifest."""
    client = _client(download_dir, registry, manifest, env)
    payload = client.load_manifest()
    if json_output:
        _emit_json(payload)
    else:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


@cli.command("export-csv")
@click.argument("output_path", type=click.Path(dir_okay=False))
@add_common_options
def export_csv(output_path: str, env: str, download_dir: str, registry: Optional[str], manifest: Optional[str]) -> None:
    """Export manifest documents to CSV."""
    client = _client(download_dir, registry, manifest, env)
    path = client.export_manifest_csv(output_path)
    click.echo(str(path))


@cli.group()
def validate() -> None:
    """Validate common Israeli fields."""


@validate.command("tz")
@click.argument("value")
@click.option("--json-output", is_flag=True)
def validate_tz(value: str, json_output: bool) -> None:
    """Validate an Israeli identity number."""
    valid = validate_teudat_zehut(value)
    payload = {"field": "tz", "value": value, "valid": valid}
    _emit_json(payload) if json_output else click.echo("valid" if valid else "invalid")


@validate.command("phone")
@click.argument("value")
@click.option("--json-output", is_flag=True)
def validate_phone(value: str, json_output: bool) -> None:
    """Validate and normalize an Israeli phone number."""
    payload = normalize_israeli_phone(value)
    _emit_json(payload) if json_output else click.echo("valid" if payload.get("valid") else "invalid")


@validate.command("mikud")
@click.argument("value")
@click.option("--json-output", is_flag=True)
def validate_postal_code(value: str, json_output: bool) -> None:
    """Validate a seven-digit postal code."""
    valid = validate_mikud(value)
    payload = {"field": "mikud", "value": value, "valid": valid}
    _emit_json(payload) if json_output else click.echo("valid" if valid else "invalid")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
