# How to use transactions

Use `Database.transaction()` to group write operations safely. Nested transactions use SQLite savepoints.

```python
from sqlite7 import connect

db = connect(":memory:")
with db.transaction():
    db.execute("CREATE TABLE item(id INTEGER PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO item(name) VALUES(?)", ("one",))
```

Call `commit()` for explicit transaction boundaries, or `rollback()` to undo pending changes.
