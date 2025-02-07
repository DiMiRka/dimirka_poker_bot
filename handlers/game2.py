import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.handlers import CallbackQueryHandler
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_hadler.db_class import Database
from create_bot import bot
from keyboards.inline_kbs import (start_game_kb, make_count, game_keyboards, purchase_players_keyboards,
                                  purchase, exit_players_keyboards, exit_player, main_kb)
from utils.game_utils import (player_input, get_players, text_game, input_players_start,
                              text_start, input_players, update_users, get_users, update_date,
                              update_game_id, get_game_id, update_count, start_game, get_count, game_utils,
                              input_players_game, add_on_players, update_add_on_player, add_on_utils)

game_router = Router()


@game_router.callback_query(F.data == 'начать игру')
async def start(call: CallbackQuery):
    player_input('новая игра')
    async with ChatActionSender.typing(bot=bot, chat_id=call.from_user.id):
        await asyncio.sleep(2)
        await update_users()
        await call.message.answer('1 фишка равняется:', reply_markup=make_count())


@game_router.message(Command('start_game'))
async def start(message: Message):
    player_input('новая игра')
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await update_users()
        await message.answer('1 фишка равняется:', reply_markup=make_count())


@game_router.callback_query(lambda call: call.data.startswith('фишка') or call.data.startswith('игрок в старт'))
async def players_in_start(call: CallbackQuery):
    if call.data.startswith('фишка'):
        async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
            await asyncio.sleep(1)
            await update_count(int(call.data[-1]))
            await input_players_start(call)
    else:
        async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
            await asyncio.sleep(1)
            await input_players_start(call)


@game_router.callback_query(lambda call: call.data == 'стартуем')
async def game_start(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(2)
        await start_game(call)


@game_router.callback_query(lambda call: call.data == 'битва')
async def game(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(2)
        await game_utils(call)


@game_router.callback_query(lambda call: call.data == 'добавить игрока')
async def players_in_game(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        await input_players(call=call)


@game_router.callback_query(lambda call: call.data.startswith('игрок в игру'))
async def add_player_in_game(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        await input_players_game(call)


@game_router.callback_query(lambda call: call.data == 'докупить')
async def add_on_player(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        await add_on_players(call)


@game_router.callback_query(lambda call: call.data.startswith('закуп'))
async def add_on(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        await update_add_on_player(call)
        await call.message.answer(text='Сколько докупаем?', reply_markup=purchase())


@game_router.callback_query(lambda call: call.data.startswith('фишки'))
async def add_on_end(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        await add_on_utils(call)


@game_router.callback_query(lambda call: call.data == 'выход')
async def player_out(call: CallbackQuery):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)

