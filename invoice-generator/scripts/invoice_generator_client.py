#!/usr/bin/env python3
"""Compatibility entry point for the typed client helper."""

from invoice_generator.client import *  # noqa: F401,F403
from invoice_generator.client import main

if __name__ == "__main__":
    raise SystemExit(main())
