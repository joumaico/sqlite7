import asyncio
from pathlib import Path

from sqlite7 import AsyncDatabase


def test_async_database_method_parity(tmp_path: Path) -> None:
    async def scenario() -> None:
        db = AsyncDatabase(tmp_path / 'async.db')
        await db.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)')
        await db.insert('users', {'name': 'Ada', 'age': 36})
        await db.insert_many('users', [
            {'name': 'Linus', 'age': 33},
            {'name': 'Grace', 'age': 40},
        ])

        rows = await db.select('users', order_by='age DESC', limit=2, offset=0)
        assert [row['name'] for row in rows] == ['Grace', 'Ada']
        assert await db.count('users') == 3
        assert await db.exists('users', where='name = ?', params=('Ada',)) is True

        table = db.table('users')
        one = await table.get('name = ?', ('Ada',), columns=('name', 'age'))
        assert one == {'name': 'Ada', 'age': 36}

        await table.update({'age': 37}, where='name = ?', params=('Ada',))
        assert await table.fetch_value('SELECT age FROM users WHERE name = ?', ('Ada',)) == 37

        await table.delete(where='name = ?', params=('Linus',), limit=1)
        assert await table.count() == 2
        await db.close()

    asyncio.run(scenario())


def test_async_transaction_and_table_passthroughs(tmp_path: Path) -> None:
    async def scenario() -> None:
        db = AsyncDatabase(tmp_path / 'txn.db')
        await db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
        table = db.table('items')

        async with db.transaction():
            await table.insert({'name': 'first'})
            await table.insert({'name': 'second'})

        assert await db.count('items') == 2

        try:
            async with table.transaction():
                await table.insert({'name': 'third'})
                raise RuntimeError('stop')
        except RuntimeError:
            pass

        assert await table.count() == 2
        dump = await table.iterdump()
        assert any('CREATE TABLE items' in line for line in dump)
        await table.close()

    asyncio.run(scenario())
