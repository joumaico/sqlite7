# Top-level helpers

### `open_db(path, **kwargs)` / `connect(path, **kwargs)`

Open a native sync `Database`.

### `open_async(path, **kwargs)` / `connect_async(path, **kwargs)`

Async entry points that return the asyncio-enabled database implementation.

```python
from sqlite7 import open_db, open_async

with open_db(":memory:") as db:
    db.execute("SELECT 1")

compat = open_async(":memory:")
compat.close()
```
