# Best Practices

- Use `script()` for schema setup and migrations made of multiple statements
- Use `fetch_all()` / `fetch_one()` when you need full SQL control
- Use `select()` / `insert()` / `update()` / `delete()` for common CRUD flows
- Use `table()` when you repeatedly work with the same table
- Use `transaction()` for grouped writes and nested savepoint logic
- Use `upsert()` when your schema has a clear conflict target
- Prefer parameterized SQL for values; never string-format raw values into SQL
- Only interpolate identifiers through sqlite7 helper methods, which validate them

---
