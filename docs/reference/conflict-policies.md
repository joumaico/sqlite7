# Conflict Policies

Methods that accept `on_conflict` support these SQLite-native values:

- `abort`
- `fail`
- `ignore`
- `replace`
- `rollback`

### Example

```python
from sqlite7 import open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE)")
    db.insert("users", {"id": 1, "email": "ada@example.com"})
    db.insert("users", {"id": 1, "email": "duplicate@example.com"}, on_conflict="ignore")
```

---
