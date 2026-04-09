# Tutorial

This tutorial walks through a basic `sqlite7` workflow using the synchronous API, then shows the equivalent asyncio style.

## Open a database

```python
from sqlite7 import connect

db = connect("tutorial.db")
```

The returned `Database` object manages a direct connection to SQLite through the native backend.

## Create a table

```python
db.execute("CREATE TABLE movie(title TEXT, year INTEGER, score REAL)")
```

## Insert rows

Use `?` placeholders to bind values safely:

```python
db.executemany(
    "INSERT INTO movie(title, year, score) VALUES(?, ?, ?)",
    [
        ("Monty Python and the Holy Grail", 1975, 8.2),
        ("And Now for Something Completely Different", 1971, 7.5),
        ("Monty Python's Life of Brian", 1979, 8.0),
    ],
)
db.commit()
```

## Query rows

```python
rows = db.fetch_all(
    "SELECT year, title FROM movie ORDER BY year"
)

for row in rows:
    print(row["year"], row["title"])
```

## Use table helpers

```python
movies = db.table("movie")
classic = movies.select(
    columns=["title", "year"],
    where="score >= ?",
    params=(8.0,),
    order_by="year ASC",
    limit=10,
)
```

## Work with transactions

```python
with db.transaction():
    movies.insert({"title": "Monty Python Live at the Hollywood Bowl", "year": 1982, "score": 7.9})
    movies.update(
        values={"score": 8.1},
        where="title = ?",
        params=("Monty Python's Life of Brian",),
    )
```

## Close the database

```python
db.close()
```


## Async example

```python
import asyncio
import sqlite7


async def main() -> None:
    async with sqlite7.connect_async(":memory:") as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        await db.insert("users", {"name": "Ada"})
        rows = await db.select("users", order_by="id ASC")
        print(rows)


asyncio.run(main())
```
