#!/usr/bin/env python3
"""Compatibility entrypoint for the installable customer_feedback_collector package."""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from customer_feedback_collector import *
