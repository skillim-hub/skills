"""Executable wrapper for installed development environments.

Install first with:
    pip install -e .
Then run:
    python scripts/renovation-cost-estimator-cli.py scenario clinic
"""

from renovation_cost_estimator.cli import main

if __name__ == "__main__":
    main()
