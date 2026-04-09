# Top-level helpers

The top-level helpers are the quickest way to start using `sqlite7` without importing the class names directly.

## `open_db(path, **kwargs)`

Open a synchronous `Database`.

This is the most ergonomic entry point for scripts, services, tests, and examples because it makes the intent obvious: open a database and start working.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("SELECT 1")
```

## `connect(path, **kwargs)`

Alias for `open_db()`.

Use this if your team prefers DB-API-style naming, or if you want code that reads similarly to Python's built-in `sqlite3.connect()`.

```python
from sqlite7 import connect

with connect(":memory:") as db:
    db.execute("SELECT 1")
```

## `open_async(path, **kwargs)`

Open an `AsyncDatabase` for asyncio-based code.

This helps developers stay in one async flow instead of mixing database calls into thread management by hand.

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.execute("SELECT 1")

asyncio.run(main())
```

## `connect_async(path, **kwargs)`

Alias for `open_async()`.

Use this when your project prefers `connect` naming symmetry between sync and async APIs.

```python
import asyncio
from sqlite7 import connect_async

async def main():
    async with connect_async(":memory:") as db:
        await db.execute("SELECT 1")

asyncio.run(main())
```
