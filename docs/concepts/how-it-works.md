# How sqlite7 Works

`sqlite7` is not an ORM. You still write SQL when you want to. The library focuses on making raw SQLite access cleaner and safer.

There are two layers:

1. **Direct SQL methods** like `execute()`, `fetch_all()`, and `script()`
2. **Convenience helpers** like `select()`, `insert()`, `update()`, `delete()`, and `upsert()`

The helper methods validate table and column names before interpolating them into SQL, while query values are still passed as parameters.

---
