from sqlalchemy import select, update
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

    async def get_all(self):
        result = await self.session.execute(
            select(Player).order_by(Player.earned)
        )
        return result.scalars().all()

    async def update(self, data: dict,):
        for player, value in data.items():
            await self.session.execute(
                update(Player).
                where(Player.login == player).
                values(value))

