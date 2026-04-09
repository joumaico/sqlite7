# `Table`

`Table` is a table-bound helper built on top of `Database`.

Use it when a piece of code works with one table repeatedly and you want the code to read more like the domain than like plumbing. Instead of repeating the table name on every call, you bind it once and focus on the operation.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, name TEXT)")
    users = db.table("users")
    users.insert({"email": "ada@example.com", "name": "Ada"})
```

## Lifecycle and shared connection behavior

### `close()`

Close the underlying database connection.

This is useful when a table helper is the only object a caller has and it needs to release the connection cleanly.

```python
from sqlite7 import open_db

users = open_db(":memory:").table("users")
users.close()
```

### `script(sql_script)`

Run a multi-statement SQL script through the underlying database.

This is helpful in setup code where a table-focused service still needs to initialize related schema or fixture data.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    users = db.table("users")
    users.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
    INSERT INTO users (name) VALUES ('Ada');
    """)
```

### `commit()`

Commit the current transaction on the shared connection.

Use this only when the surrounding code is managing transactions manually.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (name TEXT)")
    users = db.table("users")
    db.execute("BEGIN")
    users.insert({"name": "Ada"})
    users.commit()
```

### `rollback()`

Roll back the current transaction on the shared connection.

This is useful in low-level code that needs explicit failure recovery.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (name TEXT)")
    users = db.table("users")
    db.execute("BEGIN")
    users.insert({"name": "Ada"})
    users.rollback()
```

## Advanced pass-through methods

### `backup(target, pages=-1)`

Pass-through to `Database.backup()`.

It exists for API parity, but the native backend does not implement backups yet.

```python
from sqlite7 import open_db, NotSupportedError

with open_db("app.db") as db:
    users = db.table("users")
    try:
        users.backup("backup.db")
    except NotSupportedError:
        print("Backups are not implemented yet.")
```

### `iterdump()`

Yield SQL statements describing the database schema.

This can be handy when a table-centric workflow still needs to inspect the broader database structure.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    users = db.table("users")
    print(list(users.iterdump()))
```

### `create_function(name, narg, func, deterministic=False)`

Pass-through to `Database.create_function()`.

It is present for consistency, but custom SQL functions are not implemented yet in the native backend.

```python
from sqlite7 import open_db, NotSupportedError

with open_db(":memory:") as db:
    users = db.table("users")
    try:
        users.create_function("slugify", 1, lambda value: value.lower())
    except NotSupportedError:
        print("Custom SQL functions are not available yet.")
```

### `create_aggregate(name, n_arg, aggregate_class)`

Pass-through to `Database.create_aggregate()`.

It would be useful for domain-specific aggregation once supported, but it is not implemented yet.

```python
from sqlite7 import open_db, NotSupportedError

with open_db(":memory:") as db:
    users = db.table("users")
    try:
        users.create_aggregate("median", 1, object)
    except NotSupportedError:
        print("Custom aggregates are not available yet.")
```

### `create_collation(name, callable_)`

Pass-through to `Database.create_collation()`.

It is meant for custom sorting rules, but it is not implemented yet in the current backend.

```python
from sqlite7 import open_db, NotSupportedError

with open_db(":memory:") as db:
    users = db.table("users")
    try:
        users.create_collation("reverse", lambda a, b: (a > b) - (a < b))
    except NotSupportedError:
        print("Custom collations are not available yet.")
```

## Raw SQL helpers

### `execute(sql, params=None)`

Run a single SQL statement against the shared database connection.

This is useful when the table abstraction is convenient overall, but one operation still needs raw SQL.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    users = db.table("users")
    users.execute("INSERT INTO users (name) VALUES (?)", ["Ada"])
```

### `executemany(sql, seq_of_params)`

Run one SQL statement for many parameter sets.

Use this when a table-specific import or synchronization step needs repetitive raw-SQL writes.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (name TEXT)")
    users = db.table("users")
    users.executemany("INSERT INTO users (name) VALUES (?)", [("Ada",), ("Grace",)])
```

### `fetch_all(sql, params=None)`

Run a raw query and return all rows.

This helps when you want full SQL expressiveness while still working through a table-oriented object.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, active INTEGER);
    INSERT INTO users (name, active) VALUES ('Ada', 1), ('Grace', 0);
    """)
    users = db.table("users")
    rows = users.fetch_all("SELECT * FROM users WHERE active = ?", [1])
    print(rows)
```

### `fetch_one(sql, params=None)`

Run a raw query and return one row or `None`.

This is useful for lookups where the answer should be a single record.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE);
    INSERT INTO users (email) VALUES ('ada@example.com');
    """)
    users = db.table("users")
    row = users.fetch_one("SELECT * FROM users WHERE email = ?", ["ada@example.com"])
    print(row)
```

### `fetch_value(sql, params=None, default=None)`

Run a raw query and return a single scalar value.

Use this for concise existence checks, counts, or one-column lookups.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, active INTEGER);
    INSERT INTO users (active) VALUES (1), (1), (0);
    """)
    users = db.table("users")
    active_count = users.fetch_value("SELECT COUNT(*) FROM users WHERE active = ?", [1], default=0)
    print(active_count)
```

## Table-oriented read helpers

### `all(columns=None, where=None, params=None, group_by=None, having=None, order_by=None, limit=None, offset=None, distinct=False)`

Alias for `select()`.

This is helpful when your team prefers a more conversational method name for “give me rows from this table.”

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
    INSERT INTO users (name) VALUES ('Ada'), ('Grace');
    """)
    users = db.table("users")
    print(users.all(order_by="id ASC"))
```

### `select(columns=None, where=None, params=None, group_by=None, having=None, order_by=None, limit=None, offset=None, distinct=False)`

Fetch rows from the bound table without repeating the table name.

This helps keep repository and service code focused on the query conditions rather than on repeated plumbing.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
    INSERT INTO users (name, age) VALUES ('Ada', 36), ('Grace', 37), ('Linus', 28);
    """)
    users = db.table("users")
    rows = users.select(columns=["id", "name"], where="age >= ?", params=[30], order_by="id ASC")
    print(rows)
```

### `get(where, params=None, columns=None, group_by=None, having=None, order_by=None, offset=None, distinct=False)`

Return one row from the bound table.

Use this when the code expects a single logical result, such as loading one account, one setting, or one job record.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT);
    INSERT INTO users (email, name) VALUES ('ada@example.com', 'Ada');
    """)
    users = db.table("users")
    user = users.get("email = ?", ["ada@example.com"])
    print(user)
```

## Table-oriented write helpers

### `insert(values, on_conflict='abort')`

Insert one row into the bound table.

This is especially helpful in service code because the method reads like a domain action rather than a SQL statement.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    users = db.table("users")
    users.insert({"name": "Ada"})
```

### `insert_many(rows, on_conflict='abort', chunk_size=500)`

Insert multiple rows into the bound table.

Use this for seed data, imports, or synchronization jobs that all target one table.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    users = db.table("users")
    users.insert_many([{"name": "Ada"}, {"name": "Grace"}, {"name": "Linus"}])
```

### `update(values, where, params=None, order_by=None, limit=None)`

Update rows in the bound table.

This helps teams centralize update logic around one table without repeatedly passing the table name around.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, active INTEGER);
    INSERT INTO users (email, active) VALUES ('ada@example.com', 1);
    """)
    users = db.table("users")
    users.update({"active": 0}, where="email = ?", params=["ada@example.com"])
```

### `delete(where, params=None, order_by=None, limit=None)`

Delete rows from the bound table.

This is useful for retention policies, account cleanup, or admin-only removal flows.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, active INTEGER);
    INSERT INTO users (active) VALUES (1), (0), (0);
    """)
    users = db.table("users")
    users.delete(where="active = ?", params=[0])
```

### `upsert(values, conflict_columns, update_columns=None)`

Insert or update a row in the bound table.

This is excellent for idempotent write paths, especially when a service owns synchronization logic for a single table.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (email TEXT PRIMARY KEY, name TEXT)")
    users = db.table("users")
    users.upsert(
        {"email": "ada@example.com", "name": "Ada"},
        conflict_columns=["email"],
        update_columns=["name"],
    )
```

### `count(where=None, params=None)`

Count rows in the bound table.

This keeps metrics, validations, and tests expressive and compact.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, active INTEGER);
    INSERT INTO users (active) VALUES (1), (1), (0);
    """)
    users = db.table("users")
    print(users.count(where="active = ?", params=[1]))
```

### `exists(where=None, params=None)`

Return whether any row matches the condition in the bound table.

Use this when code needs a simple boolean answer before taking the next step.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (email TEXT PRIMARY KEY)")
    users = db.table("users")
    users.insert({"email": "ada@example.com"})
    print(users.exists(where="email = ?", params=["ada@example.com"]))
```

### `transaction()`

Create a transaction context manager for the underlying database.

This is useful when a table-focused workflow needs multiple changes to succeed or fail together.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (name TEXT)")
    users = db.table("users")

    with users.transaction():
        users.insert({"name": "Ada"})
        users.insert({"name": "Grace"})
```

## State and metadata

### `total_changes`

Return the number of changed rows on the shared connection.

This is useful for simple instrumentation and test assertions.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (name TEXT)")
    users = db.table("users")
    users.insert({"name": "Ada"})
    users.insert({"name": "Grace"})
    print(users.total_changes)
```

### `in_transaction`

Return whether the shared connection is currently inside a transaction.

This is helpful for debugging and low-level control flow.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (name TEXT)")
    users = db.table("users")
    print(users.in_transaction)
    db.execute("BEGIN")
    print(users.in_transaction)
```
