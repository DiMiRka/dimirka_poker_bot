from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from decouple import config
from contextlib import asynccontextmanager


class Database:
    def __init__(self):
        self.engine = create_async_engine(config('PG_LINK'), echo=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False
        )

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


db = Database()
