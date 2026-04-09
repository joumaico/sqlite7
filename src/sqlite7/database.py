"""Synchronous SQLite client for sqlite7 using the SQLite C API directly."""

from __future__ import annotations

import contextlib
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Callable

from . import exc
from ._native import NativeConnection, NativeCursor
from .dialect import insert_keyword
from .helpers import (
    build_assignment_list,
    build_placeholders,
    ensure_consistent_rows,
    map_sqlite_exception,
    normalize_params,
    quote_identifier,
    validate_identifier,
)
from .result import RowDict, StatementResult
from .transaction import Transaction

RowFactory = Callable[[NativeCursor, tuple[Any, ...]], Any]


class Database:
    """User-friendly synchronous SQLite client backed by libsqlite3."""

    def __init__(
        self,
        path: str | Path,
        *,
        timeout: float = 30.0,
        detect_types: int = 0,
        isolation_level: str | None = None,
        pragmas: Mapping[str, Any] | None = None,
        row_factory: RowFactory | None = None,
        uri: bool = False,
        check_same_thread: bool = False,
        statement_cache_size: int = 128,
    ) -> None:
        self.path = str(path)
        self.timeout = timeout
        self.detect_types = detect_types
        self.isolation_level = isolation_level
        self.pragmas = dict(pragmas or {})
        self._row_factory = row_factory
        self.uri = uri
        self.check_same_thread = check_same_thread
        self.statement_cache_size = max(int(statement_cache_size), 0)
        self._connection: NativeConnection | None = None
        self._transaction_depth = 0
        self._savepoint_index = 0
        self._savepoint_stack: list[str] = []
        self._connect()

    def _connect(self) -> None:
        if self._connection is not None:
            return
        try:
            self._connection = NativeConnection(
                self.path,
                uri=self.uri,
                check_same_thread=self.check_same_thread,
                row_factory=self._row_factory or self._dict_row_factory,
                statement_cache_size=self.statement_cache_size,
            )
            self._apply_default_pragmas()
            self._apply_user_pragmas()
        except Exception as error:
            raise map_sqlite_exception(error) from error

    @staticmethod
    def _dict_row_factory(cursor: NativeCursor, row: tuple[Any, ...]) -> RowDict:
        return {description[0]: row[index] for index, description in enumerate(cursor.description)}

    @property
    def connection(self) -> NativeConnection:
        if self._connection is None:
            raise exc.ConnectionClosedError("The database connection is closed")
        return self._connection

    def close(self) -> None:
        if self._connection is None:
            return
        try:
            self._connection.close()
        except Exception as error:
            raise map_sqlite_exception(error) from error
        finally:
            self._connection = None

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _apply_default_pragmas(self) -> None:
        defaults = {
            "foreign_keys": "ON",
            "journal_mode": "WAL",
            "busy_timeout": int(self.timeout * 1000),
            "synchronous": "NORMAL",
            "temp_store": "MEMORY",
            "cache_size": -8000,
            "mmap_size": 268435456,
        }
        for key, value in defaults.items():
            self._set_pragma(key, value)
        with contextlib.suppress(Exception):
            self.execute("PRAGMA optimize")

    def _apply_user_pragmas(self) -> None:
        for key, value in self.pragmas.items():
            self._set_pragma(key, value)

    def _set_pragma(self, key: str, value: Any) -> None:
        validate_identifier(key, kind="pragma name")
        rendered = f"'{value}'" if isinstance(value, str) and not value.isupper() else value
        self.execute(f"PRAGMA {key} = {rendered}")

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> StatementResult:
        try:
            result, _, _ = self.connection.execute(sql, normalize_params(params))
            return result
        except Exception as error:
            raise map_sqlite_exception(error) from error

    def executemany(self, sql: str, seq_of_params: Iterable[Sequence[Any]]) -> StatementResult:
        normalized_params = [tuple(normalize_params(params)) for params in seq_of_params]
        try:
            return self.connection.executemany(sql, normalized_params)
        except Exception as error:
            raise map_sqlite_exception(error) from error

    def script(self, sql_script: str) -> None:
        try:
            self.connection.exec_script(sql_script)
        except Exception as error:
            raise map_sqlite_exception(error) from error

    def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[RowDict]:
        try:
            _, rows, _ = self.connection.execute(sql, normalize_params(params))
            return list(rows)
        except Exception as error:
            raise map_sqlite_exception(error) from error

    def fetch_one(self, sql: str, params: Sequence[Any] | None = None) -> RowDict | None:
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def fetch_value(self, sql: str, params: Sequence[Any] | None = None, *, default: Any = None) -> Any:
        row = self.fetch_one(sql, params)
        if row is None:
            return default
        return next(iter(row.values()))

    def select(
        self,
        table: str,
        *,
        columns: Sequence[str] | None = None,
        where: str | None = None,
        params: Sequence[Any] | None = None,
        group_by: str | None = None,
        having: str | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        distinct: bool = False,
    ) -> list[RowDict]:
        table_sql = quote_identifier(table)
        column_sql = ", ".join(quote_identifier(column) for column in columns) if columns else "*"
        prefix = "SELECT DISTINCT" if distinct else "SELECT"
        sql = f"{prefix} {column_sql} FROM {table_sql}"
        if where:
            sql += f" WHERE {where}"
        if group_by:
            sql += f" GROUP BY {group_by}"
        if having:
            sql += f" HAVING {having}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        elif offset is not None:
            sql += " LIMIT -1"
        if offset is not None:
            sql += f" OFFSET {int(offset)}"
        return self.fetch_all(sql, params)

    def insert(self, table: str, values: Mapping[str, Any], *, on_conflict: str = "abort") -> StatementResult:
        rows = ensure_consistent_rows([values])
        return self.insert_many(table, rows, on_conflict=on_conflict)

    def insert_many(
        self,
        table: str,
        rows: Iterable[Mapping[str, Any]],
        *,
        on_conflict: str = "abort",
        chunk_size: int = 500,
    ) -> StatementResult:
        materialized = ensure_consistent_rows(rows)
        table_sql = quote_identifier(table)
        columns = list(materialized[0].keys())
        column_sql = ", ".join(quote_identifier(column) for column in columns)
        placeholders = build_placeholders(len(columns))
        sql = f"{insert_keyword(on_conflict)} INTO {table_sql} ({column_sql}) VALUES ({placeholders})"

        total_rowcount = 0
        lastrowid: int | None = None
        size = max(int(chunk_size), 1)
        for start in range(0, len(materialized), size):
            chunk = materialized[start: start + size]
            params = [tuple(row[column] for column in columns) for row in chunk]
            result = self.executemany(sql, params)
            total_rowcount += max(result.rowcount, 0)
            if result.lastrowid is not None:
                lastrowid = result.lastrowid
        return StatementResult(rowcount=total_rowcount, lastrowid=lastrowid)

    def update(
        self,
        table: str,
        values: Mapping[str, Any],
        *,
        where: str,
        params: Sequence[Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> StatementResult:
        if not values:
            raise exc.ValidationError("values must not be empty")
        columns = [validate_identifier(str(column), kind="column name") for column in values.keys()]
        assignments = build_assignment_list(columns)
        sql = f"UPDATE {quote_identifier(table)} SET {assignments} WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        final_params = [values[column] for column in columns]
        if params:
            final_params.extend(params)
        return self.execute(sql, tuple(final_params))

    def delete(
        self,
        table: str,
        *,
        where: str,
        params: Sequence[Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> StatementResult:
        sql = f"DELETE FROM {quote_identifier(table)} WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return self.execute(sql, params)

    def upsert(
        self,
        table: str,
        values: Mapping[str, Any],
        *,
        conflict_columns: Sequence[str],
        update_columns: Sequence[str] | None = None,
    ) -> StatementResult:
        row = ensure_consistent_rows([values])[0]
        columns = list(row.keys())
        target_columns = [validate_identifier(column, kind="conflict column") for column in conflict_columns]
        mutable_columns = list(update_columns) if update_columns is not None else [
            column for column in columns if column not in target_columns
        ]
        for column in mutable_columns:
            validate_identifier(column, kind="update column")

        table_sql = quote_identifier(table)
        column_sql = ", ".join(quote_identifier(column) for column in columns)
        placeholders = build_placeholders(len(columns))
        conflict_sql = ", ".join(quote_identifier(column) for column in target_columns)
        if mutable_columns:
            assignments = ", ".join(
                f'{quote_identifier(column)} = excluded.{quote_identifier(column)}' for column in mutable_columns
            )
            action = f"DO UPDATE SET {assignments}"
        else:
            action = "DO NOTHING"
        sql = (
            f"INSERT INTO {table_sql} ({column_sql}) VALUES ({placeholders}) "
            f"ON CONFLICT ({conflict_sql}) {action}"
        )
        final_params = tuple(row[column] for column in columns)
        return self.execute(sql, final_params)

    def count(self, table: str, *, where: str | None = None, params: Sequence[Any] | None = None) -> int:
        sql = f"SELECT COUNT(*) FROM {quote_identifier(table)}"
        if where:
            sql += f" WHERE {where}"
        return int(self.fetch_value(sql, params, default=0))

    def exists(self, table: str, *, where: str | None = None, params: Sequence[Any] | None = None) -> bool:
        return self.count(table, where=where, params=params) > 0

    def table(self, name: str) -> "Table":
        return Table(self, name)

    def transaction(self) -> Transaction:
        return Transaction(self)

    def _enter_transaction(self) -> None:
        try:
            if self._transaction_depth == 0:
                self.execute("BEGIN")
            else:
                savepoint = self._next_savepoint_name()
                self.execute(f"SAVEPOINT {savepoint}")
                self._savepoint_stack.append(savepoint)
            self._transaction_depth += 1
        except Exception as error:
            raise map_sqlite_exception(error) from error

    def _exit_transaction(self, committed: bool) -> None:
        try:
            if self._transaction_depth <= 0:
                return
            if self._transaction_depth == 1:
                self.execute("COMMIT" if committed else "ROLLBACK")
            else:
                savepoint = self._current_savepoint_name()
                if committed:
                    self.execute(f"RELEASE SAVEPOINT {savepoint}")
                else:
                    self.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                    self.execute(f"RELEASE SAVEPOINT {savepoint}")
        except Exception as error:
            raise map_sqlite_exception(error) from error
        finally:
            if self._transaction_depth > 1 and self._savepoint_stack:
                self._savepoint_stack.pop()
            self._transaction_depth = max(self._transaction_depth - 1, 0)

    def _next_savepoint_name(self) -> str:
        self._savepoint_index += 1
        return f"sp_{self._savepoint_index}"

    def _current_savepoint_name(self) -> str:
        if not self._savepoint_stack:
            raise exc.InternalError("No active savepoint is available")
        return self._savepoint_stack[-1]

    def commit(self) -> None:
        self.execute("COMMIT")

    def rollback(self) -> None:
        self.execute("ROLLBACK")

    def backup(self, target: Any, *, pages: int = -1) -> None:
        raise exc.NotSupportedError("backup() is not yet implemented for the native backend")

    def iterdump(self) -> Iterator[str]:
        schema_rows = self.fetch_all(
            "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )
        for row in schema_rows:
            yield f"{row['sql']};"

    def create_function(self, name: str, narg: int, func: Callable[..., Any], *, deterministic: bool = False) -> None:
        raise exc.NotSupportedError("create_function() is not yet implemented for the native backend")

    def create_aggregate(self, name: str, n_arg: int, aggregate_class: type) -> None:
        raise exc.NotSupportedError("create_aggregate() is not yet implemented for the native backend")

    def create_collation(self, name: str, callable_: Callable[[str, str], int]) -> None:
        raise exc.NotSupportedError("create_collation() is not yet implemented for the native backend")

    @property
    def total_changes(self) -> int:
        return self.connection.total_changes

    @property
    def in_transaction(self) -> bool:
        return self.connection.in_transaction


class Table:
    """Table-bound helper that mirrors the Database query surface where it makes sense."""

    def __init__(self, database: Database, name: str) -> None:
        self.database = database
        self.name = validate_identifier(name, kind="table name")

    def close(self) -> None:
        self.database.close()

    def script(self, sql_script: str) -> None:
        self.database.script(sql_script)

    def commit(self) -> None:
        self.database.commit()

    def rollback(self) -> None:
        self.database.rollback()

    def backup(self, target: Any, *, pages: int = -1) -> None:
        self.database.backup(target, pages=pages)

    def iterdump(self) -> Iterator[str]:
        return self.database.iterdump()

    def create_function(self, name: str, narg: int, func: Callable[..., Any], *, deterministic: bool = False) -> None:
        self.database.create_function(name, narg, func, deterministic=deterministic)

    def create_aggregate(self, name: str, n_arg: int, aggregate_class: type) -> None:
        self.database.create_aggregate(name, n_arg, aggregate_class)

    def create_collation(self, name: str, callable_: Callable[[str, str], int]) -> None:
        self.database.create_collation(name, callable_)

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> StatementResult:
        return self.database.execute(sql, params)

    def executemany(self, sql: str, seq_of_params: Iterable[Sequence[Any]]) -> StatementResult:
        return self.database.executemany(sql, seq_of_params)

    def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[RowDict]:
        return self.database.fetch_all(sql, params)

    def fetch_one(self, sql: str, params: Sequence[Any] | None = None) -> RowDict | None:
        return self.database.fetch_one(sql, params)

    def fetch_value(self, sql: str, params: Sequence[Any] | None = None, *, default: Any = None) -> Any:
        return self.database.fetch_value(sql, params, default=default)

    def all(
        self,
        *,
        columns: Sequence[str] | None = None,
        where: str | None = None,
        params: Sequence[Any] | None = None,
        group_by: str | None = None,
        having: str | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        distinct: bool = False,
    ) -> list[RowDict]:
        return self.select(
            columns=columns,
            where=where,
            params=params,
            group_by=group_by,
            having=having,
            order_by=order_by,
            limit=limit,
            offset=offset,
            distinct=distinct,
        )

    def select(
        self,
        *,
        columns: Sequence[str] | None = None,
        where: str | None = None,
        params: Sequence[Any] | None = None,
        group_by: str | None = None,
        having: str | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        distinct: bool = False,
    ) -> list[RowDict]:
        return self.database.select(
            self.name,
            columns=columns,
            where=where,
            params=params,
            group_by=group_by,
            having=having,
            order_by=order_by,
            limit=limit,
            offset=offset,
            distinct=distinct,
        )

    def get(
        self,
        where: str,
        params: Sequence[Any] | None = None,
        *,
        columns: Sequence[str] | None = None,
        group_by: str | None = None,
        having: str | None = None,
        order_by: str | None = None,
        offset: int | None = None,
        distinct: bool = False,
    ) -> RowDict | None:
        rows = self.select(
            columns=columns,
            where=where,
            params=params,
            group_by=group_by,
            having=having,
            order_by=order_by,
            limit=1,
            offset=offset,
            distinct=distinct,
        )
        return rows[0] if rows else None

    def insert(self, values: Mapping[str, Any], *, on_conflict: str = "abort") -> StatementResult:
        return self.database.insert(self.name, values, on_conflict=on_conflict)

    def insert_many(
        self,
        rows: Iterable[Mapping[str, Any]],
        *,
        on_conflict: str = "abort",
        chunk_size: int = 500,
    ) -> StatementResult:
        return self.database.insert_many(self.name, rows, on_conflict=on_conflict, chunk_size=chunk_size)

    def update(
        self,
        values: Mapping[str, Any],
        *,
        where: str,
        params: Sequence[Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> StatementResult:
        return self.database.update(self.name, values, where=where, params=params, order_by=order_by, limit=limit)

    def delete(
        self,
        *,
        where: str,
        params: Sequence[Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> StatementResult:
        return self.database.delete(self.name, where=where, params=params, order_by=order_by, limit=limit)

    def upsert(
        self,
        values: Mapping[str, Any],
        *,
        conflict_columns: Sequence[str],
        update_columns: Sequence[str] | None = None,
    ) -> StatementResult:
        return self.database.upsert(
            self.name,
            values,
            conflict_columns=conflict_columns,
            update_columns=update_columns,
        )

    def count(self, *, where: str | None = None, params: Sequence[Any] | None = None) -> int:
        return self.database.count(self.name, where=where, params=params)

    def exists(self, *, where: str | None = None, params: Sequence[Any] | None = None) -> bool:
        return self.database.exists(self.name, where=where, params=params)

    def transaction(self) -> Transaction:
        return self.database.transaction()

    @property
    def total_changes(self) -> int:
        return self.database.total_changes

    @property
    def in_transaction(self) -> bool:
        return self.database.in_transaction
