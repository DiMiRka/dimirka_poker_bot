import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp
from services import load_active_games_db
from utils.game_state import restore_games
from handlers.start import start_router
from handlers.game import game_router
from handlers.player import player_router
from handlers.player_statistics import statistics_router


async def _set_commands():
    """Настройка меню бота"""
    commands = [BotCommand(command='start', description='Запустить бота'),
                BotCommand(command='start_game', description='Начать новую игру'),
                BotCommand(command='resume_game', description='Продолжить незавершённую игру'),
                BotCommand(command='new_player', description='Добавить игрока'),
                BotCommand(command='statics', description='Статистика игроков'),
                BotCommand(command='past_games', description='Прошлые игры')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def _on_startup():
    """Действия при запуске бота"""
    restore_games(await load_active_games_db())
    await _set_commands()
    await bot.delete_webhook(drop_pending_updates=False)
    print('Бот запущен')


async def _on_shutdown(_):
    """Действия при остановке бота"""
    print('Бот остановлен')


async def main():
    """Запуск бота"""
    dp.include_routers(start_router, game_router, player_router, statistics_router)
    dp.startup.register(_on_startup)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
