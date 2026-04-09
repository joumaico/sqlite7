# Transactions

Use `db.transaction()` for nested transaction handling backed by savepoints.

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, message TEXT)")
    with db.transaction() as tx:
        tx.insert("logs", {"message": "outer"})
        with db.transaction() as nested:
            nested.insert("logs", {"message": "inner"})
```
