# Transactions

Transactions let developers group related changes into one atomic unit.

That matters because application workflows are usually larger than a single SQL statement. Creating an order may also reserve stock, write an audit entry, and enqueue follow-up work. A transaction makes sure other developers can trust that those steps either all happen or none of them do.

## Why `transaction()` helps

Using `db.transaction()` or `async with db.transaction()` is usually clearer than manually issuing `BEGIN`, `COMMIT`, and `ROLLBACK` yourself.

Benefits for teams:

- the intent is obvious when reading the code
- related writes are grouped in one place
- failure behavior is easier to reason about
- nested transactions are supported through savepoints

## Synchronous example

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER);
    CREATE TABLE audit_log (message TEXT);
    INSERT INTO accounts (id, balance) VALUES (1, 100), (2, 50);
    """)

    with db.transaction() as tx:
        tx.update("accounts", {"balance": 80}, where="id = ?", params=[1])
        tx.update("accounts", {"balance": 70}, where="id = ?", params=[2])
        tx.insert("audit_log", {"message": "moved 20 from account 1 to account 2"})
```

## Asynchronous example

```python
import asyncio
from sqlite7 import open_async

async def main():
    async with open_async(":memory:") as db:
        await db.script("""
        CREATE TABLE jobs (id INTEGER PRIMARY KEY, status TEXT);
        INSERT INTO jobs (status) VALUES ('queued');
        """)

        async with db.transaction():
            await db.update("jobs", {"status": "running"}, where="id = ?", params=[1])
            await db.insert("jobs", {"status": "queued"})

asyncio.run(main())
```

## Nested transactions

Nested `transaction()` blocks are backed by savepoints.

This helps when one library function uses transactions internally and another caller wraps that function in a larger transaction. Developers can compose database operations without having to rewrite everything around one global transaction style.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE logs (message TEXT)")

    with db.transaction() as outer:
        outer.insert("logs", {"message": "outer start"})

        with db.transaction() as inner:
            inner.insert("logs", {"message": "inner step"})

        outer.insert("logs", {"message": "outer done"})
```
