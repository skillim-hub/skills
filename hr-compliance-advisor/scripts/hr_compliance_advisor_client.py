"""Compatibility import shim for the installable HR Compliance Advisor package.

Import from ``hr_compliance_advisor`` in new code. This module remains for users
who reference the script path directly.
"""
from __future__ import annotations

from hr_compliance_advisor.client import *  # noqa: F401,F403
