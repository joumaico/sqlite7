# SQLite7

SQLite7 is a DB-API 2.0 style interface for SQLite databases backed directly by the SQLite C library, with both synchronous and asynchronous APIs.

This documentation is organized into four main sections:

- **Tutorial** teaches the core workflow for opening a database, creating tables, inserting data, and querying rows.
- **Reference** describes the classes, functions, constants, and exceptions provided by `sqlite7`.
- **How-to guides** show how to perform focused tasks such as binding placeholders, working with row factories, and using transactions.
- **Explanation** provides background on the native backend design and transaction behavior.

```{toctree}
:maxdepth: 2
:caption: Tutorial

tutorial
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/module
api/top-level
api/sync-database
api/sync-table
api/results
reference/exceptions
reference/sqlite-exports
reference/conflict-policies
```

```{toctree}
:maxdepth: 2
:caption: How-to guides

howto/placeholders
howto/row-factories
howto/transactions
```

```{toctree}
:maxdepth: 2
:caption: Explanation

explanation/transaction-control
concepts/how-it-works
features
best-practices
installation
license
```
