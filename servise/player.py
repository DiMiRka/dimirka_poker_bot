from db_hadler.database import db
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
        players = await repo.get_all_login()
        print(players)
        return players
