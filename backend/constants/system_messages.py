"""Single source of truth for user-facing response text. Add a constant here
before using it anywhere — services, routes, and exception handlers all import
from this module so wording stays uniform (see CONTRIBUTING.md)."""

OPERATION_SUCCESSFUL = "Operation successful"
HEALTHY = "LedgerLens API is healthy"
UNHEALTHY = "LedgerLens API is unhealthy"

NOT_FOUND = "The requested resource was not found"
VALIDATION_ERROR = "The request could not be validated"
UNAUTHORIZED = "Missing or invalid authentication credentials"
INTERNAL_ERROR = "An unexpected error occurred"

CURRENCY_MISMATCH = "Cannot combine amounts in different currencies"
CATEGORY_CYCLE = "This change would make a category its own ancestor"
