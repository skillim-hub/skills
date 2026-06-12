#!/usr/bin/env python3
"""Underscored client entry point."""
from disaster_preparedness_guide.client import *  # noqa: F401,F403
from disaster_preparedness_guide.client import main
if __name__ == '__main__':
    raise SystemExit(main())
