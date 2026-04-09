# `AsyncDatabase`

`AsyncDatabase` is the asyncio-friendly version of `Database`.

Use it when your application already runs inside an async stack, such as FastAPI handlers, background workers, bots, or event-driven services. The API closely mirrors the synchronous client, so teams can move between sync and async code without learning two different mental models.

A key design detail is that one SQLite connection is still used safely: `sqlite7` serializes access so multiple tasks do not drive the same connection concurrently.

## Creating an async database

### `open_async(path, **kwargs)` / `connect_async(path, **kwargs)`

Open an `AsyncDatabase`.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("SELECT 1")

asyncio.run(main())
```

## Read-only properties

### `path`

Return the database path.

Helpful for diagnostics, logging, and confirming which database an async service is using.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("app.db") as db:
        print(db.path)

asyncio.run(main())
```

### `timeout`

Return the configured busy timeout.

Useful when debugging contention behavior in async services.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("app.db", timeout=10.0) as db:
        print(db.timeout)

asyncio.run(main())
```

### `detect_types`

Return the configured SQLite type-detection flags.

Helpful when developers need to confirm connection behavior around adapters and converters.

```python
import asyncio
from sqlite7 import PARSE_DECLTYPES, open_async

async def main():
    async with open_async("app.db", detect_types=PARSE_DECLTYPES) as db:
        print(db.detect_types)

asyncio.run(main())
```

### `isolation_level`

Return the configured isolation level value.

Useful when integrating with code that needs to understand transaction expectations.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("app.db", isolation_level=None) as db:
        print(db.isolation_level)

asyncio.run(main())
```

### `pragmas`

Return the configured pragma mapping.

Helpful for debugging connection tuning in production-like async environments.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("app.db", pragmas={"cache_size": -4000}) as db:
        print(db.pragmas)

asyncio.run(main())
```

### `uri`

Return whether URI mode is enabled.

Useful when teams use SQLite URI connection strings and want to verify that behavior explicitly.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("file:app.db?mode=rwc", uri=True) as db:
        print(db.uri)

asyncio.run(main())
```

### `check_same_thread`

Return the configured thread-safety flag.

Helpful mainly for debugging or confirming compatibility settings.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("app.db", check_same_thread=False) as db:
        print(db.check_same_thread)

asyncio.run(main())
```

### `statement_cache_size`

Return the configured statement cache size.

Useful for performance tuning conversations and connection introspection.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async("app.db", statement_cache_size=256) as db:
        print(db.statement_cache_size)

asyncio.run(main())
```

### `total_changes`

Return the number of rows changed during the lifetime of the connection.

Useful for instrumentation, tests, and sanity checks after async write flows.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE jobs (name TEXT)")
        await db.insert("jobs", {"name": "sync-users"})
        await db.insert("jobs", {"name": "sync-orders"})
        print(db.total_changes)

asyncio.run(main())
```

### `in_transaction`

Return whether the connection is currently inside a transaction.

Helpful for debugging async workflows that coordinate multiple writes.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        print(db.in_transaction)
        await db.execute("BEGIN")
        print(db.in_transaction)

asyncio.run(main())
```

## Connection lifecycle

### `close()`

Close the async database connection.

This helps long-running services release resources cleanly when a worker or application scope ends.

```python
import asyncio
from sqlite7 import open_async

async def main():
    db = open_async(":memory:")
    await db.execute("SELECT 1")
    await db.close()

asyncio.run(main())
```

## Query and write methods

### `execute(sql, params=None)`

Async equivalent of `Database.execute()`.

Use it for schema changes, one-off writes, or raw SQL statements that are clearer than helper calls.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        result = await db.execute("INSERT INTO users (name) VALUES (?)", ["Ada"])
        print(result.lastrowid)

asyncio.run(main())
```

### `executemany(sql, seq_of_params)`

Async batch execution for repeated statements.

Useful for imports, queue drains, and synchronization tasks that process many records.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE logs (message TEXT)")
        await db.executemany(
            "INSERT INTO logs (message) VALUES (?)",
            [("started",), ("validated",), ("finished",)],
        )

asyncio.run(main())
```

### `script(sql_script)`

Async helper for multi-statement setup scripts.

Useful in test setup, local bootstrap code, or service startup initialization.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO users (name) VALUES ('Ada');
        """)

asyncio.run(main())
```

### `fetch_all(sql, params=None)`

Run a raw query and return all rows.

Helpful for reporting queries, joins, and custom SQL in async code paths.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, active INTEGER);
        INSERT INTO users (name, active) VALUES ('Ada', 1), ('Grace', 0);
        """)
        rows = await db.fetch_all("SELECT * FROM users WHERE active = ?", [1])
        print(rows)

asyncio.run(main())
```

### `fetch_one(sql, params=None)`

Run a raw query and return one row or `None`.

Great for lookup-style async handlers that expect at most one record.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
        INSERT INTO settings (key, value) VALUES ('theme', 'dark');
        """)
        row = await db.fetch_one("SELECT value FROM settings WHERE key = ?", ["theme"])
        print(row)

asyncio.run(main())
```

### `fetch_value(sql, params=None, default=None)`

Run a raw query and return one scalar value.

This is especially useful in async code where concise guard checks and counts reduce boilerplate.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE jobs (status TEXT);
        INSERT INTO jobs (status) VALUES ('queued'), ('queued'), ('done');
        """)
        queued = await db.fetch_value("SELECT COUNT(*) FROM jobs WHERE status = ?", ["queued"], default=0)
        print(queued)

asyncio.run(main())
```

### `select(table, **kwargs)`

Async equivalent of `Database.select()`.

Use it when you want structured table reads without building the full SQL manually.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        INSERT INTO users (name, age) VALUES ('Ada', 36), ('Grace', 37), ('Linus', 28);
        """)
        rows = await db.select("users", columns=["id", "name"], where="age >= ?", params=[30])
        print(rows)

asyncio.run(main())
```

### `insert(table, values, on_conflict='abort')`

Async single-row insert.

Useful for request handlers or workers that create one logical record at a time.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT)")
        await db.insert("users", {"email": "ada@example.com", "name": "Ada"})

asyncio.run(main())
```

### `insert_many(table, rows, on_conflict='abort', chunk_size=500)`

Async batch insert.

Helpful for ingestion pipelines and async synchronization tasks.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        await db.insert_many("users", [{"name": "Ada"}, {"name": "Grace"}], chunk_size=1)

asyncio.run(main())
```

### `update(table, values, **kwargs)`

Async row update helper.

Use it when your async business logic is changing a known set of columns.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (email TEXT PRIMARY KEY, active INTEGER);
        INSERT INTO users (email, active) VALUES ('ada@example.com', 1);
        """)
        await db.update("users", {"active": 0}, where="email = ?", params=["ada@example.com"])

asyncio.run(main())
```

### `delete(table, **kwargs)`

Async row deletion helper.

Useful for cleanup tasks, retention workers, and admin operations.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, expired INTEGER);
        INSERT INTO sessions (expired) VALUES (1), (0), (1);
        """)
        await db.delete("sessions", where="expired = ?", params=[1])

asyncio.run(main())
```

### `upsert(table, values, **kwargs)`

Async insert-or-update helper.

This is especially useful for idempotent async consumers such as webhooks, event processors, or sync jobs.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (email TEXT PRIMARY KEY, name TEXT)")
        await db.upsert(
            "users",
            {"email": "ada@example.com", "name": "Ada"},
            conflict_columns=["email"],
            update_columns=["name"],
        )

asyncio.run(main())
```

### `count(table, **kwargs)`

Async row-count helper.

Helpful in dashboards, validation steps, and tests.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE jobs (status TEXT);
        INSERT INTO jobs (status) VALUES ('queued'), ('queued'), ('done');
        """)
        print(await db.count("jobs", where="status = ?", params=["queued"]))

asyncio.run(main())
```

### `exists(table, **kwargs)`

Async boolean existence check.

Useful when the code only needs to know whether a record is present before deciding what to do next.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (email TEXT PRIMARY KEY)")
        await db.insert("users", {"email": "ada@example.com"})
        print(await db.exists("users", where="email = ?", params=["ada@example.com"]))

asyncio.run(main())
```

### `table(name)`

Create an `AsyncTable` helper bound to one table.

This is useful for async repository code that repeatedly targets the same table.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await users.insert({"name": "Ada"})
        print(await users.count())

asyncio.run(main())
```

## Transactions

### `transaction()`

Create an async transaction context manager.

Use this to group related async writes into one atomic unit.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE logs (message TEXT)")
        async with db.transaction():
            await db.insert("logs", {"message": "created"})
            await db.insert("logs", {"message": "notified"})

asyncio.run(main())
```

### `commit()`

Commit the current transaction manually.

Mostly useful when low-level async code intentionally owns transaction boundaries.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE logs (message TEXT)")
        await db.execute("BEGIN")
        await db.insert("logs", {"message": "manual commit"})
        await db.commit()

asyncio.run(main())
```

### `rollback()`

Roll back the current transaction manually.

Useful in explicit error recovery paths.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE logs (message TEXT)")
        await db.execute("BEGIN")
        await db.insert("logs", {"message": "temporary"})
        await db.rollback()

asyncio.run(main())
```

## Advanced and currently unsupported features

### `backup(target, pages=-1)`

Async wrapper around backup behavior.

The method is present for parity, but the native backend does not implement backups yet.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async("app.db") as db:
        try:
            await db.backup("backup.db")
        except NotSupportedError:
            print("Backups are not implemented yet.")

asyncio.run(main())
```

### `iterdump()`

Return the database schema dump as a list of SQL statements.

Useful for diagnostics and debugging in async tools.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        print(await db.iterdump())

asyncio.run(main())
```

### `create_function(name, narg, func, deterministic=False)`

Async wrapper for custom SQL function registration.

The method is currently not implemented by the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async(":memory:") as db:
        try:
            await db.create_function("slugify", 1, lambda value: value.lower())
        except NotSupportedError:
            print("Custom SQL functions are not available yet.")

asyncio.run(main())
```

### `create_aggregate(name, n_arg, aggregate_class)`

Async wrapper for custom SQL aggregate registration.

The method is currently not implemented by the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async(":memory:") as db:
        try:
            await db.create_aggregate("median", 1, object)
        except NotSupportedError:
            print("Custom aggregates are not available yet.")

asyncio.run(main())
```

### `create_collation(name, callable_)`

Async wrapper for custom collation registration.

The method is currently not implemented by the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async(":memory:") as db:
        try:
            await db.create_collation("reverse", lambda a, b: (a > b) - (a < b))
        except NotSupportedError:
            print("Custom collations are not available yet.")

asyncio.run(main())
```
