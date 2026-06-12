"""Emergency contact and first-aid local toolkit."""

from .client import (
    AsyncEmergencyInfoClient,
    DEFAULT_EMERGENCY_SERVICES,
    EmergencyContact,
    EmergencyInfoClient,
    EmergencyProfile,
    MedicalNotes,
    SiteInfo,
    TriageResult,
    ValidationResult,
    contains_id_like_value,
    days_since_review,
    is_supported_phone,
    make_starter_profile,
    normalize_israeli_phone,
    parse_local_date,
    profile_from_mapping,
    triage_first_aid,
    validate_profile,
)

__all__ = [
    "AsyncEmergencyInfoClient",
    "DEFAULT_EMERGENCY_SERVICES",
    "EmergencyContact",
    "EmergencyInfoClient",
    "EmergencyProfile",
    "MedicalNotes",
    "SiteInfo",
    "TriageResult",
    "ValidationResult",
    "contains_id_like_value",
    "days_since_review",
    "is_supported_phone",
    "make_starter_profile",
    "normalize_israeli_phone",
    "parse_local_date",
    "profile_from_mapping",
    "triage_first_aid",
    "validate_profile",
]

__version__ = "2.2.0"
