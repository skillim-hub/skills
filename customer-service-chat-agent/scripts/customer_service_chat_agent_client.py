#!/usr/bin/env python3
"""Compatibility entry point for the importable customer_service_chat_agent package."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from customer_service_chat_agent import *  # noqa: F401,F403
