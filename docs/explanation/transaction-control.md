# Transaction control

`sqlite7` follows SQLite's native transaction model closely. Write statements begin a transaction when necessary, and explicit transaction scopes are available through `Database.transaction()`.

Nested transactions are implemented with savepoints. This allows inner units of work to roll back independently while the outer transaction remains active.

Because the package is built directly on the SQLite C library, transaction behavior is intentionally predictable and close to SQLite itself across both the sync and async APIs.
