# Quickstart

## Open a database

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
```

## Insert rows

```python
with open_db(":memory:") as db:
    db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    db.insert("users", {"name": "Ada", "age": 36})
    db.insert_many(
        "users",
        [
            {"name": "Grace", "age": 37},
            {"name": "Linus", "age": 38},
        ],
        chunk_size=2,
    )
```

## Select rows with the table helper

```python
with open_db(":memory:") as db:
    db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    users = db.table("users")
    users.insert_many(
        [
            {"name": "Ada", "age": 36},
            {"name": "Grace", "age": 37},
            {"name": "Linus", "age": 38},
        ]
    )
    rows = users.select(
        columns=["id", "name"],
        where="age >= ?",
        params=[37],
        order_by="id DESC",
        limit=2,
        offset=0,
    )
    print(rows)
```
