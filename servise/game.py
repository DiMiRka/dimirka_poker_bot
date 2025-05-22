from db_hadler.database import db
from repositories import GameRepository


async def create_game_db(count: int):
    async with db.session() as session:
        repo = GameRepository(session)

        game = await repo.create(count)
        return game.date, game.id


async def update_game_db(game: dict, game_id: int):
    async with db.session() as session:
        repo = GameRepository(session)
        await repo.update(game, game_id)
