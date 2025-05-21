from typing import Union, Callable, Annotated
from sqlalchemy.ext.asyncio import (async_sessionmaker, create_async_engine,
                                    AsyncSession, AsyncEngine, AsyncConnection)

from decouple import config


class InternalError(Exception):
    pass


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except InternalError:
            await session.rollback()


def create_sessionmaker(
        bind_engine: Union[AsyncEngine, AsyncConnection]
) -> Callable[..., async_sessionmaker]:
    return async_sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


engine = create_async_engine(config('PG_LINK'))

async_session = create_sessionmaker(engine)

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
