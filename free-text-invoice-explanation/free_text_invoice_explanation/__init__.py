"""Plain-language invoice item explanations for Israeli documents."""

from .client import (
    Explanation,
    ExplanationOptions,
    InvoiceContext,
    InvoiceExplanationClient,
    InvoiceLine,
    ValidationIssue,
    explain_invoice,
    explain_line,
)

__all__ = [
    "Explanation",
    "ExplanationOptions",
    "InvoiceContext",
    "InvoiceExplanationClient",
    "InvoiceLine",
    "ValidationIssue",
    "explain_invoice",
    "explain_line",
]

__version__ = "2.1.0"
