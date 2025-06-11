import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp
from handlers.start import start_router
from handlers.game import game_router
from handlers.player import player_router
from handlers.player_statistics import statistics_router


async def set_commands():
    """Настройка меню бота"""
    commands = [BotCommand(command='start', description='Запустить бота'),
                BotCommand(command='start_game', description='Начать новую игру'),
                BotCommand(command='new_player', description='Добавить игрока'),
                BotCommand(command='statics', description='Статистика игроков'),
                BotCommand(command='past_games', description='Прошлые игры')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def on_startup():
    """Действия при запуске бота"""
    await set_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    print('Бот запущен')


async def on_shutdown(_):
    """Действия при остановке бота"""
    print('Бот остановлен')


async def main():
    """Запуск бота"""
    dp.include_routers(start_router, game_router, player_router, statistics_router)
    dp.startup.register(on_startup)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
