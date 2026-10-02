from db.database import db
from repositories import GameRepository
from repositories.active_game import ActiveGameRepository

async def create_game_db(count: int, chat_id: int | None = None, state: dict | None = None):
    async with db.session() as session:
        repo = GameRepository(session)

        game = await repo.create(count)
        if chat_id is not None:
            snapshot = dict(state, date=game.formatted_date, game_id=game.id,
                            phase='playing', start_status=True)
            await ActiveGameRepository(session).save(chat_id, snapshot)
        return game.formatted_date, game.id


async def save_active_game_db(chat_id: int, state: dict):
    async with db.session() as session:
        await ActiveGameRepository(session).save(chat_id, state)


async def load_active_games_db() -> dict[int, dict]:
    async with db.session() as session:
        return await ActiveGameRepository(session).get_all()


async def finish_game_db(chat_id: int, game: dict, game_id: int):
    async with db.session() as session:
        await GameRepository(session).update(game, game_id)
        await ActiveGameRepository(session).delete(chat_id)


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
