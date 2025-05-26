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

    async def update(self, data: dict, game_id: int):
        result = await self.session.execute(
            update(Game).where(Game.id == game_id).values(game=data)
        )
        return result

    async def get_all(self):
        result = await self.session.execute(select(Game))
        return result.scalars().all()
