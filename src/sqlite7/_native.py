from __future__ import annotations

import ctypes
import ctypes.util
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Callable

from . import exc
from .result import RowDict, StatementResult

SQLITE_OK = 0
SQLITE_ERROR = 1
SQLITE_INTERNAL = 2
SQLITE_PERM = 3
SQLITE_ABORT = 4
SQLITE_BUSY = 5
SQLITE_LOCKED = 6
SQLITE_NOMEM = 7
SQLITE_READONLY = 8
SQLITE_INTERRUPT = 9
SQLITE_IOERR = 10
SQLITE_CORRUPT = 11
SQLITE_NOTFOUND = 12
SQLITE_FULL = 13
SQLITE_CANTOPEN = 14
SQLITE_PROTOCOL = 15
SQLITE_EMPTY = 16
SQLITE_SCHEMA = 17
SQLITE_TOOBIG = 18
SQLITE_CONSTRAINT = 19
SQLITE_MISMATCH = 20
SQLITE_MISUSE = 21
SQLITE_NOLFS = 22
SQLITE_AUTH = 23
SQLITE_FORMAT = 24
SQLITE_RANGE = 25
SQLITE_NOTADB = 26
SQLITE_NOTICE = 27
SQLITE_WARNING = 28
SQLITE_ROW = 100
SQLITE_DONE = 101

SQLITE_INTEGER = 1
SQLITE_FLOAT = 2
SQLITE_TEXT = 3
SQLITE_BLOB = 4
SQLITE_NULL = 5

SQLITE_OPEN_READWRITE = 0x00000002
SQLITE_OPEN_CREATE = 0x00000004
SQLITE_OPEN_URI = 0x00000040
SQLITE_OPEN_NOMUTEX = 0x00008000
SQLITE_OPEN_FULLMUTEX = 0x00010000

SQLITE_TRANSIENT = ctypes.c_void_p(-1)

ERR_NAMES = {
    SQLITE_OK: "SQLITE_OK",
    SQLITE_ERROR: "SQLITE_ERROR",
    SQLITE_INTERNAL: "SQLITE_INTERNAL",
    SQLITE_PERM: "SQLITE_PERM",
    SQLITE_ABORT: "SQLITE_ABORT",
    SQLITE_BUSY: "SQLITE_BUSY",
    SQLITE_LOCKED: "SQLITE_LOCKED",
    SQLITE_NOMEM: "SQLITE_NOMEM",
    SQLITE_READONLY: "SQLITE_READONLY",
    SQLITE_INTERRUPT: "SQLITE_INTERRUPT",
    SQLITE_IOERR: "SQLITE_IOERR",
    SQLITE_CORRUPT: "SQLITE_CORRUPT",
    SQLITE_NOTFOUND: "SQLITE_NOTFOUND",
    SQLITE_FULL: "SQLITE_FULL",
    SQLITE_CANTOPEN: "SQLITE_CANTOPEN",
    SQLITE_PROTOCOL: "SQLITE_PROTOCOL",
    SQLITE_EMPTY: "SQLITE_EMPTY",
    SQLITE_SCHEMA: "SQLITE_SCHEMA",
    SQLITE_TOOBIG: "SQLITE_TOOBIG",
    SQLITE_CONSTRAINT: "SQLITE_CONSTRAINT",
    SQLITE_MISMATCH: "SQLITE_MISMATCH",
    SQLITE_MISUSE: "SQLITE_MISUSE",
    SQLITE_NOLFS: "SQLITE_NOLFS",
    SQLITE_AUTH: "SQLITE_AUTH",
    SQLITE_FORMAT: "SQLITE_FORMAT",
    SQLITE_RANGE: "SQLITE_RANGE",
    SQLITE_NOTADB: "SQLITE_NOTADB",
    SQLITE_NOTICE: "SQLITE_NOTICE",
    SQLITE_WARNING: "SQLITE_WARNING",
}


def _load_sqlite() -> ctypes.CDLL:
    library = ctypes.util.find_library("sqlite3")
    if not library:
        raise RuntimeError("Could not locate libsqlite3")
    return ctypes.CDLL(library)


_lib = _load_sqlite()

sqlite3_p = ctypes.c_void_p
sqlite3_stmt_p = ctypes.c_void_p

_lib.sqlite3_open_v2.argtypes = [ctypes.c_char_p, ctypes.POINTER(sqlite3_p), ctypes.c_int, ctypes.c_char_p]
_lib.sqlite3_open_v2.restype = ctypes.c_int
_lib.sqlite3_close_v2.argtypes = [sqlite3_p]
_lib.sqlite3_close_v2.restype = ctypes.c_int
_lib.sqlite3_errmsg.argtypes = [sqlite3_p]
_lib.sqlite3_errmsg.restype = ctypes.c_char_p
_lib.sqlite3_errcode.argtypes = [sqlite3_p]
_lib.sqlite3_errcode.restype = ctypes.c_int
_lib.sqlite3_extended_errcode.argtypes = [sqlite3_p]
_lib.sqlite3_extended_errcode.restype = ctypes.c_int
_lib.sqlite3_exec.argtypes = [sqlite3_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p)]
_lib.sqlite3_exec.restype = ctypes.c_int
_lib.sqlite3_prepare_v2.argtypes = [sqlite3_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(sqlite3_stmt_p), ctypes.POINTER(ctypes.c_char_p)]
_lib.sqlite3_prepare_v2.restype = ctypes.c_int
_lib.sqlite3_step.argtypes = [sqlite3_stmt_p]
_lib.sqlite3_step.restype = ctypes.c_int
_lib.sqlite3_finalize.argtypes = [sqlite3_stmt_p]
_lib.sqlite3_finalize.restype = ctypes.c_int
_lib.sqlite3_reset.argtypes = [sqlite3_stmt_p]
_lib.sqlite3_reset.restype = ctypes.c_int
_lib.sqlite3_clear_bindings.argtypes = [sqlite3_stmt_p]
_lib.sqlite3_clear_bindings.restype = ctypes.c_int
_lib.sqlite3_bind_parameter_count.argtypes = [sqlite3_stmt_p]
_lib.sqlite3_bind_parameter_count.restype = ctypes.c_int
_lib.sqlite3_bind_null.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_bind_null.restype = ctypes.c_int
_lib.sqlite3_bind_int64.argtypes = [sqlite3_stmt_p, ctypes.c_int, ctypes.c_longlong]
_lib.sqlite3_bind_int64.restype = ctypes.c_int
_lib.sqlite3_bind_double.argtypes = [sqlite3_stmt_p, ctypes.c_int, ctypes.c_double]
_lib.sqlite3_bind_double.restype = ctypes.c_int
_lib.sqlite3_bind_text.argtypes = [sqlite3_stmt_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p]
_lib.sqlite3_bind_text.restype = ctypes.c_int
_lib.sqlite3_bind_blob.argtypes = [sqlite3_stmt_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
_lib.sqlite3_bind_blob.restype = ctypes.c_int
_lib.sqlite3_column_count.argtypes = [sqlite3_stmt_p]
_lib.sqlite3_column_count.restype = ctypes.c_int
_lib.sqlite3_column_name.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_name.restype = ctypes.c_char_p
_lib.sqlite3_column_type.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_type.restype = ctypes.c_int
_lib.sqlite3_column_int64.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_int64.restype = ctypes.c_longlong
_lib.sqlite3_column_double.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_double.restype = ctypes.c_double
_lib.sqlite3_column_text.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_text.restype = ctypes.POINTER(ctypes.c_ubyte)
_lib.sqlite3_column_blob.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_blob.restype = ctypes.c_void_p
_lib.sqlite3_column_bytes.argtypes = [sqlite3_stmt_p, ctypes.c_int]
_lib.sqlite3_column_bytes.restype = ctypes.c_int
_lib.sqlite3_changes.argtypes = [sqlite3_p]
_lib.sqlite3_changes.restype = ctypes.c_int
_lib.sqlite3_total_changes.argtypes = [sqlite3_p]
_lib.sqlite3_total_changes.restype = ctypes.c_int
_lib.sqlite3_last_insert_rowid.argtypes = [sqlite3_p]
_lib.sqlite3_last_insert_rowid.restype = ctypes.c_longlong
_lib.sqlite3_get_autocommit.argtypes = [sqlite3_p]
_lib.sqlite3_get_autocommit.restype = ctypes.c_int
_lib.sqlite3_libversion.restype = ctypes.c_char_p
_lib.sqlite3_complete.argtypes = [ctypes.c_char_p]
_lib.sqlite3_complete.restype = ctypes.c_int


class Row(tuple):
    pass


class Binary(bytes):
    pass


PARSE_DECLTYPES = 0
PARSE_COLNAMES = 0


def register_adapter(*args: Any, **kwargs: Any) -> None:
    return None


def register_converter(*args: Any, **kwargs: Any) -> None:
    return None


def complete_statement(statement: str) -> bool:
    return bool(_lib.sqlite3_complete(statement.encode("utf-8")))


class NativeCursor:
    def __init__(self, description: list[tuple[str, None, None, None, None, None, None]]) -> None:
        self.description = description


class NativeConnection:
    def __init__(
        self,
        path: str | Path,
        *,
        uri: bool = False,
        check_same_thread: bool = False,
        row_factory: Callable[[NativeCursor, tuple[Any, ...]], Any] | None = None,
        statement_cache_size: int = 128,
    ) -> None:
        self.path = str(path)
        self.row_factory = row_factory
        self._statement_cache_size = max(int(statement_cache_size), 0)
        self._statement_cache: OrderedDict[str, NativeStatement] = OrderedDict()
        self._db = sqlite3_p()
        flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE
        flags |= SQLITE_OPEN_FULLMUTEX if check_same_thread else SQLITE_OPEN_NOMUTEX
        if uri:
            flags |= SQLITE_OPEN_URI
        rc = _lib.sqlite3_open_v2(self.path.encode("utf-8"), ctypes.byref(self._db), flags, None)
        if rc != SQLITE_OK:
            try:
                raise sqlite_error_from_db(self._db, rc)
            finally:
                if self._db:
                    _lib.sqlite3_close_v2(self._db)
                    self._db = sqlite3_p()

    @property
    def handle(self) -> sqlite3_p:
        if not self._db:
            raise exc.ConnectionClosedError("The database connection is closed")
        return self._db

    def close(self) -> None:
        if not self._db:
            return
        for statement in self._statement_cache.values():
            statement.close()
        self._statement_cache.clear()
        rc = _lib.sqlite3_close_v2(self._db)
        if rc != SQLITE_OK:
            raise sqlite_error_from_db(self._db, rc)
        self._db = sqlite3_p()

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> tuple[StatementResult, list[Any], list[tuple[str, None, None, None, None, None, None]]]:
        statement = self._acquire_statement(sql)
        try:
            statement.bind(params or ())
            rows = statement.fetch_all()
            return statement.result(), rows, statement.description
        finally:
            self._release_statement(sql, statement)

    def executemany(self, sql: str, seq_of_params: Sequence[Sequence[Any]]) -> StatementResult:
        statement = self._acquire_statement(sql)
        try:
            total_changes_before = _lib.sqlite3_total_changes(self.handle)
            lastrowid: int | None = None
            for params in seq_of_params:
                statement.bind(params)
                statement.run_to_completion()
                lastrowid = int(_lib.sqlite3_last_insert_rowid(self.handle))
                statement.reset()
            total_delta = _lib.sqlite3_total_changes(self.handle) - total_changes_before
            return StatementResult(rowcount=total_delta, lastrowid=lastrowid)
        finally:
            self._release_statement(sql, statement)

    def _acquire_statement(self, sql: str) -> "NativeStatement":
        statement = self._statement_cache.pop(sql, None)
        if statement is not None:
            statement.reset()
            return statement
        return NativeStatement(self, sql)

    def _release_statement(self, sql: str, statement: "NativeStatement") -> None:
        statement.reset()
        if self._statement_cache_size <= 0:
            statement.close()
            return
        self._statement_cache[sql] = statement
        self._statement_cache.move_to_end(sql)
        while len(self._statement_cache) > self._statement_cache_size:
            _, evicted = self._statement_cache.popitem(last=False)
            evicted.close()

    def exec_script(self, sql_script: str) -> None:
        errmsg = ctypes.c_char_p()
        rc = _lib.sqlite3_exec(self.handle, sql_script.encode("utf-8"), None, None, ctypes.byref(errmsg))
        if rc != SQLITE_OK:
            message = errmsg.value.decode("utf-8", errors="replace") if errmsg.value else self.errmsg()
            raise sqlite_error_from_result(rc, message)

    def errmsg(self) -> str:
        return _lib.sqlite3_errmsg(self.handle).decode("utf-8", errors="replace")

    @property
    def total_changes(self) -> int:
        return int(_lib.sqlite3_total_changes(self.handle))

    @property
    def in_transaction(self) -> bool:
        return not bool(_lib.sqlite3_get_autocommit(self.handle))


class NativeStatement:
    def __init__(self, connection: NativeConnection, sql: str) -> None:
        self.connection = connection
        self.sql = sql
        self._stmt = sqlite3_stmt_p()
        tail = ctypes.c_char_p()
        rc = _lib.sqlite3_prepare_v2(connection.handle, sql.encode("utf-8"), -1, ctypes.byref(self._stmt), ctypes.byref(tail))
        if rc != SQLITE_OK:
            raise sqlite_error_from_db(connection.handle, rc)
        self._keepalive: list[Any] = []
        self.description = self._build_description()

    def _build_description(self) -> list[tuple[str, None, None, None, None, None, None]]:
        count = _lib.sqlite3_column_count(self._stmt)
        return [(_lib.sqlite3_column_name(self._stmt, i).decode("utf-8"), None, None, None, None, None, None) for i in range(count)]

    def bind(self, params: Sequence[Any]) -> None:
        self.reset()
        count = _lib.sqlite3_bind_parameter_count(self._stmt)
        if len(params) != count:
            raise exc.ProgrammingError(f"Expected {count} SQL parameters but received {len(params)}")
        self._keepalive.clear()
        for index, value in enumerate(params, start=1):
            self._bind_one(index, value)

    def _bind_one(self, index: int, value: Any) -> None:
        if value is None:
            rc = _lib.sqlite3_bind_null(self._stmt, index)
        elif isinstance(value, bool):
            rc = _lib.sqlite3_bind_int64(self._stmt, index, int(value))
        elif isinstance(value, int):
            rc = _lib.sqlite3_bind_int64(self._stmt, index, value)
        elif isinstance(value, float):
            rc = _lib.sqlite3_bind_double(self._stmt, index, value)
        elif isinstance(value, (bytes, bytearray, memoryview, Binary)):
            data = bytes(value)
            buffer = ctypes.create_string_buffer(data)
            self._keepalive.append(buffer)
            rc = _lib.sqlite3_bind_blob(self._stmt, index, ctypes.cast(buffer, ctypes.c_void_p), len(data), SQLITE_TRANSIENT)
        else:
            encoded = str(value).encode("utf-8")
            buffer = ctypes.create_string_buffer(encoded)
            self._keepalive.append(buffer)
            rc = _lib.sqlite3_bind_text(self._stmt, index, ctypes.cast(buffer, ctypes.c_char_p), len(encoded), SQLITE_TRANSIENT)
        if rc != SQLITE_OK:
            raise sqlite_error_from_db(self.connection.handle, rc)

    def run_to_completion(self) -> None:
        while True:
            rc = _lib.sqlite3_step(self._stmt)
            if rc == SQLITE_DONE:
                return
            if rc == SQLITE_ROW:
                continue
            raise sqlite_error_from_db(self.connection.handle, rc)

    def fetch_all(self) -> list[Any]:
        rows: list[Any] = []
        while True:
            rc = _lib.sqlite3_step(self._stmt)
            if rc == SQLITE_ROW:
                row_tuple = self._read_row()
                if self.connection.row_factory is None:
                    rows.append({desc[0]: row_tuple[i] for i, desc in enumerate(self.description)})
                else:
                    rows.append(self.connection.row_factory(NativeCursor(self.description), row_tuple))
            elif rc == SQLITE_DONE:
                break
            else:
                raise sqlite_error_from_db(self.connection.handle, rc)
        return rows

    def _read_row(self) -> tuple[Any, ...]:
        values: list[Any] = []
        for i in range(len(self.description)):
            col_type = _lib.sqlite3_column_type(self._stmt, i)
            if col_type == SQLITE_NULL:
                values.append(None)
            elif col_type == SQLITE_INTEGER:
                values.append(int(_lib.sqlite3_column_int64(self._stmt, i)))
            elif col_type == SQLITE_FLOAT:
                values.append(float(_lib.sqlite3_column_double(self._stmt, i)))
            elif col_type == SQLITE_TEXT:
                size = _lib.sqlite3_column_bytes(self._stmt, i)
                ptr = _lib.sqlite3_column_text(self._stmt, i)
                values.append(ctypes.string_at(ptr, size).decode("utf-8", errors="replace"))
            elif col_type == SQLITE_BLOB:
                size = _lib.sqlite3_column_bytes(self._stmt, i)
                ptr = _lib.sqlite3_column_blob(self._stmt, i)
                values.append(ctypes.string_at(ptr, size))
            else:
                values.append(None)
        return tuple(values)

    def result(self) -> StatementResult:
        return StatementResult(
            rowcount=int(_lib.sqlite3_changes(self.connection.handle)),
            lastrowid=int(_lib.sqlite3_last_insert_rowid(self.connection.handle)),
        )

    def reset(self) -> None:
        if not self._stmt:
            return
        _lib.sqlite3_reset(self._stmt)
        _lib.sqlite3_clear_bindings(self._stmt)
        self._keepalive.clear()

    def close(self) -> None:
        if self._stmt:
            _lib.sqlite3_finalize(self._stmt)
            self._stmt = sqlite3_stmt_p()


def sqlite_error_from_result(result_code: int, message: str) -> exc.Error:
    details = exc.SQLiteErrorDetails(errorcode=result_code, errorname=ERR_NAMES.get(result_code))
    base = result_code & 0xFF
    if base in {SQLITE_CONSTRAINT}:
        target = exc.IntegrityError
    elif base in {SQLITE_INTERNAL}:
        target = exc.InternalError
    elif base in {SQLITE_MISUSE, SQLITE_RANGE, SQLITE_SCHEMA}:
        target = exc.ProgrammingError
    elif base in {SQLITE_BUSY, SQLITE_LOCKED, SQLITE_CANTOPEN, SQLITE_IOERR, SQLITE_READONLY, SQLITE_INTERRUPT}:
        target = exc.OperationalError
    elif base in {SQLITE_NOTADB, SQLITE_CORRUPT, SQLITE_FULL, SQLITE_ERROR}:
        target = exc.DatabaseError
    elif base in {SQLITE_MISMATCH, SQLITE_TOOBIG}:
        target = exc.DataError
    elif base in {SQLITE_NOTFOUND, SQLITE_AUTH, SQLITE_FORMAT, SQLITE_NOLFS}:
        target = exc.NotSupportedError
    else:
        target = exc.Error
    return target(message, details=details)


def sqlite_error_from_db(db: sqlite3_p, fallback_code: int | None = None) -> exc.Error:
    if db:
        code = int(_lib.sqlite3_extended_errcode(db))
        message = _lib.sqlite3_errmsg(db).decode("utf-8", errors="replace")
        return sqlite_error_from_result(code or fallback_code or SQLITE_ERROR, message)
    return sqlite_error_from_result(fallback_code or SQLITE_ERROR, "SQLite error")


def sqlite_version() -> str:
    return _lib.sqlite3_libversion().decode("ascii")
