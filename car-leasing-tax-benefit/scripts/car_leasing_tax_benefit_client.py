#!/usr/bin/env python3
"""Script wrapper for the installable car_leasing_tax_benefit package."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from car_leasing_tax_benefit import (
    CalculationTrace,
    CalculatorError,
    CarLeasingTaxBenefitClient,
    InputValidationError,
    RequestStore,
    RuleTableError,
    TaxResult,
    UnsupportedCategoryError,
    VehicleInput,
    decimal_value,
    money,
)
from car_leasing_tax_benefit.cli import main

__all__ = [
    "CalculationTrace",
    "CalculatorError",
    "CarLeasingTaxBenefitClient",
    "InputValidationError",
    "RequestStore",
    "RuleTableError",
    "TaxResult",
    "UnsupportedCategoryError",
    "VehicleInput",
    "decimal_value",
    "money",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
