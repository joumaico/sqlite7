"""Package-specific exceptions for sqlite7.

This module mirrors the familiar DB-API exception hierarchy for the native SQLite backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class SQLiteErrorDetails:
    """Extra metadata captured from a native SQLite failure.

    Attributes:
        errorcode: SQLite numeric error code, when available.
        errorname: SQLite symbolic error name, when available.
    """

    errorcode: Optional[int] = None
    errorname: Optional[str] = None


class SQLite7Error(Exception):
    """Base exception for all package-defined errors.

    Args:
        message: Human-readable error message.
        original: Original backend exception, when present.
        details: Structured SQLite metadata, when present.
    """

    def __init__(
        self,
        message: str,
        *,
        original: BaseException | None = None,
        details: SQLiteErrorDetails | None = None,
    ) -> None:
        super().__init__(message)
        self.original = original
        self.details = details or SQLiteErrorDetails()
        self.sqlite_errorcode = self.details.errorcode
        self.sqlite_errorname = self.details.errorname


class Warning(SQLite7Error):
    """Raised for important non-fatal conditions."""


class Error(SQLite7Error):
    """Base class for database-related errors."""


class InterfaceError(Error):
    """Raised for interface misuse or invalid inputs."""


class DatabaseError(Error):
    """Raised for general database failures."""


class DataError(DatabaseError):
    """Raised for data processing failures."""


class OperationalError(DatabaseError):
    """Raised for operational failures such as locks or path issues."""


class IntegrityError(DatabaseError):
    """Raised for constraint violations."""


class InternalError(DatabaseError):
    """Raised when SQLite reports an internal failure."""


class ProgrammingError(DatabaseError):
    """Raised for invalid SQL or programming mistakes."""


class NotSupportedError(DatabaseError):
    """Raised for unsupported SQLite features."""


class ConfigurationError(InterfaceError):
    """Raised for invalid client configuration."""


class ValidationError(InterfaceError):
    """Raised when helper-method inputs are malformed."""


class InvalidIdentifierError(ValidationError):
    """Raised when a SQL identifier fails safety validation."""


class ConnectionClosedError(InterfaceError):
    """Raised when an operation is attempted on a closed connection."""
