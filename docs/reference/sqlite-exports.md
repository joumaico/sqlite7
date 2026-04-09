# SQLite Compatibility Exports

These are provided by the native backend for API compatibility:

- `Binary`
- `Row`
- `PARSE_DECLTYPES`
- `PARSE_COLNAMES`
- `register_adapter` *(compatibility stub on the native backend)*
- `register_converter` *(compatibility stub on the native backend)*
- `complete_statement`

### Example

```python
import datetime as dt
from sqlite7 import register_adapter, register_converter, complete_statement

# Adapter and converter helpers are currently compatibility no-ops
print(complete_statement("SELECT 1;"))
```

---
