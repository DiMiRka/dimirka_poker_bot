import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import BaseMiddleware
from aiogram.types import Message

from decouple import config
from asyncpg_lite import DatabaseManager
from typing import Callable, Dict, Awaitable, Any


class MessageLogMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        logging.info(event.text)  # Выводим текст сообщения
        return await handler(event, data)  # Возвращаем обновление хендлерам


'''Создание бота'''
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=config('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.message.outer_middleware(MessageLogMiddleware())
db_manager = DatabaseManager(db_url=config('PG_LINK'), deletion_password=config('ROOT_PASS'))
