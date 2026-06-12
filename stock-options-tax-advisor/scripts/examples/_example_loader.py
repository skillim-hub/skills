from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

from stock_options_tax_advisor import EquityScenario, StockOptionsTaxAdvisorClient


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("STOCK_OPTIONS_TAX_ADVISOR_ENV", "sandbox"))
    return p


def env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return default if raw in (None, "") else float(raw)


def print_case(case: Dict[str, Any]) -> None:
    print(json.dumps(case, ensure_ascii=False, indent=2))


def run_case(env: str, data: Dict[str, Any]) -> None:
    client = StockOptionsTaxAdvisorClient(environment=env)
    scenario = EquityScenario.from_dict(data)
    print_case({"environment": client.environment, "scenario": scenario.to_dict(), "result": client.calculate(scenario).to_dict()})
