from sqlalchemy import select
from models.game import Game
from repositories.base import BaseRepository


class GameRepository(BaseRepository):
    async def get_by_login(self, login: str) -> Game:
        result = await self.session.execute(
            select(Game).where(Game.login == login)
        )
        return result.scalar_one_or_none()

    async def create(self, login: str) -> Game:
        player = Game(login=login)
        self.session.add(player)
        await self.session.flush()
        return player
