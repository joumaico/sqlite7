"""Transaction context manager for the synchronous sqlite7 client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database


@dataclass(slots=True)
class Transaction:
    """Synchronous transaction context manager with savepoint nesting support."""

    database: "Database"

    def __enter__(self) -> "Database":
        self.database._enter_transaction()
        return self.database

    def __exit__(self, exc_type, exc, tb) -> None:
        self.database._exit_transaction(exc is None)
