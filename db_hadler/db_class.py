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
        """Добавить нового игрока в базу данных (таблица players)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        login = player_data.get('login')
        async with cls._pool.acquire() as conn:
            await conn.fetch('INSERT INTO players (login) VALUES ($1)', login)

    @classmethod
    async def get_users_bd(cls):
        """Получить список всех игроков с базы данных (таблица players)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            user = await conn.fetch("SELECT * FROM players;")
            players = [login[1] for login in user]
            return players

    @classmethod
    async def insert_new_game(cls, count: int):
        """Создать новую игру в базе данных (таблица games)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            await conn.fetch("INSERT INTO games (count) VALUES ($1)", count)

    @classmethod
    async def get_date(cls):
        """Получить дату последней созданной игры (таблица games)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            date = (await conn.fetchrow("SELECT date FROM GAMES ORDER BY id DESC LIMIT 1;"))['date'].strftime('%d.%m.%Y')
            return date

    @classmethod
    async def get_game_id(cls):
        """Получить id последней созданной игры (таблица games)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            game_id = (await conn.fetchrow("SELECT id FROM GAMES ORDER BY id DESC LIMIT 1;"))['id']
            return game_id

    @classmethod
    async def update_game(cls, game: dict, game_id: int):
        """Добавить json с результатами завершенной игры в строку последней игры (таблица games)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            game = json.dumps(game, ensure_ascii=False)
            await conn.fetch("UPDATE games SET game = $1 WHERE id = $2", game, game_id)

    @classmethod
    async def get_games(cls):
        """Получить список всех json результатов игр (таблица games)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            games = await conn.fetch("SELECT game FROM games ;")
            games_list = [game[0] for game in games if game[0]]
            return games_list

    @classmethod
    async def update_player_statistics(cls, data: dict):
        """Обновить строки игроков согласно результатов всех игр (таблица players)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            for player, value in data.items():
                await conn.fetch("UPDATE players SET games = $1, win = $2, draw = $3, loss = $4, winrate = $5, earned = $6 WHERE login = $7",
                                 value.get('games'), value.get('win'), value.get('draw'), value.get('loss'), value.get('winrate'), value.get('earned'), player)

    @classmethod
    async def get_statistics(cls):
        """Получить статистику всех игроков отсортированных по общему выигрышу (таблица players)"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=cls._dsn)
                print('Data base connected OK!')
            except Exception as e:
                print(f'Unable to connect to the database: {e}')
        async with cls._pool.acquire() as conn:
            statistics_sorted = await conn.fetch("SELECT * FROM players ORDER BY earned DESC;")
            statistics_list = [player for player in statistics_sorted]
            return statistics_list
