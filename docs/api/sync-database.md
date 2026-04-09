# `Database`

Low-level and high-level SQLite client backed by the native SQLite C library.

### Constructor

`Database(path, timeout=30.0, detect_types=0, isolation_level=None, pragmas=None, row_factory=None, uri=False, check_same_thread=False, statement_cache_size=128)`

### Query helpers

- `execute(sql, params=None)`
- `executemany(sql, seq_of_params)`
- `script(sql_script)`
- `fetch_all(sql, params=None)`
- `fetch_one(sql, params=None)`
- `fetch_value(sql, params=None, default=None)`
- `select(table, columns=None, where=None, params=None, group_by=None, having=None, order_by=None, limit=None, offset=None, distinct=False)`
- `insert(table, values, on_conflict='abort')`
- `insert_many(table, rows, on_conflict='abort', chunk_size=500)`
- `update(table, values, where, params=None, order_by=None, limit=None)`
- `delete(table, where, params=None, order_by=None, limit=None)`
- `upsert(table, values, conflict_columns, update_columns=None)`
- `count(table, where=None, params=None)`
- `exists(table, where=None, params=None)`
- `table(name)`
- `transaction()`

### Example

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, age INTEGER)")
    db.insert("users", {"email": "ada@example.com", "name": "Ada", "age": 36})
    rows = db.select(
        "users",
        columns=["id", "name"],
        where="age >= ?",
        params=[30],
        order_by="id ASC",
        limit=10,
        offset=0,
    )
    print(rows)
```
