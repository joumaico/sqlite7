# Public API Overview

### Top-level exports

- `open_db`, `connect`
- `open_async`, `connect_async` (real asyncio entry points)
- `Database`, `Table`
- `AsyncDatabase`, `AsyncTable` (real asyncio APIs)
- `StatementResult`, `RowDict`
- SQLite compatibility exports: `Binary`, `Row`, `PARSE_DECLTYPES`, `PARSE_COLNAMES`, `register_adapter`, `register_converter`, `complete_statement`
- Package exceptions from `SQLite7Error` down to SQLite-like subclasses
