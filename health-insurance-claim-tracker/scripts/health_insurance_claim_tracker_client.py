"""Importable compatibility module for the claim tracker client.

Prefer importing from the installable package:

    from health_insurance_claim_tracker import HealthInsuranceClaimTrackerClient
"""

from health_insurance_claim_tracker.client import (
    AsyncHealthInsuranceClaimTrackerClient,
    Claim,
    ClaimNotFoundError,
    ClaimStatus,
    ClaimTrackerError,
    Document,
    HealthInsuranceClaimTrackerClient,
    PolicyType,
    Reimbursement,
    TimelineEvent,
    ValidationError,
    format_ils,
    format_israeli_date,
    money,
    parse_israeli_date,
    required_documents,
)

__all__ = [
    "AsyncHealthInsuranceClaimTrackerClient",
    "Claim",
    "ClaimNotFoundError",
    "ClaimStatus",
    "ClaimTrackerError",
    "Document",
    "HealthInsuranceClaimTrackerClient",
    "PolicyType",
    "Reimbursement",
    "TimelineEvent",
    "ValidationError",
    "format_ils",
    "format_israeli_date",
    "money",
    "parse_israeli_date",
    "required_documents",
]
