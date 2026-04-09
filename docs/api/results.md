# Result Types

## `StatementResult`

Immutable dataclass containing metadata about write statements.

**Fields**

- `rowcount`: Number of affected rows reported by SQLite
- `lastrowid`: Last inserted row id when available

**Example**

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
    result = db.insert("items", {"name": "Ada"})
    print(result.rowcount)
    print(result.lastrowid)
```

## `RowDict`

Type alias:

```python
dict[str, Any]
```

This is the default row shape returned by query helpers and fetch methods unless you supply a custom `row_factory`.

---
