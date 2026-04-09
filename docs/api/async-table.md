# AsyncTable

`AsyncTable` mirrors `Table` with awaited methods such as `select()`, `get()`, `insert_many()`, `update()`, `delete()`, `count()`, and `exists()`.

It delegates to its parent `AsyncDatabase` and participates in the same transaction and connection-serialization rules.
