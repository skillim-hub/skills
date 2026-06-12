"""Compatibility entry point for the installable client module."""
from loan_amortization_planner.client import *
from loan_amortization_planner.client import main

if __name__ == "__main__":
    raise SystemExit(main())
