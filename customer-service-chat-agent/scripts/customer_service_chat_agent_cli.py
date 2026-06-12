#!/usr/bin/env python3
"""Script entry point for the customer-service chat agent CLI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from customer_service_chat_agent.cli import app

if __name__ == "__main__":
    app()
