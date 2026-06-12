#!/usr/bin/env python3
"""Compatibility wrapper for the installable leave_sick_day_tracker package.

Import from `leave_sick_day_tracker` in new code. This wrapper exists for users who
run files from the scripts directory during migration.
"""
from leave_sick_day_tracker import *  # noqa: F401,F403
