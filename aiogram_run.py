import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp
from handlers.start import start_router
from handlers.game import game_router
from handlers.player import player_router
from handlers.player_statistics import statistics_router
from db_hadler.db_class import Database
from decouple import config


async def set_commands():
    """Настройка меню бота"""
    commands = [BotCommand(command='start', description='Запустить бота'),
                BotCommand(command='start_game', description='Начать новую игру'),
                BotCommand(command='new_player', description='Добавить игрока'),
                BotCommand(command='static', description='Статистика игроков')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()


async def main():
    """Запуск бота"""
    dp.include_routers(start_router, game_router, player_router, statistics_router)
    dp.startup.register(start_bot)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    db = Database(config('PG_LINK'))
    asyncio.run(main())
