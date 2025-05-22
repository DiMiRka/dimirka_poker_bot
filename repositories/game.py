import json
from sqlalchemy import select, update
from models.game import Game
from repositories.base import BaseRepository


class GameRepository(BaseRepository):

    async def create(self, count: int) -> Game:
        game = Game(count=count)
        self.session.add(game)
        await self.session.flush()
        return game

    async def update(self, game: dict, game_id: int):
        game = json.dumps(game, ensure_ascii=False)
        result = await self.session.execute(
            update(Game).where(Game.id == game_id).values(game=game)
        )
        return result
