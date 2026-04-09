# How to use placeholders to bind values in SQL queries

`sqlite7` supports `?` placeholders only. Named placeholders such as `:name` are intentionally not supported.

```python
from sqlite7 import connect

db = connect(":memory:")
db.execute("CREATE TABLE user(id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
db.execute(
    "INSERT INTO user(name, email) VALUES(?, ?)",
    ("Ada", "ada@example.com"),
)
```

For repeated inserts, use `executemany()` with a sequence of tuples:

```python
db.executemany(
    "INSERT INTO user(name, email) VALUES(?, ?)",
    [("Ada", "ada@example.com"), ("Grace", "grace@example.com")],
)
```
