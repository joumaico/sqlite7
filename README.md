# SQLite7

SQLite7 is a DB-API 2.0 style interface for SQLite databases backed directly by the SQLite C library, with both synchronous and asynchronous APIs.

## Installation

```bash
pip install sqlite7
```

**Requires:** Python 3.11+

## Quick Example

```python
from sqlite7 import connect

with open_db(":memory:") as db:
    db.script(
        '''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        );
        '''
    )

    users = db.table("users")
    users.insert({"email": "ada@example.com", "name": "Ada", "age": 36})
    users.insert({"email": "grace@example.com", "name": "Grace", "age": 37})

    rows = users.select(
        columns=["id", "name"],
        where="age >= ?",
        params=[36],
        order_by="id ASC",
        limit=10,
        offset=0,
    )
    print(rows)
```

## License

MIT License
