# How to create and use row factories

By default, `sqlite7` returns mapping-style rows. You can provide a custom `row_factory` to shape result rows differently.

```python
from sqlite7 import connect

def as_tuple(columns, values):
    return tuple(values)

db = connect(":memory:", row_factory=as_tuple)
```

A row factory receives the selected columns and the raw row values.
