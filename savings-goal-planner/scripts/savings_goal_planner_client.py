#!/usr/bin/env python3
"""Installable helper entry for the Savings Goal Planner client.

Import public objects from savings_goal_planner.client. Execute the file to print
available vehicle keys as JSON.
"""

from __future__ import annotations

import json

from savings_goal_planner.client import *  # noqa: F403


if __name__ == "__main__":
    from savings_goal_planner.client import VEHICLES

    print(json.dumps({"vehicles": sorted(VEHICLES)}, ensure_ascii=False, indent=2))
