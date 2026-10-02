import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender


from create_bot import bot
from utils.statistic_utils import update_player_statistics

statistics_router = Router()


@statistics_router.callback_query(F.data == 'cтатистика игроков')
async def player_statistics(call: CallbackQuery):
    """Вывести статистику всех игроков по сыгранным играм"""
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(2)
        photo = await update_player_statistics()
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption='Статистика игроков 🏆',
                             show_caption_above_media=True)


@statistics_router.message(Command('static'))
async def player_statistics(message: Message):
    """Вывести статистику всех игроков по сыгранным играм"""
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        photo = await update_player_statistics()
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption='Статистика игроков 🏆',
                             show_caption_above_media=True)
