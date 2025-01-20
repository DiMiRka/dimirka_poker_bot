import json
import asyncpg

from decouple import config


class Database:
    _pool = None
    _dsn = config('PG_LINK')

    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def close(self):
        await self.pool.close()

    @classmethod
    async def insert_player(cls, player_data: dict):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        login = player_data.get('login')
        async with pool.acquire() as conn:
            await conn.fetch('INSERT INTO players (login) VALUES ($1)', login)

    @classmethod
    async def get_tables(cls):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            print(type(tables))
            for tb in tables:
                print(tb)

    @classmethod
    async def get_users_bd(cls):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            user = await conn.fetch("SELECT * FROM players;")
            players = []
            for login in user:
                players.append(login[1])
            return players

    @classmethod
    async def new_table(cls):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            await conn.fetch("CREATE TABLE products (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL);")

    @classmethod
    async def insert_new_game(cls, count: int):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            await conn.fetch("INSERT INTO games (count) VALUES ($1)", count)

    @classmethod
    async def get_date(cls):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            date = await conn.fetchrow("SELECT date FROM GAMES ORDER BY id DESC LIMIT 1;")
            date = date['date'].strftime('%d.%m.%Y')
            return date

    @classmethod
    async def get_game_id(cls):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            game_id = await conn.fetchrow("SELECT id FROM GAMES ORDER BY id DESC LIMIT 1;")
            game_id = game_id['id']
            return game_id

    @classmethod
    async def update_game(cls, game: dict, game_id: int):
        if cls._pool is None:
            try:
                pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with pool.acquire() as conn:
            game = json.dumps(game, ensure_ascii=False)
            await conn.fetch("UPDATE games SET game = $1 WHERE id = $2", game, game_id)
