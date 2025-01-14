from decouple import config
from create_bot import db_manager
import asyncpg


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
        tele_id = player_data.get('tele_id')
        login = player_data.get('login')
        async with pool.acquire() as conn:
            await conn.fetch('INSERT INTO players (tele_id, login) VALUES ($1, $2)', tele_id, login)

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
    async def get_users(cls):
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


# async def get_player_data(user_id: int, table_name='players'):
#     async with pg_manager:
#         user_info = await pg_manager.select_data(table_name=table_name, where_dict={'tele_id': user_id}, one_dict=True)
#         if user_info:
#             return user_info
#         else:
#             return None
#
#
# async def insert_player(player_data: dict, table_name='players'):
#     async with db_manager:
#         await db_manager.insert_data_with_update(table_name=table_name, records_data=player_data, conflict_column='tele_id', update_on_conflict=False)
