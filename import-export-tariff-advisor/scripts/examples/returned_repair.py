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
result = client().estimate(
    description="Returned repaired camera",
    goods_value=150,
    shipping=40,
    exchange_rate_to_ils=fx(4.00),
    duty_rate=0,
    purchase_tax_rate=0,
    vat_rate=vat_rate(),
    use_type="repair return",
    environment=args.env,
)
print_result(result)
