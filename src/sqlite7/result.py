"""Result primitives for sqlite7."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class StatementResult:
    """Structured metadata about a write statement.

    Attributes:
        rowcount: Number of affected rows reported by SQLite.
        lastrowid: Last inserted row id, when available.
    """

    rowcount: int
    lastrowid: int | None = None


RowDict = dict[str, Any]
