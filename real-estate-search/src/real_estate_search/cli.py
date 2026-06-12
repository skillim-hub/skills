from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import Listing, RealEstateSearchClient, SearchCriteria

app = typer.Typer(help="Create and review Israeli real-estate search plans for Yad2, Madlan, and Komo.")


def _criteria_from_options(
    city: str,
    deal_type: str,
    neighborhoods: str,
    min_price: Optional[int],
    max_price: Optional[int],
    min_rooms: Optional[float],
    max_rooms: Optional[float],
    property_types: str,
    sources: str,
    parking: Optional[bool],
    balcony: Optional[bool],
    accessible: Optional[bool],
    pets_allowed: Optional[bool],
    entry_date: Optional[str],
) -> SearchCriteria:
    return SearchCriteria.from_mapping(
        {
            "city": city,
            "deal_type": deal_type,
            "neighborhoods": neighborhoods,
            "min_price": min_price,
            "max_price": max_price,
            "min_rooms": min_rooms,
            "max_rooms": max_rooms,
            "property_types": property_types,
            "sources": sources,
            "parking": parking,
            "balcony": balcony,
            "accessible": accessible,
            "pets_allowed": pets_allowed,
            "entry_date": entry_date,
        }
    )


@app.command("create")
def create_plan(
    city: str = typer.Option(..., help="City name, for example: תל אביב-יפו"),
    deal_type: str = typer.Option("rent", help="rent, sale, commercial_rent, or commercial_sale"),
    neighborhoods: str = typer.Option("", help="Comma-separated neighborhood names"),
    min_price: Optional[int] = typer.Option(None),
    max_price: Optional[int] = typer.Option(None),
    min_rooms: Optional[float] = typer.Option(None),
    max_rooms: Optional[float] = typer.Option(None),
    property_types: str = typer.Option("", help="Comma-separated property types"),
    sources: str = typer.Option("yad2,madlan,komo", help="Comma-separated sources"),
    parking: Optional[bool] = typer.Option(None),
    balcony: Optional[bool] = typer.Option(None),
    accessible: Optional[bool] = typer.Option(None),
    pets_allowed: Optional[bool] = typer.Option(None),
    entry_date: Optional[str] = typer.Option(None, help="YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional JSON output path"),
) -> None:
    client = RealEstateSearchClient(environment=env)
    criteria = _criteria_from_options(
        city,
        deal_type,
        neighborhoods,
        min_price,
        max_price,
        min_rooms,
        max_rooms,
        property_types,
        sources,
        parking,
        balcony,
        accessible,
        pets_allowed,
        entry_date,
    )
    plan = client.build_search_plan(criteria)
    payload = plan.to_dict()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if output:
        output.write_text(rendered + "\n", encoding="utf-8")
    typer.echo(rendered)


@app.command("show")
def show_plan(
    file: Path = typer.Option(..., "--file", "-f", help="Plan JSON file"),
    plan_id: str = typer.Option(..., "--plan-id", help="Plan id extracted from the create response"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    client = RealEstateSearchClient(environment=env)
    plan = client.load_plan_json(file)
    if plan.plan_id != plan_id:
        raise typer.BadParameter("plan_id does not match the file")
    typer.echo(client.summarize_plan(plan))
    for link in plan.links:
        typer.echo(f"{link.source}: {link.url}")


@app.command("links")
def links(
    city: str = typer.Option(...),
    deal_type: str = typer.Option("rent"),
    neighborhoods: str = typer.Option(""),
    max_price: Optional[int] = typer.Option(None),
    min_rooms: Optional[float] = typer.Option(None),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    client = RealEstateSearchClient(environment=env)
    criteria = SearchCriteria.from_mapping(
        {
            "city": city,
            "deal_type": deal_type,
            "neighborhoods": neighborhoods,
            "max_price": max_price,
            "min_rooms": min_rooms,
        }
    )
    output = {"links": [link.to_dict() for link in client.build_source_urls(criteria)]}
    typer.echo(json.dumps(output, ensure_ascii=False, indent=2))


@app.command("compare")
def compare(
    listings_file: Path = typer.Option(..., "--listings", help="JSON array of listing objects"),
    city: str = typer.Option(...),
    deal_type: str = typer.Option("rent"),
    neighborhoods: str = typer.Option(""),
    max_price: Optional[int] = typer.Option(None),
    min_rooms: Optional[float] = typer.Option(None),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    client = RealEstateSearchClient(environment=env)
    payload = json.loads(listings_file.read_text(encoding="utf-8"))
    listings = [Listing.from_mapping(item) for item in payload]
    criteria = SearchCriteria.from_mapping(
        {
            "city": city,
            "deal_type": deal_type,
            "neighborhoods": neighborhoods,
            "max_price": max_price,
            "min_rooms": min_rooms,
        }
    )
    typer.echo(json.dumps(client.rank_listings(listings, criteria), ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
