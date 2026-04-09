# Exceptions

`sqlite7` maps native SQLite result codes into package-defined exceptions and preserves SQLite metadata when available.

### Base exceptions

- `SQLite7Error`
- `Warning`
- `Error`

### SQLite-like subclasses

- `InterfaceError`
- `DatabaseError`
- `DataError`
- `OperationalError`
- `IntegrityError`
- `InternalError`
- `ProgrammingError`
- `NotSupportedError`

### sqlite7-specific subclasses

- `ConfigurationError`
- `ValidationError`
- `InvalidIdentifierError`
- `ConnectionClosedError`

### Example

```python
from sqlite7 import IntegrityError, ValidationError, open_db

with open_db(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE)")
    db.insert("users", ["ada@example.com"])

    try:
        db.insert("users", ["ada@example.com"])
    except IntegrityError as exc:
        print(type(exc).__name__)
        print(exc.sqlite_errorcode)
        print(exc.sqlite_errorname)

    try:
        db.insert_many("users", [{1, "bad payload"}])
    except ValidationError as exc:
        print(type(exc).__name__)
        print(str(exc))
```

---
