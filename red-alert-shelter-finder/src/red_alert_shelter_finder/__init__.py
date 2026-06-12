"""Installable package for red-alert and public-shelter workflows."""

from .client import (
    Alert,
    AlertClientError,
    AlertParseError,
    RedAlertShelterFinderClient,
    Shelter,
    ShelterDataError,
    Watch,
    WatchError,
    alerts_to_json,
    haversine_m,
    normalize_area,
    now_iso,
    shelters_to_json,
    strip_hebrew_niqqud,
    validate_coordinates,
)

__all__ = [
    "Alert",
    "AlertClientError",
    "AlertParseError",
    "RedAlertShelterFinderClient",
    "Shelter",
    "ShelterDataError",
    "Watch",
    "WatchError",
    "alerts_to_json",
    "haversine_m",
    "normalize_area",
    "now_iso",
    "shelters_to_json",
    "strip_hebrew_niqqud",
    "validate_coordinates",
]
