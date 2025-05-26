from db.database import db
from repositories import PlayerRepository


async def create_player_db(login: str):
    async with db.session() as session:
        repo = PlayerRepository(session)
        player = await repo.get_by_login(login)

        if player:
            return "Вы уже зарегистрированы!"

        player = await repo.create(login)
        return f'Готовь свои бабки 💲 {player.login}'


async def get_players_db():
    async with db.session() as session:
        repo = PlayerRepository(session)
        players = await repo.get_all()
        return players


async def update_player_db(data: dict):
    async with db.session() as session:
        repo = PlayerRepository(session)
        await repo.update(data)
