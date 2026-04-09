# `AsyncTable`

`AsyncTable` is the table-bound async companion to `AsyncDatabase`.

Use it when an async function, repository, or service mostly interacts with one table and you want that code to stay concise and domain-focused.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        users = db.table("users")
        await users.insert({"name": "Ada"})

asyncio.run(main())
```

## Lifecycle and connection-level methods

### `close()`

Close the shared async connection.

Useful when a caller only has an `AsyncTable` reference but still needs to release the underlying database resources.

```python
import asyncio
from sqlite7 import open_async

async def main():
    db = open_async(":memory:")
    users = db.table("users")
    await users.close()

asyncio.run(main())
```

### `script(sql_script)`

Run a multi-statement setup script through the shared async database.

Helpful in async tests or service bootstrap code.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        users = db.table("users")
        await users.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO users (name) VALUES ('Ada');
        """)

asyncio.run(main())
```

### `commit()`

Commit the current transaction manually.

Use it only when your async code intentionally manages transactions itself.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await db.execute("BEGIN")
        await users.insert({"name": "Ada"})
        await users.commit()

asyncio.run(main())
```

### `rollback()`

Roll back the current transaction manually.

Helpful in explicit async recovery flows.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await db.execute("BEGIN")
        await users.insert({"name": "Ada"})
        await users.rollback()

asyncio.run(main())
```

### `backup(target, pages=-1)`

Pass-through to async backup support.

The method exists for parity, but backups are not implemented yet in the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async("app.db") as db:
        users = db.table("users")
        try:
            await users.backup("backup.db")
        except NotSupportedError:
            print("Backups are not implemented yet.")

asyncio.run(main())
```

### `iterdump()`

Return the schema dump as a list of SQL statements.

Useful for diagnostics in async tooling.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        users = db.table("users")
        print(await users.iterdump())

asyncio.run(main())
```

### `create_function(name, narg, func, deterministic=False)`

Pass-through to async custom function registration.

The method is not implemented yet in the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async(":memory:") as db:
        users = db.table("users")
        try:
            await users.create_function("slugify", 1, lambda value: value.lower())
        except NotSupportedError:
            print("Custom SQL functions are not available yet.")

asyncio.run(main())
```

### `create_aggregate(name, n_arg, aggregate_class)`

Pass-through to async custom aggregate registration.

The method is not implemented yet in the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async(":memory:") as db:
        users = db.table("users")
        try:
            await users.create_aggregate("median", 1, object)
        except NotSupportedError:
            print("Custom aggregates are not available yet.")

asyncio.run(main())
```

### `create_collation(name, callable_)`

Pass-through to async custom collation registration.

The method is not implemented yet in the native backend.

```python
import asyncio
from sqlite7 import NotSupportedError, open_async

async def main():
    async with open_async(":memory:") as db:
        users = db.table("users")
        try:
            await users.create_collation("reverse", lambda a, b: (a > b) - (a < b))
        except NotSupportedError:
            print("Custom collations are not available yet.")

asyncio.run(main())
```

## Raw SQL methods

### `execute(sql, params=None)`

Run one SQL statement through the shared async database.

Useful when the table abstraction is convenient overall but one operation needs custom SQL.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        users = db.table("users")
        await users.execute("INSERT INTO users (name) VALUES (?)", ["Ada"])

asyncio.run(main())
```

### `executemany(sql, seq_of_params)`

Run the same SQL statement for many parameter sets.

Helpful in async import or synchronization workflows that still prefer raw SQL.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await users.executemany("INSERT INTO users (name) VALUES (?)", [("Ada",), ("Grace",)])

asyncio.run(main())
```

### `fetch_all(sql, params=None)`

Run a raw query and return all rows.

Useful for custom reads where SQL is clearer than abstractions.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, active INTEGER);
        INSERT INTO users (name, active) VALUES ('Ada', 1), ('Grace', 0);
        """)
        users = db.table("users")
        print(await users.fetch_all("SELECT * FROM users WHERE active = ?", [1]))

asyncio.run(main())
```

### `fetch_one(sql, params=None)`

Run a raw query and return one row or `None`.

Helpful for single-record async lookups.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (email TEXT PRIMARY KEY, name TEXT);
        INSERT INTO users (email, name) VALUES ('ada@example.com', 'Ada');
        """)
        users = db.table("users")
        print(await users.fetch_one("SELECT * FROM users WHERE email = ?", ["ada@example.com"]))

asyncio.run(main())
```

### `fetch_value(sql, params=None, default=None)`

Run a raw query and return one scalar value.

Useful for compact async checks and aggregate reads.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (active INTEGER);
        INSERT INTO users (active) VALUES (1), (1), (0);
        """)
        users = db.table("users")
        print(await users.fetch_value("SELECT COUNT(*) FROM users WHERE active = ?", [1], default=0))

asyncio.run(main())
```

## Table-focused helpers

### `all(**kwargs)`

Alias for `select()`.

Useful when a team prefers a more conversational method name.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO users (name) VALUES ('Ada'), ('Grace');
        """)
        users = db.table("users")
        print(await users.all(order_by="id ASC"))

asyncio.run(main())
```

### `select(**kwargs)`

Fetch rows from the bound table without repeating its name.

This keeps async repository code compact and readable.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        INSERT INTO users (name, age) VALUES ('Ada', 36), ('Grace', 37), ('Linus', 28);
        """)
        users = db.table("users")
        rows = await users.select(columns=["id", "name"], where="age >= ?", params=[30])
        print(rows)

asyncio.run(main())
```

### `get(where, params=None, **kwargs)`

Return one row from the bound table.

Useful when an async service expects a single logical record.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (email TEXT PRIMARY KEY, name TEXT);
        INSERT INTO users (email, name) VALUES ('ada@example.com', 'Ada');
        """)
        users = db.table("users")
        print(await users.get("email = ?", ["ada@example.com"]))

asyncio.run(main())
```

### `insert(values, on_conflict='abort')`

Insert one row into the bound table.

Helpful for async service code that creates one record at a time.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await users.insert({"name": "Ada"})

asyncio.run(main())
```

### `insert_many(rows, on_conflict='abort', chunk_size=500)`

Insert many rows into the bound table.

Useful for async ingestion and synchronization paths.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await users.insert_many([{"name": "Ada"}, {"name": "Grace"}], chunk_size=1)

asyncio.run(main())
```

### `update(values, where, params=None, order_by=None, limit=None)`

Update rows in the bound table.

Useful when async business logic changes a known set of columns for matching records.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (email TEXT PRIMARY KEY, active INTEGER);
        INSERT INTO users (email, active) VALUES ('ada@example.com', 1);
        """)
        users = db.table("users")
        await users.update({"active": 0}, where="email = ?", params=["ada@example.com"])

asyncio.run(main())
```

### `delete(where, params=None, order_by=None, limit=None)`

Delete rows from the bound table.

Helpful for cleanup jobs and retention rules in async apps.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (active INTEGER);
        INSERT INTO users (active) VALUES (1), (0), (0);
        """)
        users = db.table("users")
        await users.delete(where="active = ?", params=[0])

asyncio.run(main())
```

### `upsert(values, conflict_columns, update_columns=None)`

Insert or update a row in the bound table.

Great for idempotent async write paths such as sync workers and webhook processing.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (email TEXT PRIMARY KEY, name TEXT)")
        users = db.table("users")
        await users.upsert(
            {"email": "ada@example.com", "name": "Ada"},
            conflict_columns=["email"],
            update_columns=["name"],
        )

asyncio.run(main())
```

### `count(where=None, params=None)`

Count rows in the bound table.

Useful for async validations, metrics, and test assertions.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE users (active INTEGER);
        INSERT INTO users (active) VALUES (1), (1), (0);
        """)
        users = db.table("users")
        print(await users.count(where="active = ?", params=[1]))

asyncio.run(main())
```

### `exists(where=None, params=None)`

Return whether any row matches the condition.

Useful for async guard clauses that only need a boolean answer.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (email TEXT PRIMARY KEY)")
        users = db.table("users")
        await users.insert({"email": "ada@example.com"})
        print(await users.exists(where="email = ?", params=["ada@example.com"]))

asyncio.run(main())
```

### `transaction()`

Create an async transaction context manager for the shared database.

Use it when several operations on the table must succeed or fail together.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        async with users.transaction():
            await users.insert({"name": "Ada"})
            await users.insert({"name": "Grace"})

asyncio.run(main())
```

## State and metadata

### `total_changes`

Return the number of changed rows on the shared connection.

Helpful for instrumentation and tests.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        await users.insert({"name": "Ada"})
        await users.insert({"name": "Grace"})
        print(users.total_changes)

asyncio.run(main())
```

### `in_transaction`

Return whether the shared connection is inside a transaction.

Useful when debugging async transactional behavior.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("CREATE TABLE users (name TEXT)")
        users = db.table("users")
        print(users.in_transaction)
        await db.execute("BEGIN")
        print(users.in_transaction)

asyncio.run(main())
```
