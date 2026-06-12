"""Click command line interface for data.gov.il CKAN data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

import click

from .client import DatagovClient, RequestConfig, base_url_for_env, extract_first_dataset_id, extract_first_resource_id, parse_filter_pairs


def _echo_json(data: Any) -> None:
    click.echo(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _make_client(ctx: click.Context) -> DatagovClient:
    config = RequestConfig(base_url=ctx.obj["base_url"], timeout=ctx.obj["timeout"], max_retries=ctx.obj["retries"])
    return DatagovClient(config=config)


@click.group()
@click.option("--env", "env_name", default="production", type=click.Choice(["sandbox", "production"]), show_default=True, help="Runtime environment.")
@click.option("--base-url", default=None, help="Override the CKAN API base URL.")
@click.option("--timeout", default=30.0, show_default=True, type=float, help="HTTP timeout in seconds.")
@click.option("--retries", default=2, show_default=True, type=int, help="Retries for temporary GET failures.")
@click.pass_context
def cli(ctx: click.Context, env_name: str, base_url: Optional[str], timeout: float, retries: int) -> None:
    """Discover, query, and export public data.gov.il CKAN datasets."""
    ctx.ensure_object(dict)
    ctx.obj.update({"base_url": (base_url or base_url_for_env(env_name)).rstrip("/"), "timeout": timeout, "retries": retries, "env": env_name})


@cli.command()
@click.argument("query")
@click.option("--rows", default=10, show_default=True, type=int, help="Number of datasets to return.")
@click.option("--start", default=0, show_default=True, type=int, help="Dataset search offset.")
@click.option("--fq", default=None, help="CKAN filter query, for example organization:lamas.")
@click.option("--sort", default=None, help="CKAN sort expression, for example metadata_modified desc.")
@click.option("--json-output", "as_json", is_flag=True, help="Print raw JSON.")
@click.pass_context
def search(ctx: click.Context, query: str, rows: int, start: int, fq: Optional[str], sort: Optional[str], as_json: bool) -> None:
    """Search datasets."""
    result = _make_client(ctx).package_search(query, rows=rows, start=start, fq=fq, sort=sort)
    if as_json:
        _echo_json(result)
        return
    click.echo(f"Found {result.get('count', 0)} datasets")
    for item in result.get("results", []):
        title = item.get("title") or item.get("name")
        name = item.get("name")
        org = (item.get("organization") or {}).get("title") or (item.get("organization") or {}).get("name") or ""
        click.echo(f"- {title} [{name}] {org}")


@cli.command("first-dataset-id")
@click.argument("query")
@click.option("--rows", default=5, show_default=True, type=int, help="Number of candidates to scan.")
@click.pass_context
def first_dataset_id(ctx: click.Context, query: str, rows: int) -> None:
    """Print the first dataset identifier from a search response."""
    result = _make_client(ctx).package_search(query, rows=rows)
    dataset_id = extract_first_dataset_id(result)
    if not dataset_id:
        raise click.ClickException("No dataset id found")
    click.echo(dataset_id)


@cli.command()
@click.argument("dataset_id")
@click.option("--json-output", "as_json", is_flag=True, help="Print raw JSON.")
@click.pass_context
def dataset(ctx: click.Context, dataset_id: str, as_json: bool) -> None:
    """Show dataset metadata and resources."""
    result = _make_client(ctx).package_show(dataset_id)
    if as_json:
        _echo_json(result)
        return
    click.echo(f"{result.get('title') or result.get('name')} [{result.get('name')}]")
    org = result.get("organization") or {}
    click.echo(f"Publisher: {org.get('title') or org.get('name') or 'unknown'}")
    click.echo(f"Modified: {result.get('metadata_modified', 'unknown')}")
    click.echo("Resources:")
    for resource in result.get("resources", []):
        active = "datastore" if resource.get("datastore_active") else "file"
        click.echo(f"- {resource.get('name') or resource.get('id')} [{resource.get('id')}] {resource.get('format')} {active}")


@cli.command("first-resource-id")
@click.argument("dataset_id")
@click.option("--any-resource", is_flag=True, help="Allow non-datastore resources.")
@click.pass_context
def first_resource_id(ctx: click.Context, dataset_id: str, any_resource: bool) -> None:
    """Print the first useful resource identifier from dataset metadata."""
    result = _make_client(ctx).package_show(dataset_id)
    resource_id = extract_first_resource_id(result, prefer_datastore=not any_resource)
    if not resource_id:
        raise click.ClickException("No resource id found")
    click.echo(resource_id)


@cli.command()
@click.argument("resource_id")
@click.option("--json-output", "as_json", is_flag=True, help="Print raw JSON.")
@click.pass_context
def resource(ctx: click.Context, resource_id: str, as_json: bool) -> None:
    """Show resource metadata."""
    result = _make_client(ctx).resource_show(resource_id)
    if as_json:
        _echo_json(result)
        return
    click.echo(f"{result.get('name') or result.get('id')} [{result.get('id')}]")
    click.echo(f"Format: {result.get('format')}")
    click.echo(f"Datastore active: {result.get('datastore_active')}")


@cli.command("query")
@click.argument("resource_id")
@click.option("--limit", default=100, show_default=True, type=int, help="Record limit.")
@click.option("--offset", default=0, show_default=True, type=int, help="Record offset.")
@click.option("--fields", default=None, help="Comma-separated fields.")
@click.option("--filter", "filters", multiple=True, help="Equality filter in key=value form. Can be repeated.")
@click.option("--q", default=None, help="Full-text search inside resource.")
@click.option("--sort", default=None, help="Sort expression, for example _id asc.")
@click.option("--json-output", "as_json", is_flag=True, help="Print raw JSON.")
@click.pass_context
def query_resource(ctx: click.Context, resource_id: str, limit: int, offset: int, fields: Optional[str], filters: List[str], q: Optional[str], sort: Optional[str], as_json: bool) -> None:
    """Query datastore records."""
    try:
        parsed_filters = parse_filter_pairs(filters)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    result = _make_client(ctx).datastore_search(resource_id, limit=limit, offset=offset, fields=fields, filters=parsed_filters or None, q=q, sort=sort)
    if as_json:
        _echo_json(result)
        return
    click.echo(f"Total: {result.get('total', 'unknown')}; returned: {len(result.get('records', []))}")
    for record in result.get("records", [])[:limit]:
        click.echo(json.dumps(record, ensure_ascii=False))


@cli.command()
@click.argument("resource_id")
@click.option("--out", "output_path", required=True, type=click.Path(dir_okay=False, path_type=Path), help="Output CSV path.")
@click.option("--page-size", default=1000, show_default=True, type=int, help="Page size.")
@click.option("--max-records", default=None, type=int, help="Maximum records to export.")
@click.option("--fields", default=None, help="Comma-separated fields.")
@click.option("--filter", "filters", multiple=True, help="Equality filter in key=value form. Can be repeated.")
@click.option("--q", default=None, help="Full-text search inside resource.")
@click.pass_context
def export(ctx: click.Context, resource_id: str, output_path: Path, page_size: int, max_records: Optional[int], fields: Optional[str], filters: List[str], q: Optional[str]) -> None:
    """Export datastore records to UTF-8 CSV."""
    try:
        parsed_filters = parse_filter_pairs(filters)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    client = _make_client(ctx)
    records = list(client.datastore_search_all(resource_id, page_size=page_size, max_records=max_records, fields=fields, filters=parsed_filters or None, q=q))
    count = DatagovClient.write_csv(records, output_path)
    click.echo(f"Wrote {count} rows to {output_path}")


@cli.command()
@click.option("--json-output", "as_json", is_flag=True, help="Print raw JSON.")
@click.pass_context
def orgs(ctx: click.Context, as_json: bool) -> None:
    """List publishing organizations."""
    result = _make_client(ctx).organization_list(all_fields=True)
    if as_json:
        _echo_json(result)
        return
    value = result.get("value", []) if isinstance(result, dict) else []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                click.echo(f"- {item.get('title') or item.get('name')} [{item.get('name')}]")
            else:
                click.echo(f"- {item}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
