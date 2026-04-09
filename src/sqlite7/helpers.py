"""Internal helper utilities for sqlite7."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from . import exc

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(value: str, *, kind: str = "identifier") -> str:
    if not isinstance(value, str):
        raise exc.InvalidIdentifierError(f"{kind} must be a string")
    if not value:
        raise exc.InvalidIdentifierError(f"{kind} must not be empty")
    if not _IDENTIFIER_RE.fullmatch(value):
        raise exc.InvalidIdentifierError(
            f"Invalid {kind}: {value!r}. Only letters, numbers, and underscores are allowed, and it must not start with a number."
        )
    return value


def quote_identifier(value: str) -> str:
    return f'"{validate_identifier(value)}"'


def normalize_params(params: Sequence[Any] | None) -> Sequence[Any]:
    if params is None:
        return ()
    if isinstance(params, Mapping):
        raise exc.ValidationError(
            "Named SQL parameters are no longer supported. Use positional parameters with ? placeholders instead."
        )
    return params


def ensure_mapping_row(row: Any, *, index: int) -> Mapping[str, Any]:
    if not isinstance(row, Mapping):
        raise exc.ValidationError(
            f"rows[{index}] must be a mapping of column names to values; got {type(row).__name__}"
        )
    if not row:
        raise exc.ValidationError(f"rows[{index}] must not be empty")
    for key in row.keys():
        validate_identifier(str(key), kind="column name")
    return row


def ensure_consistent_rows(rows: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    materialized = [ensure_mapping_row(row, index=index) for index, row in enumerate(rows)]
    if not materialized:
        raise exc.ValidationError("rows must contain at least one item")
    first_keys = list(materialized[0].keys())
    for index, row in enumerate(materialized[1:], start=1):
        row_keys = list(row.keys())
        if row_keys != first_keys:
            raise exc.ValidationError(
                f"rows[{index}] has different keys. Expected {first_keys!r}, got {row_keys!r}"
            )
    return materialized


def build_assignment_list(columns: Sequence[str]) -> str:
    return ", ".join(f"{quote_identifier(column)} = ?" for column in columns)


def build_placeholders(count: int) -> str:
    return ", ".join("?" for _ in range(count))


def map_sqlite_exception(error: BaseException) -> exc.Error:
    if isinstance(error, exc.Error):
        return error
    return exc.Error(str(error), original=error)
