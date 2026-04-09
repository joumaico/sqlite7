# Module reference

## Module functions

### `sqlite7.connect(path, **kwargs)`

Open a database connection and return a `Database` object.

Common keyword arguments include:

- `timeout`
- `isolation_level`
- `cached_statements`
- `uri`
- `row_factory`

### `sqlite7.connect_async(path, **kwargs)`

Return an `AsyncDatabase` instance backed by the native SQLite engine and integrated with `asyncio`.

### `sqlite7.complete_statement(statement)`

Return `True` when a SQL string appears complete according to SQLite's parser.

## Module constants

- `PARSE_DECLTYPES`
- `PARSE_COLNAMES`

## Main classes

- `Database`
- `Table`
- `AsyncDatabase`
- `AsyncTable`
- `StatementResult`
- `Row`

See the API pages for the full method surface.
