from db.database import db
from repositories import GameRepository

from keyboards import last_game_kb


async def create_game_db(count: int):
    async with db.session() as session:
        repo = GameRepository(session)

        game = await repo.create(count)
        return game.formatted_date, game.id


async def update_game_db(game: dict, game_id: int):
    async with db.session() as session:
        repo = GameRepository(session)
        await repo.update(game, game_id)


async def get_result_games_db():
    async with db.session() as session:
        repo = GameRepository(session)
        games = await repo.get_all()
        games_result = [dict(game.game) for game in games]
        return games_result


async def get_games_db():
    async with db.session() as session:
        repo = GameRepository(session)
        games = await repo.get_all()
        games_data = [game.to_dict for game in games]
        games_dates = [game.formatted_date for game in games]
        return games_data, games_dates
