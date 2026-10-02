from decouple import config
from sqlalchemy.engine import URL


def get_database_url() -> str:
    host = config('PG_HOST', default='')
    if not host:
        return config('PG_LINK')
    return URL.create(
        'postgresql+asyncpg',
        username=config('POSTGRES_USER', default='poker_user'),
        password=config('POSTGRES_PASSWORD'),
        host=host,
        port=config('PG_PORT', default=5432, cast=int),
        database=config('POSTGRES_DB', default='poker_db'),
    ).render_as_string(hide_password=False)
