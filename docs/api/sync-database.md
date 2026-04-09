# `Database`

`Database` is the main synchronous client in `sqlite7`.

Use it when you want one object that can:

- open and manage a SQLite connection
- run raw SQL when you need full control
- provide higher-level helpers for common CRUD work
- give your team a consistent, readable interface around SQLite

This page focuses on **when each method is useful**, **what problem it solves**, and **how another developer would typically use it in an application**.

## Constructor

### `Database(path, timeout=30.0, detect_types=0, isolation_level=None, pragmas=None, row_factory=None, uri=False, check_same_thread=False, statement_cache_size=128)`

Create a connection to a SQLite database.

This is useful when your application needs a long-lived database object that is easy to pass around to repositories, services, or command handlers.

```python
from sqlite7 import Database

# A file-backed database for a real app
with Database("app.db") as db:
    db.execute("SELECT 1")
```

Common reasons to customize constructor arguments:

- `timeout`: helpful when multiple writers may briefly contend for the database
- `pragmas`: useful when your project wants repeatable connection defaults
- `row_factory`: helpful when your team prefers custom row objects over dictionaries
- `uri=True`: useful when using SQLite URI connection strings
- `statement_cache_size`: helpful for applications that repeat many similar queries

## Connection and lifecycle

### `connection`

Expose the underlying native connection object.

Most teams should stay on the higher-level `sqlite7` API, but this property is useful when advanced tooling, debugging, or inspection needs direct access to connection-level details.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    native = db.connection
    print(native.in_transaction)
```

### `close()`

Close the database connection.

This helps developers release resources explicitly when a connection is no longer needed, especially in scripts, workers, or tests that open many databases over time.

```python
from sqlite7 import open_db

db = open_db(":memory:")
db.execute("SELECT 1")
db.close()
```

## Running SQL directly

### `execute(sql, params=None)`

Run a single SQL statement and return a `StatementResult`.

Use this when you want the full power of SQL and do not need rows back. It is especially useful for DDL, one-off updates, and statements that are clearer in raw SQL than in helper methods.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    result = db.execute("INSERT INTO users (name) VALUES (?)", ["Ada"])
    print(result.lastrowid)
```

### `executemany(sql, seq_of_params)`

Run the same statement many times with different parameter sets.

This helps developers batch repeated writes without manually building large SQL strings. It keeps ingestion code simpler and easier to review.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE logs (message TEXT)")
    db.executemany(
        "INSERT INTO logs (message) VALUES (?)",
        [("started",), ("validated",), ("finished",)],
    )
```

### `script(sql_script)`

Run a multi-statement SQL script.

Use this for schema setup, fixtures, or local test bootstrapping. It helps other developers keep related setup statements together instead of scattering them across many `execute()` calls.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        team_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY(team_id) REFERENCES teams(id)
    );
    """)
```

## Fetching data from raw SQL

### `fetch_all(sql, params=None)`

Run a query and return all rows.

This is useful when the SQL matters more than the abstraction. Developers often use it for reporting queries, joins, aggregate queries, or any case where the built-in table helpers would be too limiting.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, active INTEGER);
    INSERT INTO users (name, active) VALUES ('Ada', 1), ('Grace', 0), ('Linus', 1);
    """)

    rows = db.fetch_all(
        "SELECT id, name FROM users WHERE active = ? ORDER BY id ASC",
        [1],
    )
    print(rows)
```

### `fetch_one(sql, params=None)`

Run a query and return the first row or `None`.

Use this when your code expects at most one meaningful record, such as looking up a user by id or loading configuration for a single feature.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
    INSERT INTO settings (key, value) VALUES ('theme', 'dark');
    """)

    row = db.fetch_one("SELECT value FROM settings WHERE key = ?", ["theme"])
    print(row)
```

### `fetch_value(sql, params=None, default=None)`

Run a query and return the first column from the first row.

This helps developers avoid repetitive boilerplate for common scalar queries like counts, names, flags, totals, and timestamps.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, active INTEGER);
    INSERT INTO users (active) VALUES (1), (1), (0);
    """)

    active_count = db.fetch_value("SELECT COUNT(*) FROM users WHERE active = ?", [1], default=0)
    print(active_count)
```

## High-level query helpers

### `select(table, columns=None, where=None, params=None, group_by=None, having=None, order_by=None, limit=None, offset=None, distinct=False)`

Fetch rows from a table using structured arguments instead of hand-writing the entire query.

This is useful when your application performs common table reads and you want the intent of the query to be immediately obvious to other developers.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
    INSERT INTO users (name, age) VALUES ('Ada', 36), ('Grace', 37), ('Linus', 28);
    """)

    rows = db.select(
        "users",
        columns=["id", "name"],
        where="age >= ?",
        params=[30],
        order_by="id ASC",
        limit=10,
    )
    print(rows)
```

### `insert(table, values, on_conflict='abort')`

Insert one row into a table.

Use this when the code is adding a single logical record, such as creating a user, order, or audit event. It makes business logic easier to read than raw SQL because the input is a Python mapping.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT)")
    result = db.insert("users", {"email": "ada@example.com", "name": "Ada"})
    print(result.rowcount, result.lastrowid)
```

### `insert_many(table, rows, on_conflict='abort', chunk_size=500)`

Insert many rows in batches.

This helps when importing CSV data, processing event streams, seeding fixtures, or syncing records from an API. It keeps bulk-write code compact while still supporting chunking for larger datasets.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT)")
    db.insert_many(
        "users",
        [
            {"email": "ada@example.com", "name": "Ada"},
            {"email": "grace@example.com", "name": "Grace"},
            {"email": "linus@example.com", "name": "Linus"},
        ],
        chunk_size=2,
    )
```

### `update(table, values, where, params=None, order_by=None, limit=None)`

Update rows that match a condition.

Use this when business logic is changing a well-defined set of columns and you want the update payload to stay explicit in Python rather than being assembled into SQL strings manually.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, active INTEGER);
    INSERT INTO users (email, active) VALUES ('ada@example.com', 1), ('grace@example.com', 1);
    """)

    db.update(
        "users",
        {"active": 0},
        where="email = ?",
        params=["grace@example.com"],
    )
```

### `delete(table, where, params=None, order_by=None, limit=None)`

Delete rows that match a condition.

This is helpful for cleanup jobs, expiration logic, and admin tools. It gives developers a direct way to express removal logic while still using bound parameters.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE sessions (id INTEGER PRIMARY KEY, expired INTEGER);
    INSERT INTO sessions (expired) VALUES (1), (0), (1);
    """)

    db.delete("sessions", where="expired = ?", params=[1])
```

### `upsert(table, values, conflict_columns, update_columns=None)`

Insert a row, or update an existing row when a conflict occurs.

This is one of the most useful methods for synchronization code. It helps developers write idempotent imports, cache refreshes, and webhook consumers without first checking whether a row already exists.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (email TEXT PRIMARY KEY, name TEXT, last_seen TEXT)")

    db.upsert(
        "users",
        {"email": "ada@example.com", "name": "Ada", "last_seen": "2026-04-09"},
        conflict_columns=["email"],
        update_columns=["name", "last_seen"],
    )
```

### `count(table, where=None, params=None)`

Return the number of rows in a table, optionally filtered.

Use this when you need a simple, readable count in application code, dashboards, admin panels, or test assertions.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE jobs (id INTEGER PRIMARY KEY, status TEXT);
    INSERT INTO jobs (status) VALUES ('queued'), ('queued'), ('done');
    """)

    queued = db.count("jobs", where="status = ?", params=["queued"])
    print(queued)
```

### `exists(table, where=None, params=None)`

Return `True` if at least one row matches the condition.

This helps when code only needs a yes-or-no answer. It keeps guard clauses and validation checks very clear.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (email TEXT PRIMARY KEY)")
    db.insert("users", {"email": "ada@example.com"})

    has_ada = db.exists("users", where="email = ?", params=["ada@example.com"])
    print(has_ada)
```

### `table(name)`

Create a `Table` helper bound to one table name.

Use this when multiple operations in the same function or service all target the same table. It reduces repetition and makes the code easier for teammates to scan.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    users = db.table("users")
    users.insert({"name": "Ada"})
    print(users.count())
```

## Transactions and durability

### `transaction()`

Create a transaction context manager.

This is the preferred way to group related writes so they either all succeed or all roll back together. It helps developers protect data integrity without having to manually manage `BEGIN`, `COMMIT`, and `ROLLBACK` statements.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE audit (message TEXT)")

    with db.transaction() as tx:
        tx.insert("audit", {"message": "created"})
        tx.insert("audit", {"message": "notified"})
```

### `commit()`

Commit the current transaction manually.

This is mainly useful when your code is intentionally managing transaction boundaries itself. Most application code will be easier to maintain with `transaction()`.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE logs (message TEXT)")
    db.execute("BEGIN")
    db.insert("logs", {"message": "manual commit"})
    db.commit()
```

### `rollback()`

Roll back the current transaction manually.

Use this for explicit error recovery in low-level code, migration tooling, or framework integrations that own transaction flow.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE logs (message TEXT)")
    db.execute("BEGIN")
    db.insert("logs", {"message": "temporary"})
    db.rollback()
```

## Introspection and advanced features

### `backup(target, pages=-1)`

Intended to copy the current database into another target.

This method exists to signal an important database capability, but in the current native backend it is **not implemented yet**. That is useful for developers to know early so they can plan around it.

```python
from sqlite7 import open_db, NotSupportedError

with open_db("app.db") as db:
    try:
        db.backup("backup.db")
    except NotSupportedError:
        print("Use another backup strategy for now.")
```

### `iterdump()`

Yield SQL statements that describe the current schema.

This is useful for debugging, diagnostics, lightweight exports, and understanding what structure actually exists in a database during development or support work.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

    for statement in db.iterdump():
        print(statement)
```

### `create_function(name, narg, func, deterministic=False)`

Intended to register a custom SQL function.

This would be valuable when teams want domain-specific logic available inside SQL queries, but it is **not implemented yet** in the current backend.

```python
from sqlite7 import open_db, NotSupportedError

with open_db(":memory:") as db:
    try:
        db.create_function("slugify", 1, lambda value: value.lower().replace(" ", "-"))
    except NotSupportedError:
        print("Custom SQL functions are not available yet.")
```

### `create_aggregate(name, n_arg, aggregate_class)`

Intended to register a custom SQL aggregate.

This would help teams push reusable aggregation logic into SQLite, but it is **not implemented yet** in the current backend.

```python
from sqlite7 import open_db, NotSupportedError

with open_db(":memory:") as db:
    try:
        db.create_aggregate("median", 1, object)
    except NotSupportedError:
        print("Custom aggregates are not available yet.")
```

### `create_collation(name, callable_)`

Intended to register a custom collation for sorting and comparison.

This would be useful for locale-aware or domain-specific ordering rules, but it is **not implemented yet** in the current backend.

```python
from sqlite7 import open_db, NotSupportedError

with open_db(":memory:") as db:
    try:
        db.create_collation("reverse", lambda a, b: (a > b) - (a < b))
    except NotSupportedError:
        print("Custom collations are not available yet.")
```

## State and metadata

### `total_changes`

Return the number of rows changed by the connection over its lifetime.

This helps with instrumentation, test assertions, and quick sanity checks after a sequence of writes.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE logs (message TEXT)")
    db.insert("logs", {"message": "a"})
    db.insert("logs", {"message": "b"})
    print(db.total_changes)
```

### `in_transaction`

Return whether the connection is currently inside a transaction.

This is useful in framework code, debugging tools, or low-level utilities that need to confirm transactional state before taking action.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    print(db.in_transaction)
    db.execute("BEGIN")
    print(db.in_transaction)
```
