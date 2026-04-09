# Result Types

## `StatementResult`

`StatementResult` is the small metadata object returned by write-oriented methods such as `execute()`, `insert()`, `insert_many()`, `update()`, `delete()`, and `upsert()`.

It helps developers inspect what happened after a statement without parsing driver-specific objects.

### Why it is useful

- It gives a predictable place to read `rowcount`
- It exposes `lastrowid` when SQLite provides one
- It keeps write-heavy service code and tests easy to reason about

### Fields

#### `rowcount`

The number of rows SQLite reports as affected.

Useful for confirming whether an update or delete actually changed anything.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, active INTEGER)")
    db.insert_many("users", [{"active": 1}, {"active": 1}, {"active": 0}])
    result = db.update("users", {"active": 0}, where="active = ?", params=[1])
    print(result.rowcount)
```

#### `lastrowid`

The last inserted row id, when one is available.

Helpful when your application creates a record and immediately needs its generated primary key.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
    result = db.insert("items", {"name": "Ada"})
    print(result.lastrowid)
```

## `RowDict`

`RowDict` is the default row shape returned by read helpers.

It is effectively:

```python
dict[str, Any]
```

### Why it is useful

Returning dictionaries makes rows easy for developers to inspect, serialize, log, and pass between layers without additional adaptation.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    db.insert("users", {"name": "Ada"})
    row = db.fetch_one("SELECT id, name FROM users")
    print(row["name"])
```
