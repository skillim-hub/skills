"""Compatibility shim for local script imports.

Import the installable package instead of keeping a second implementation.
"""

from privacy_compliance_checker.client import *  # noqa: F401,F403
