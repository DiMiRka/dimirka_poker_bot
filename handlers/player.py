import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender

from create_bot import bot
from db_hadler.db_class import Database
from db_hadler.database import db
from repositories import PlayerRepository

player_router = Router()


class Player(StatesGroup):
    login = State()
    players = State()


@player_router.callback_query(F.data == 'новый игрок')
async def new_player(call: CallbackQuery, state: FSMContext):
    """Добавление в таблицу player базы данных нового игрока
    Запрос логина"""
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=call.from_user.id):
        await asyncio.sleep(1)
        await call.message.answer('Как тебя величать, дружок?', reply_markup=None)
    await state.set_state(Player.login.state)


@player_router.message(Command('new_player'))
async def new_player(message: Message, state: FSMContext):
    """Добавление в таблицу player базы данных нового игрока
    Запрос логина"""
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        await asyncio.sleep(1)
        await message.answer('Как тебя величать, дружок?', reply_markup=None)
    await state.set_state(Player.login.state)


@player_router.message(Player.login)
async def new_player_end(message: Message, state: FSMContext):
    """Добавление в таблицу player базы данных нового игрока
        Внесение логина в базу данных"""
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        await asyncio.sleep(2)



        async with db.session() as session:
            repo = PlayerRepository(session)
            player = await repo.get_by_login(message.text)

            if player:
                await message.answer("Вы уже зарегистрированы!")
                return

            player = await repo.create(message.text)
            await message.answer(f'Готовь свои бабки 💲 {player.login}', reply_markup=None)
