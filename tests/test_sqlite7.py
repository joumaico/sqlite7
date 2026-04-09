from __future__ import annotations

from sqlite7 import IntegrityError, ValidationError, open_async, open_db


def test_sync_roundtrip_and_duplicate_ignore() -> None:
    with open_db(":memory:") as db:
        db.script(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            );
            """
        )
        result = db.insert_many(
            "users",
            [
                {"id": 1, "email": "a@example.com", "name": "A", "age": 20},
                {"id": 1, "email": "a-duplicate@example.com", "name": "AA", "age": 21},
                {"id": 2, "email": "b@example.com", "name": "B", "age": 22},
            ],
            on_conflict="ignore",
        )
        assert result.rowcount == 2
        rows = db.select("users", order_by="id ASC")
        assert [row["id"] for row in rows] == [1, 2]


def test_sync_upsert() -> None:
    with open_db(":memory:") as db:
        db.script(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            );
            """
        )
        db.insert("users", {"email": "a@example.com", "name": "A", "age": 20})
        db.upsert(
            "users",
            {"email": "a@example.com", "name": "Ada", "age": 36},
            conflict_columns=["email"],
        )
        row = db.fetch_one("SELECT name, age FROM users WHERE email = ?", ["a@example.com"])
        assert row == {"name": "Ada", "age": 36}


def test_invalid_rows_raise_validation_error() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);")
        try:
            db.insert_many("users", [{1, "John", 18}])
        except ValidationError as exc:
            assert "mapping" in str(exc)
        else:
            raise AssertionError("ValidationError was not raised")


def test_integrity_error_mapping() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE);")
        db.insert("users", {"email": "a@example.com"})
        try:
            db.insert("users", {"email": "a@example.com"})
        except IntegrityError:
            pass
        else:
            raise AssertionError("IntegrityError was not raised")


def test_open_async_returns_real_async_database() -> None:
    import asyncio

    async def scenario() -> None:
        db = open_async(":memory:")
        try:
            await db.script(
                """
                CREATE TABLE events (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
                """
            )
            await db.insert_many(
                "events",
                [
                    {"id": 1, "name": "Launch"},
                    {"id": 1, "name": "Duplicate Launch"},
                    {"id": 2, "name": "Review"},
                ],
                on_conflict="ignore",
            )
            rows = await db.select("events", order_by="id ASC")
            assert [row["name"] for row in rows] == ["Launch", "Review"]
        finally:
            await db.close()

    asyncio.run(scenario())


def test_named_parameters_are_rejected() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE);")
        try:
            db.execute("INSERT INTO users (email) VALUES (?)", {"email": "a@example.com"})
        except ValidationError as exc:
            assert "Named SQL parameters" in str(exc)
        else:
            raise AssertionError("ValidationError was not raised")


def test_named_parameters_are_rejected_in_executemany() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE);")
        try:
            db.executemany("INSERT INTO users (email) VALUES (?)", [{"email": "a@example.com"}])
        except ValidationError as exc:
            assert "Named SQL parameters" in str(exc)
        else:
            raise AssertionError("ValidationError was not raised")


def test_table_mirrors_database_query_arguments() -> None:
    with open_db(":memory:") as db:
        db.script(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            );
            """
        )
        users = db.table("users")
        users.insert_many(
            [
                {"id": 1, "name": "A", "age": 20},
                {"id": 2, "name": "B", "age": 21},
                {"id": 3, "name": "C", "age": 22},
            ]
        )
        row = users.get("age >= ?", [20], order_by="id ASC", offset=1)
        assert row == {"id": 2, "name": "B", "age": 21}
        rows = users.select(columns=["id", "name"], order_by="id DESC", limit=2, offset=0)
        assert rows == [{"id": 3, "name": "C"}, {"id": 2, "name": "B"}]
        assert users.count(where="age >= ?", params=[21]) == 2
        assert users.exists(where="name = ?", params=["A"]) is True
