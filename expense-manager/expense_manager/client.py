"""Client re-export module."""
from __future__ import annotations

from scripts import expense_manager_client as _client
from scripts.expense_manager_client import *

__all__ = list(_client.__all__)
