from __future__ import annotations

import argparse
import json
import os

from import_export_tariff_advisor import LineItem, TariffAdvisorClient


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TARIFF_ADVISOR_ENV", "sandbox"))
    return p


def vat_rate() -> float:
    return float(os.getenv("TARIFF_ADVISOR_VAT_RATE", "0.18"))


def fx(default: float) -> float:
    return float(os.getenv("TARIFF_ADVISOR_EXCHANGE_RATE_TO_ILS", str(default)))


def print_result(result) -> None:
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def client() -> TariffAdvisorClient:
    store = os.getenv("TARIFF_ADVISOR_STORE")
    return TariffAdvisorClient(default_vat_rate=vat_rate(), store_path=store)

args = parser().parse_args()
items = [
    LineItem.create(
        description="Cotton T-shirts for resale",
        goods_value=500,
        shipping=40,
        exchange_rate_to_ils=fx(3.70),
        duty_rate=0.06,
        purchase_tax_rate=0,
        vat_rate=vat_rate(),
        quantity=50,
        use_type="resale",
        environment=args.env,
    ),
    LineItem.create(
        description="Bluetooth power banks for resale",
        goods_value=800,
        shipping=60,
        exchange_rate_to_ils=fx(3.70),
        duty_rate=0,
        purchase_tax_rate=0,
        vat_rate=vat_rate(),
        quantity=20,
        use_type="resale",
        environment=args.env,
    ),
]
print_result(client().estimate_lines(items))
