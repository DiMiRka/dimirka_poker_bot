import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender

from create_bot import bot
from db_hadler.db_class import Database

player_router = Router()


class Player(StatesGroup):
    login = State()
    players = State()


@player_router.callback_query(F.data == 'новый игрок')
async def start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=call.from_user.id):
        await asyncio.sleep(2)
        await call.message.answer('Как тебя величать, дружок?', reply_markup=None)
    await state.set_state(Player.login.state)


@player_router.message(Player.login)
async def start(message: Message, state: FSMContext):
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        await asyncio.sleep(2)
        player_info = {'login': message.text}
        await Database.insert_player(player_data=player_info)
        await message.answer(f'Готовь свои бабки 💲 {message.text}', reply_markup=None)


@player_router.callback_query(F.data == 'cтатистика игроков')
async def tables(call: CallbackQuery, state: FSMContext):
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(2)
        await Database.get_users_bd()
        await call.message.answer('В разработке ⚙', reply_markup=None)
