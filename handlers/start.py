from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from keyboards.start import main_kb, admin_main_kb
from utils.statistic_utils import get_last_games, get_last_game
from create_bot import bot

start_router = Router()


class Game(StatesGroup):
    last_games = State()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Вызов стартовой клавиатуры"""
    await message.answer('Салам браток 🤙',
                         reply_markup=await main_kb(message.from_user.id))


@start_router.callback_query(F.data == 'админ панель')
async def admin_board(call: CallbackQuery):
    await call.message.answer('Что делаем?', reply_markup=await admin_main_kb())


@start_router.callback_query(F.data == "прошлая игра", )
async def last_game_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboards, games = await get_last_games()
    await state.set_data({"games": games})
    await call.message.answer('Какую игру хочешь чекнуть?', reply_markup=keyboards)
    await state.set_state(Game.last_games.state)


@start_router.message(Command('past_games'))
async def last_game_start(message: Message, state: FSMContext):
    await state.clear()
    keyboards, games = await get_last_games()
    await state.set_data({"games": games})
    await message.answer('Какую игру хочешь чекнуть?', reply_markup=keyboards)
    await state.set_state(Game.last_games.state)


@start_router.callback_query(lambda call: call.data.startswith('результаты'))
async def last_game_end(call: CallbackQuery, state: FSMContext):
    games = await state.get_data()
    game = next((game for game in games["games"] if game["date"] == call.data[11:]))
    text = await get_last_game(game)
    photo = FSInputFile('utils/last_game_image.png')
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo,
                         reply_markup=await main_kb(call.from_user.id), caption=text, show_caption_above_media=True)


