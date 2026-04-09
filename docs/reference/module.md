# Module reference

This page summarizes the top-level surface of `sqlite7` and points developers toward the right entry points.

## Connection helpers

### `sqlite7.connect(path, **kwargs)`

Open a synchronous `Database`.

Use this when you want a DB-API-style entry point that feels familiar to developers who have used Python's built-in `sqlite3` module.

```python
from sqlite7 import connect

with connect(":memory:") as db:
    db.execute("SELECT 1")
```

### `sqlite7.open_db(path, **kwargs)`

Alias for `connect()`.

Use this when you want the call site to read more explicitly as “open a database.”

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("SELECT 1")
```

### `sqlite7.connect_async(path, **kwargs)`

Open an `AsyncDatabase`.

This is the async entry point for web handlers, async workers, and other asyncio-based code.

```python
import asyncio
from sqlite7 import connect_async

async def main():
    async with connect_async(":memory:") as db:
        await db.execute("SELECT 1")

asyncio.run(main())
```

### `sqlite7.open_async(path, **kwargs)`

Alias for `connect_async()`.

Use this when you want naming symmetry with `open_db()`.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("SELECT 1")

asyncio.run(main())
```

## SQL parsing helper

### `sqlite7.complete_statement(statement)`

Return `True` when SQLite considers a SQL string complete.

This is useful for shell-like tools, REPLs, migration editors, or developer tooling that needs to know whether a statement is ready to execute.

```python
from sqlite7 import complete_statement

print(complete_statement("SELECT 1;"))
print(complete_statement("SELECT"))
```

## Main classes

### `Database`

Synchronous database client for raw SQL and higher-level CRUD helpers.

Use it in scripts, CLIs, workers, and any synchronous service layer.

### `Table`

Table-bound helper for synchronous code.

Use it when one part of the codebase mainly interacts with a single table.

### `AsyncDatabase`

Async database client for asyncio-based applications.

Use it when database access needs to fit naturally into async request handlers, jobs, or event consumers.

### `AsyncTable`

Table-bound helper for async code.

Use it when an async component repeatedly targets one table.

### `StatementResult`

Small metadata object returned by write methods.

Useful when code needs to inspect affected-row counts or the last inserted id.

### `Row`

Compatibility export from the underlying SQLite layer.

Useful when code wants SQLite-style row behavior instead of the default dictionary rows.

## Constants

### `PARSE_DECLTYPES`

SQLite type-detection flag.

Use this when you want SQLite conversion behavior based on declared column types.

### `PARSE_COLNAMES`

SQLite type-detection flag.

Use this when you want conversion behavior based on column names in query results.

See the dedicated API pages for full method-level documentation.
