"""Asynchronous SQLite client for sqlite7 built on top of the native sync backend."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Sequence
from contextlib import AbstractAsyncContextManager
from typing import Any

from .database import Database, Table
from .result import RowDict, StatementResult


class _AsyncConnectionGate:
    """Task-aware reentrant gate that serializes access to a single connection."""

    __slots__ = ("_lock", "_owner", "_depth")

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._owner: asyncio.Task[Any] | None = None
        self._depth = 0

    def owned_by_current_task(self) -> bool:
        task = asyncio.current_task()
        return task is not None and task is self._owner

    async def acquire(self) -> None:
        task = asyncio.current_task()
        if task is not None and task is self._owner:
            self._depth += 1
            return
        await self._lock.acquire()
        self._owner = task
        self._depth = 1

    def release(self) -> None:
        task = asyncio.current_task()
        if task is not None and task is not self._owner:
            raise RuntimeError("sqlite7 async connection gate released by non-owner task")
        if self._depth <= 0:
            raise RuntimeError("sqlite7 async connection gate release without acquire")
        self._depth -= 1
        if self._depth == 0:
            self._owner = None
            self._lock.release()


class AsyncTransaction(AbstractAsyncContextManager["AsyncDatabase"]):
    __slots__ = ("database",)

    def __init__(self, database: "AsyncDatabase") -> None:
        self.database = database

    async def __aenter__(self) -> "AsyncDatabase":
        await self.database._gate.acquire()
        try:
            await asyncio.to_thread(self.database._db._enter_transaction)
        except Exception:
            self.database._gate.release()
            raise
        return self.database

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            await asyncio.to_thread(self.database._db._exit_transaction, exc is None)
        finally:
            self.database._gate.release()


class AsyncDatabase:
    """Async facade with method parity for the synchronous Database API."""

    __slots__ = ("_db", "_gate")

    def __init__(self, path: str, **kwargs: Any) -> None:
        self._db = Database(path, **kwargs)
        self._gate = _AsyncConnectionGate()

    async def _call(self, func, /, *args, **kwargs):
        if self._gate.owned_by_current_task():
            return await asyncio.to_thread(func, *args, **kwargs)
        await self._gate.acquire()
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        finally:
            self._gate.release()

    @property
    def path(self) -> str:
        return self._db.path

    @property
    def timeout(self) -> float:
        return self._db.timeout

    @property
    def detect_types(self) -> int:
        return self._db.detect_types

    @property
    def isolation_level(self) -> str | None:
        return self._db.isolation_level

    @property
    def pragmas(self) -> dict[str, Any]:
        return self._db.pragmas

    @property
    def uri(self) -> bool:
        return self._db.uri

    @property
    def check_same_thread(self) -> bool:
        return self._db.check_same_thread

    @property
    def statement_cache_size(self) -> int:
        return self._db.statement_cache_size

    @property
    def total_changes(self) -> int:
        return self._db.total_changes

    @property
    def in_transaction(self) -> bool:
        return self._db.in_transaction

    async def close(self) -> None:
        await self._call(self._db.close)

    async def __aenter__(self) -> "AsyncDatabase":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def execute(self, sql: str, params: Sequence[Any] | None = None) -> StatementResult:
        return await self._call(self._db.execute, sql, params)

    async def executemany(self, sql: str, seq_of_params: Iterable[Sequence[Any]]) -> StatementResult:
        materialized = tuple(tuple(params) for params in seq_of_params)
        return await self._call(self._db.executemany, sql, materialized)

    async def script(self, sql_script: str) -> None:
        await self._call(self._db.script, sql_script)

    async def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[RowDict]:
        return await self._call(self._db.fetch_all, sql, params)

    async def fetch_one(self, sql: str, params: Sequence[Any] | None = None) -> RowDict | None:
        return await self._call(self._db.fetch_one, sql, params)

    async def fetch_value(self, sql: str, params: Sequence[Any] | None = None, *, default: Any = None) -> Any:
        return await self._call(self._db.fetch_value, sql, params, default=default)

    async def select(self, table: str, **kwargs: Any) -> list[RowDict]:
        return await self._call(self._db.select, table, **kwargs)

    async def insert(self, table: str, values: dict[str, Any], *, on_conflict: str = "abort") -> StatementResult:
        return await self._call(self._db.insert, table, values, on_conflict=on_conflict)

    async def insert_many(
        self,
        table: str,
        rows: Iterable[dict[str, Any]],
        *,
        on_conflict: str = "abort",
        chunk_size: int = 500,
    ) -> StatementResult:
        materialized = tuple(dict(row) for row in rows)
        return await self._call(self._db.insert_many, table, materialized, on_conflict=on_conflict, chunk_size=chunk_size)

    async def update(self, table: str, values: dict[str, Any], **kwargs: Any) -> StatementResult:
        return await self._call(self._db.update, table, values, **kwargs)

    async def delete(self, table: str, **kwargs: Any) -> StatementResult:
        return await self._call(self._db.delete, table, **kwargs)

    async def upsert(self, table: str, values: dict[str, Any], **kwargs: Any) -> StatementResult:
        return await self._call(self._db.upsert, table, values, **kwargs)

    async def count(self, table: str, **kwargs: Any) -> int:
        return await self._call(self._db.count, table, **kwargs)

    async def exists(self, table: str, **kwargs: Any) -> bool:
        return await self._call(self._db.exists, table, **kwargs)

    def table(self, name: str) -> "AsyncTable":
        return AsyncTable(self, name)

    def transaction(self) -> AsyncTransaction:
        return AsyncTransaction(self)

    async def commit(self) -> None:
        await self._call(self._db.commit)

    async def rollback(self) -> None:
        await self._call(self._db.rollback)

    async def backup(self, target: Any, *, pages: int = -1) -> None:
        await self._call(self._db.backup, target, pages=pages)

    async def iterdump(self) -> list[str]:
        return await self._call(lambda: list(self._db.iterdump()))

    async def create_function(self, name: str, narg: int, func, *, deterministic: bool = False) -> None:
        await self._call(self._db.create_function, name, narg, func, deterministic=deterministic)

    async def create_aggregate(self, name: str, n_arg: int, aggregate_class: type) -> None:
        await self._call(self._db.create_aggregate, name, n_arg, aggregate_class)

    async def create_collation(self, name: str, callable_) -> None:
        await self._call(self._db.create_collation, name, callable_)


class AsyncTable:
    """Async table-bound facade with parity for the synchronous Table API."""

    __slots__ = ("database", "name")

    def __init__(self, database: AsyncDatabase, name: str) -> None:
        self.database = database
        self.name = name

    async def close(self) -> None:
        await self.database.close()

    async def script(self, sql_script: str) -> None:
        await self.database.script(sql_script)

    async def commit(self) -> None:
        await self.database.commit()

    async def rollback(self) -> None:
        await self.database.rollback()

    async def backup(self, target: Any, *, pages: int = -1) -> None:
        await self.database.backup(target, pages=pages)

    async def iterdump(self) -> list[str]:
        return await self.database.iterdump()

    async def create_function(self, name: str, narg: int, func, *, deterministic: bool = False) -> None:
        await self.database.create_function(name, narg, func, deterministic=deterministic)

    async def create_aggregate(self, name: str, n_arg: int, aggregate_class: type) -> None:
        await self.database.create_aggregate(name, n_arg, aggregate_class)

    async def create_collation(self, name: str, callable_) -> None:
        await self.database.create_collation(name, callable_)

    async def execute(self, sql: str, params: Sequence[Any] | None = None) -> StatementResult:
        return await self.database.execute(sql, params)

    async def executemany(self, sql: str, seq_of_params: Iterable[Sequence[Any]]) -> StatementResult:
        return await self.database.executemany(sql, seq_of_params)

    async def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[RowDict]:
        return await self.database.fetch_all(sql, params)

    async def fetch_one(self, sql: str, params: Sequence[Any] | None = None) -> RowDict | None:
        return await self.database.fetch_one(sql, params)

    async def fetch_value(self, sql: str, params: Sequence[Any] | None = None, *, default: Any = None) -> Any:
        return await self.database.fetch_value(sql, params, default=default)

    async def all(self, **kwargs: Any) -> list[RowDict]:
        return await self.select(**kwargs)

    async def select(self, **kwargs: Any) -> list[RowDict]:
        return await self.database.select(self.name, **kwargs)

    async def get(self, where: str, params: Sequence[Any] | None = None, **kwargs: Any) -> RowDict | None:
        options = dict(kwargs)
        options["where"] = where
        options["params"] = params
        options.setdefault("limit", 1)
        rows = await self.select(**options)
        return rows[0] if rows else None

    async def insert(self, values: dict[str, Any], *, on_conflict: str = "abort") -> StatementResult:
        return await self.database.insert(self.name, values, on_conflict=on_conflict)

    async def insert_many(self, rows: Iterable[dict[str, Any]], *, on_conflict: str = "abort", chunk_size: int = 500) -> StatementResult:
        return await self.database.insert_many(self.name, rows, on_conflict=on_conflict, chunk_size=chunk_size)

    async def update(self, values: dict[str, Any], **kwargs: Any) -> StatementResult:
        return await self.database.update(self.name, values, **kwargs)

    async def delete(self, **kwargs: Any) -> StatementResult:
        return await self.database.delete(self.name, **kwargs)

    async def upsert(self, values: dict[str, Any], **kwargs: Any) -> StatementResult:
        return await self.database.upsert(self.name, values, **kwargs)

    async def count(self, **kwargs: Any) -> int:
        return await self.database.count(self.name, **kwargs)

    async def exists(self, **kwargs: Any) -> bool:
        return await self.database.exists(self.name, **kwargs)

    def transaction(self) -> AsyncTransaction:
        return self.database.transaction()

    @property
    def total_changes(self) -> int:
        return self.database.total_changes

    @property
    def in_transaction(self) -> bool:
        return self.database.in_transaction
