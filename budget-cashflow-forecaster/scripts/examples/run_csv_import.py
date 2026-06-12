from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from budget_cashflow_forecaster import CashFlowForecaster


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BCF_ENV", "sandbox"))
    args = parser.parse_args()
    result = CashFlowForecaster().forecast_from_csv(
        Path(__file__).with_name("sample_transactions.csv"),
        opening_balance=float(os.getenv("BCF_OPENING_BALANCE", "10000")),
        start_month=os.getenv("BCF_START_MONTH", "2026-01"),
        months=int(os.getenv("BCF_MONTHS", "3")),
        environment=args.env,
        tax_profile={
            "vat_rate": float(os.getenv("BCF_VAT_RATE", "0.18")),
            "vat_cadence": os.getenv("BCF_VAT_CADENCE", "monthly"),
            "income_tax_advance_rate": float(os.getenv("BCF_INCOME_TAX_ADVANCE_RATE", "0.08")),
            "bituach_leumi_rate": float(os.getenv("BCF_BITUACH_LEUMI_RATE", "0.18")),
            "reviewed_on": os.getenv("BCF_REVIEWED_ON", "2026-06-02"),
        },
        buffer=float(os.getenv("BCF_BUFFER", "5000")),
    )
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
