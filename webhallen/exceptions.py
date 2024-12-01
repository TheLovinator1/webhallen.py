from __future__ import annotations


class WebhallenError(Exception):
    """Base exception for Webhallen API errors."""


class ProductNotFoundError(WebhallenError):
    """Raised when a product cannot be found."""
