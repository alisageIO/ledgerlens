"""Domain-exception vocabulary. This is the only thing the API layer's
exception mapping (api/exceptions.py) needs to know about — domain services
raise these and never construct an HTTP response themselves."""


class DomainError(Exception):
    """Base class for every domain-layer exception."""


class NotFoundError(DomainError):
    """Raised when a resource doesn't exist or isn't owned by the caller.

    Mapped to 404, never 403 — the response must not confirm a resource
    exists at all when it belongs to another user (TRD §10).
    """


class CurrencyMismatchError(DomainError):
    """Raised when a Money operation combines mismatched currencies."""

    def __init__(self, left_currency: str, right_currency: str) -> None:
        super().__init__(f"Currency mismatch: {left_currency} vs {right_currency}")
        self.left_currency = left_currency
        self.right_currency = right_currency


class CategoryCycleError(DomainError):
    """Raised when a category edit would make it its own ancestor (TRD §3)."""


class ValidationError(DomainError):
    """Raised for domain-level validation failures not caught by Pydantic."""


class EmptyPasswordError(DomainError):
    """Raised when an empty-string password reaches the hashing boundary (NFR-1.1)."""


class DuplicateEmailError(DomainError):
    """Raised when registration is attempted with an email that's already taken."""
