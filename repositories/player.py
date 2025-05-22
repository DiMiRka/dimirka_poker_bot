from sqlalchemy import select
from models.game import Player
from repositories.base import BaseRepository


class PlayerRepository(BaseRepository):
    """Репозиторий для работы с таблицей игроков"""
    async def get_by_login(self, login: str) -> Player:
        result = await self.session.execute(
            select(Player).where(Player.login == login)
        )
        return result.scalar_one_or_none()

    async def create(self, login: str) -> Player:
        player = Player(login=login)
        self.session.add(player)
        await self.session.flush()
        return player

    async def get_all_login(self):
        result = await self.session.execute(
            select(Player)
        )
        return result.scalars().all()

