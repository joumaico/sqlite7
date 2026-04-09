"""
This module was written by Joumaico Maulas. It provides an SQL
interface inspired by the DB-API 2.0 specification described by PEP 249,
and requires the third-party SQLite library.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._native import (
    Binary,
    PARSE_COLNAMES,
    PARSE_DECLTYPES,
    Row,
    complete_statement,
    register_adapter,
    register_converter,
)
from .async_database import AsyncDatabase, AsyncTable
from .exc import (
    ConfigurationError,
    ConnectionClosedError,
    DataError,
    DatabaseError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    InvalidIdentifierError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    SQLite7Error,
    ValidationError,
    Warning,
)
from .result import RowDict, StatementResult
from .database import Database, Table

__all__ = [
    "AsyncDatabase",
    "AsyncTable",
    "ConfigurationError",
    "ConnectionClosedError",
    "DataError",
    "Database",
    "DatabaseError",
    "Error",
    "IntegrityError",
    "InterfaceError",
    "InternalError",
    "InvalidIdentifierError",
    "NotSupportedError",
    "OperationalError",
    "ProgrammingError",
    "RowDict",
    "SQLite7Error",
    "StatementResult",
    "Table",
    "ValidationError",
    "Warning",
    "connect",
    "open_db",
    "connect_async",
    "open_async",
    "Binary",
    "Row",
    "PARSE_COLNAMES",
    "PARSE_DECLTYPES",
    "register_adapter",
    "register_converter",
    "complete_statement",
]


def connect(path: str | Path, **kwargs: Any) -> Database:
    return Database(path, **kwargs)


def connect_async(path: str | Path, **kwargs: Any) -> AsyncDatabase:
    return AsyncDatabase(path, **kwargs)


open_db = connect
open_async = connect_async
