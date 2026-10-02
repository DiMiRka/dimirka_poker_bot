from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from models.game import ActiveGame
from repositories.base import BaseRepository


class ActiveGameRepository(BaseRepository):
    async def save(self, chat_id: int, state: dict):
        query = insert(ActiveGame).values(chat_id=chat_id, state=state)
        await self.session.execute(query.on_conflict_do_update(
            index_elements=[ActiveGame.chat_id], set_={'state': query.excluded.state},
        ))

    async def get_all(self) -> dict[int, dict]:
        result = await self.session.execute(select(ActiveGame))
        return {game.chat_id: game.state for game in result.scalars().all()}

    async def delete(self, chat_id: int):
        await self.session.execute(delete(ActiveGame).where(ActiveGame.chat_id == chat_id))
