# AsyncDatabase

`AsyncDatabase` mirrors `Database` and exposes awaited versions of the same methods. It uses `asyncio` and serializes connection access so one SQLite connection is not driven concurrently by multiple tasks.

Key points:

- All core methods from `Database` are available asynchronously
- `async with db.transaction():` is supported
- `open_async()` and `connect_async()` return this type
