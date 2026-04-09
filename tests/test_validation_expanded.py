from __future__ import annotations

from sqlite7 import NotSupportedError, open_db


def test_nested_transactions_use_correct_savepoints() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL);")
        with db.transaction():
            db.insert("items", {"id": 1, "name": "outer"})
            with db.transaction():
                db.insert("items", {"id": 2, "name": "middle"})
                with db.transaction():
                    db.insert("items", {"id": 3, "name": "inner"})
        rows = db.select("items", order_by="id ASC")
        assert [row["id"] for row in rows] == [1, 2, 3]


def test_nested_transaction_inner_rollback_preserves_outer_work() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);")
        with db.transaction():
            db.insert("items", {"id": 1, "name": "outer"})
            try:
                with db.transaction():
                    db.insert("items", {"id": 2, "name": "dup"})
                    db.insert("items", {"id": 3, "name": "dup"})
            except Exception:
                pass
            db.insert("items", {"id": 4, "name": "after"})
        rows = db.select("items", order_by="id ASC")
        assert [row["id"] for row in rows] == [1, 4]


def test_select_offset_without_limit_is_supported() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL);")
        db.insert_many(
            "items",
            [
                {"id": 1, "name": "a"},
                {"id": 2, "name": "b"},
                {"id": 3, "name": "c"},
            ],
        )
        rows = db.select("items", columns=["id"], order_by="id ASC", offset=1)
        assert rows == [{"id": 2}, {"id": 3}]
        assert db.table("items").select(columns=["id"], order_by="id ASC", offset=2) == [{"id": 3}]


def test_update_and_delete_limit_ordering() -> None:
    with open_db(":memory:") as db:
        db.script("CREATE TABLE items (id INTEGER PRIMARY KEY, score INTEGER NOT NULL, name TEXT NOT NULL);")
        db.insert_many(
            "items",
            [
                {"id": 1, "score": 10, "name": "a"},
                {"id": 2, "score": 20, "name": "b"},
                {"id": 3, "score": 30, "name": "c"},
            ],
        )
        db.update("items", {"name": "top"}, where="score >= ?", params=[10], order_by="score DESC", limit=1)
        assert db.fetch_one("SELECT id, name FROM items WHERE name = ?", ["top"]) == {"id": 3, "name": "top"}
        db.delete("items", where="score >= ?", params=[10], order_by="score ASC", limit=1)
        assert [row["id"] for row in db.select("items", order_by="id ASC")] == [2, 3]


def test_custom_row_factory_is_used() -> None:
    def row_factory(cursor, row):
        return tuple((desc[0], row[i]) for i, desc in enumerate(cursor.description))

    with open_db(":memory:", row_factory=row_factory) as db:
        db.script("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL);")
        db.insert("items", {"id": 1, "name": "a"})
        assert db.fetch_one("SELECT id, name FROM items") == (("id", 1), ("name", "a"))


def test_unsupported_native_hooks_raise_explicitly() -> None:
    with open_db(":memory:") as db:
        for call in [
            lambda: db.backup(object()),
            lambda: db.create_function("f", 1, lambda x: x),
            lambda: db.create_aggregate("agg", 1, object),
            lambda: db.create_collation("c", lambda a, b: 0),
        ]:
            try:
                call()
            except NotSupportedError:
                pass
            else:
                raise AssertionError("NotSupportedError was not raised")
