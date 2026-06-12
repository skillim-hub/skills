#!/usr/bin/env python3
"""Command-line interface for inventory and catalog management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

import inventory_catalog_manager_client as client

app = typer.Typer(no_args_is_help=True, help="Manage an Israeli small-business inventory catalog.")


def load_or_new(path: Path) -> client.InventoryCatalog:
    if path.exists():
        return client.InventoryCatalog.load_json(path)
    return client.InventoryCatalog()


def emit(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def init(
    catalog_path: Path = typer.Argument(..., help="JSON catalog path to create."),
    currency: str = typer.Option("ILS", help="Catalog currency."),
    overwrite: bool = typer.Option(False, help="Overwrite existing file."),
) -> None:
    """Create an empty catalog."""
    if catalog_path.exists() and not overwrite:
        raise typer.BadParameter(f"File already exists: {catalog_path}")
    catalog = client.InventoryCatalog(currency=currency)
    catalog.save_json(catalog_path)
    emit({"status": "created", "path": str(catalog_path), "currency": catalog.currency})


def add_item_impl(
    catalog_path: Path,
    sku: str,
    name: str,
    unit: str,
    price_before_vat: str,
    vat_rate: str,
    stock: str,
    reorder_point: str,
    category: str,
    name_en: str,
    barcode: str,
    supplier_name: str,
    supplier_sku: str,
    tax_treatment: str,
    note: str,
    replace: bool,
) -> None:
    catalog = load_or_new(catalog_path)
    item = client.CatalogItem(
        sku=sku,
        name=name,
        unit=unit,
        price_before_vat=price_before_vat,
        vat_rate=vat_rate,
        stock_quantity=stock,
        reorder_point=reorder_point,
        category=category,
        name_en=name_en,
        barcode=barcode,
        supplier_name=supplier_name,
        supplier_sku=supplier_sku,
        tax_treatment=tax_treatment,
        notes=note,
    )
    catalog.add_item(item, replace=replace)
    catalog.save_json(catalog_path)
    payload = item.to_dict()
    payload["id"] = item.sku
    payload["status"] = "created" if not replace else "upserted"
    emit(payload)


@app.command("create-item")
def create_item(
    catalog_path: Path,
    sku: str = typer.Option(..., help="Internal SKU, uppercase letters, digits, hyphens."),
    name: str = typer.Option(..., help="Item name."),
    unit: str = typer.Option("unit", help="Sale unit, such as unit, kg, hour, session."),
    price_before_vat: str = typer.Option(..., help="Price before VAT, e.g. 42.37."),
    vat_rate: str = typer.Option("0.18", help="VAT decimal rate, e.g. 0.18."),
    stock: str = typer.Option("0", help="Opening stock quantity."),
    reorder_point: str = typer.Option("0", help="Low-stock threshold."),
    category: str = typer.Option("", help="Category."),
    name_en: str = typer.Option("", help="English item name."),
    barcode: str = typer.Option("", help="Barcode/GTIN stored as text."),
    supplier_name: str = typer.Option("", help="Supplier name."),
    supplier_sku: str = typer.Option("", help="Supplier SKU."),
    tax_treatment: str = typer.Option("standard_domestic_vat", help="Tax treatment note."),
    note: str = typer.Option("", help="Internal note."),
    replace: bool = typer.Option(False, help="Replace existing SKU."),
) -> None:
    """Create or upsert an item and return a JSON object containing id."""
    add_item_impl(
        catalog_path,
        sku,
        name,
        unit,
        price_before_vat,
        vat_rate,
        stock,
        reorder_point,
        category,
        name_en,
        barcode,
        supplier_name,
        supplier_sku,
        tax_treatment,
        note,
        replace,
    )


@app.command()
def add(
    catalog_path: Path,
    sku: str,
    name: str,
    unit: str = typer.Option("unit", help="Sale unit, such as unit, kg, hour, session."),
    price_before_vat: str = typer.Option(..., help="Price before VAT, e.g. 42.37."),
    vat_rate: str = typer.Option("0.18", help="VAT decimal rate, e.g. 0.18."),
    stock: str = typer.Option("0", help="Opening stock quantity."),
    reorder_point: str = typer.Option("0", help="Low-stock threshold."),
    category: str = typer.Option("", help="Category."),
    name_en: str = typer.Option("", help="English item name."),
    barcode: str = typer.Option("", help="Barcode/GTIN stored as text."),
    supplier_name: str = typer.Option("", help="Supplier name."),
    supplier_sku: str = typer.Option("", help="Supplier SKU."),
    tax_treatment: str = typer.Option("standard_domestic_vat", help="Tax treatment note."),
    note: str = typer.Option("", help="Internal note."),
    replace: bool = typer.Option(False, help="Replace existing SKU."),
) -> None:
    """Add or replace an item and return a JSON object containing id."""
    add_item_impl(
        catalog_path,
        sku,
        name,
        unit,
        price_before_vat,
        vat_rate,
        stock,
        reorder_point,
        category,
        name_en,
        barcode,
        supplier_name,
        supplier_sku,
        tax_treatment,
        note,
        replace,
    )


@app.command("list")
def list_items(
    catalog_path: Path,
    active_only: bool = typer.Option(False, help="Show only active items."),
    category: Optional[str] = typer.Option(None, help="Filter by category."),
) -> None:
    """List catalog items."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    rows = [item.to_dict() for item in catalog.list_items(active_only=active_only, category=category)]
    emit(rows)


@app.command()
def show(catalog_path: Path, item_id: str = typer.Argument(..., help="Item id. The id is the normalized SKU.")) -> None:
    """Show one item."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    emit(catalog.get_item(item_id).to_dict())


@app.command()
def price(catalog_path: Path, item_id: str = typer.Argument(..., help="Item id. The id is the normalized SKU.")) -> None:
    """Show before-VAT and VAT-inclusive price for one item."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    item = catalog.get_item(item_id)
    emit({
        "id": item.sku,
        "sku": item.sku,
        "price_before_vat": item.price_before_vat,
        "vat_rate": item.vat_rate,
        "price_with_vat": item.price_with_vat,
        "currency": catalog.currency,
    })


@app.command("stock-adjust")
def stock_adjust(
    catalog_path: Path,
    item_id: str = typer.Argument(..., help="Item id. The id is the normalized SKU."),
    quantity_delta: str = typer.Argument(..., help="Signed quantity delta."),
    reason: str = typer.Option(..., help="Movement reason, such as purchase, sale, damage, count_adjustment."),
    reference: str = typer.Option("", help="Reference such as invoice, PO, or count ID."),
    note: str = typer.Option("", help="Audit note."),
) -> None:
    """Create a stock movement and update quantity."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    movement = catalog.adjust_stock(item_id, quantity_delta, reason=reason, reference=reference, note=note)
    catalog.save_json(catalog_path)
    payload = movement.to_dict()
    payload["id"] = movement.sku
    emit(payload)


@app.command("set-count")
def set_count(
    catalog_path: Path,
    item_id: str = typer.Argument(..., help="Item id. The id is the normalized SKU."),
    counted_quantity: str = typer.Argument(..., help="Physical count quantity."),
    reference: str = typer.Option(..., help="Count reference."),
    note: str = typer.Option("", help="Audit note."),
) -> None:
    """Set stock from a physical count by creating a count adjustment."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    movement = catalog.set_stock_from_count(item_id, counted_quantity, reference=reference, note=note)
    catalog.save_json(catalog_path)
    emit({"status": "unchanged", "id": client.normalize_sku(item_id)} if movement is None else movement.to_dict())


@app.command("low-stock")
def low_stock(
    catalog_path: Path,
    include_inactive: bool = typer.Option(False, help="Include inactive items."),
) -> None:
    """Show items at or below reorder point."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    rows = [item.to_dict() for item in catalog.low_stock(include_inactive=include_inactive)]
    emit(rows)


@app.command("import-csv")
def import_csv(
    catalog_path: Path,
    csv_path: Path,
    replace: bool = typer.Option(False, help="Replace existing items when merging."),
) -> None:
    """Import items from CSV and save JSON catalog."""
    imported = client.InventoryCatalog.import_csv(csv_path)
    catalog = load_or_new(catalog_path)
    catalog.merge(imported, replace=replace)
    catalog.save_json(catalog_path)
    emit({"status": "imported", "count": len(imported.items), "path": str(catalog_path)})


@app.command("export-csv")
def export_csv(
    catalog_path: Path,
    csv_path: Path,
    include_inactive: bool = typer.Option(False, help="Include inactive items."),
    utf8_bom: bool = typer.Option(False, help="Write UTF-8 with BOM for older Excel."),
) -> None:
    """Export items to CSV."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    catalog.export_csv(csv_path, include_inactive=include_inactive, utf8_bom=utf8_bom)
    emit({"status": "exported", "path": str(csv_path)})


@app.command()
def validate(catalog_path: Path) -> None:
    """Validate catalog data."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    errors = catalog.validate()
    if errors:
        emit({"status": "failed", "errors": errors})
        raise typer.Exit(1)
    emit({"status": "ok"})


@app.command("consumer-export")
def consumer_export(catalog_path: Path) -> None:
    """Print sanitized consumer price-list rows."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    emit(client.consumer_export_rows(catalog))


@app.command("b2b-export")
def b2b_export(catalog_path: Path) -> None:
    """Print B2B price-list rows with VAT data."""
    catalog = client.InventoryCatalog.load_json(catalog_path)
    emit(client.b2b_export_rows(catalog))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
