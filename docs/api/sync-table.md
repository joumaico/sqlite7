# `Table`

A convenience wrapper bound to a single validated table name.

`Table` now mirrors the database query surface anywhere a table-bound version makes sense.

### `Table.select(columns=None, where=None, params=None, group_by=None, having=None, order_by=None, limit=None, offset=None, distinct=False)`

Return rows from the bound table.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);")
    users = db.table("users")
    users.insert_many(
        [
            {"id": 1, "name": "Ada", "age": 36},
            {"id": 2, "name": "Grace", "age": 37},
            {"id": 3, "name": "Linus", "age": 38},
        ]
    )
    rows = users.select(
        columns=["id", "name"],
        where="age >= ?",
        params=[36],
        order_by="id DESC",
        limit=2,
        offset=0,
        distinct=False,
    )
    print(rows)
```

### `Table.all(...)`

Alias for `Table.select(...)` with the same arguments.

### `Table.get(where, params=None, columns=None, group_by=None, having=None, order_by=None, offset=None, distinct=False)`

Return one row from the bound table using the same selection controls, with `limit=1` applied automatically.

### `Table.insert(values, on_conflict='abort')`
### `Table.insert_many(rows, on_conflict='abort', chunk_size=500)`
### `Table.update(values, where, params=None, order_by=None, limit=None)`
### `Table.delete(where, params=None, order_by=None, limit=None)`
### `Table.upsert(values, conflict_columns, update_columns=None)`
### `Table.count(where=None, params=None)`
### `Table.exists(where=None, params=None)`
### `Table.execute(sql, params=None)`
### `Table.executemany(sql, seq_of_params)`
### `Table.fetch_all(sql, params=None)`
### `Table.fetch_one(sql, params=None)`
### `Table.fetch_value(sql, params=None, default=None)`
### `Table.transaction()`
