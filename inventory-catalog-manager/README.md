# Inventory & Catalog Manager

Manage a structured catalog of SKUs, prices, VAT rates, and stock levels for Israeli small businesses, freelancers, service providers, shops, and practical household inventory.

The package contains bilingual skill guides, Israeli workflow references, a typed Python helper, a Typer CLI, runnable examples, pytest tests, and a two-pass web verification log.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a catalog, create an item, extract the item id from the JSON response, then reuse that id in the next command.

```bash
inventory-catalog-manager init catalog.json

CREATE_RESPONSE=$(inventory-catalog-manager create-item catalog.json \
  --sku COF-BNS-001 \
  --name "פולי קפה 1 ק״ג" \
  --category coffee \
  --unit kg \
  --price-before-vat 42.37 \
  --vat-rate 0.18 \
  --stock 18 \
  --reorder-point 5)

ITEM_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

inventory-catalog-manager price catalog.json "$ITEM_ID"
inventory-catalog-manager stock-adjust catalog.json "$ITEM_ID" -3 --reason sale --reference INV-1001
inventory-catalog-manager low-stock catalog.json
```

The local wrapper also works without installing console scripts:

```bash
python scripts/inventory-catalog-manager-cli.py list catalog.json
```

## Python usage

After `pip install -e .`, import the helper without path manipulation:

```python
import inventory_catalog_manager_client as catalog_client

catalog = catalog_client.InventoryCatalog()
catalog.add_item(
    catalog_client.CatalogItem(
        sku="MUG-WHT-001",
        name="ספל לבן",
        unit="unit",
        price_before_vat="21.19",
        vat_rate="0.18",
        stock_quantity="34",
        reorder_point="8",
    )
)
catalog.save_json("catalog.json")
```

## Run tests

```bash
pytest
python -m compileall scripts/ -q
```

## Run examples

Each example accepts `--env sandbox` or `--env production` and reads optional `ICM_` environment variables.

```bash
python scripts/examples/retail_quickstart.py --env sandbox
python scripts/examples/freelancer_services_catalog.py --env sandbox
python scripts/examples/csv_import_export.py --env sandbox
python scripts/examples/stock_count_reconciliation.py --env sandbox
python scripts/examples/vat_price_check.py --env sandbox
python scripts/examples/reorder_report.py --env sandbox
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and ₪/DD/MM/YYYY localization. |
| `metadata.json` | Skill metadata without creator fields. |
| `references/api-reference.md` | Israeli API and regulation reference with request/response examples and error tables. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Diagnosis and recovery guide. |
| `references/test-scenarios.md` | Concrete validation scenarios. |
| `references/migration-checklist.md` | Spreadsheet, POS, and accounting migration checklist. |
| `references/branding-audit.md` | Branding, creator, and visual asset audit log. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log. |
| `references/verification-log.md` | Two-pass web validation log for official Israeli sources and corrections. |
| `scripts/inventory_catalog_manager_client.py` | Typed sync and async Python helper. |
| `scripts/inventory_catalog_manager_cli.py` | Importable Typer CLI implementation. |
| `scripts/inventory-catalog-manager-cli.py` | Thin executable CLI wrapper. |
| `scripts/test_inventory_catalog_manager_client.py` | pytest suite with 20+ tests. |
| `scripts/examples/` | Runnable examples. |
| `pyproject.toml` | Python project metadata, console script, importable modules, and test configuration. |
| `requirements-dev.txt` | Development dependencies. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |

## Data format

```json
{
  "currency": "ILS",
  "items": [
    {
      "sku": "COF-BNS-001",
      "name": "פולי קפה 1 ק״ג",
      "unit": "kg",
      "price_before_vat": "42.37",
      "vat_rate": "0.18",
      "stock_quantity": "18",
      "reorder_point": "5",
      "active": true
    }
  ],
  "movements": []
}
```

## Production notes

- Confirm current VAT settings and invoice-allocation obligations against official Israeli sources before live invoicing.
- Keep supplier costs out of public exports.
- Store identifiers as text.
- Back up before bulk imports.
- Use stock movements instead of silent direct quantity edits.
