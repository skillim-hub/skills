#!/usr/bin/env python3
"""Compatibility launcher for the Expense Manager CLI."""
from __future__ import annotations

try:
    from .expense_manager_cli import main
except ImportError:
    from expense_manager_cli import main  # type: ignore[no-redef]

if __name__ == "__main__":
    main()
