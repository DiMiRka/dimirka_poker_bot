import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_hadler.db_class import Database
from create_bot import bot
from keyboards.inline_kbs import start_game, make_count
from utils.my_utils import player_input, get_players, get_players_text

game_router = Router()


class Game(StatesGroup):
    start = State()
    players = State()
    new_game = State()


@game_router.callback_query(F.data == 'начать игру')
async def start(call: CallbackQuery, state: FSMContext):
    player_input('новая игра')
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=call.from_user.id):
        await asyncio.sleep(1)
        await call.message.answer('1 фишка равняется:', reply_markup=make_count())
    await state.set_state(Game.start.state)


@game_router.message(Command('start_game'))
async def start(message: Message, state: FSMContext):
    player_input('новая игра')
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.answer('1 фишка равняется:', reply_markup=make_count())
    await state.set_state(Game.start.state)


@game_router.callback_query(Game.start)
async def players(call: CallbackQuery, state: FSMContext):
    await state.update_data(count=int(call.message.text[0]))
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        game_players = await Database.get_users()
        kb_list = []
        for player in game_players:
            if player not in get_players():
                kb_list.append([InlineKeyboardButton(text=player, callback_data=player)])
        kb_list.append([InlineKeyboardButton(text='Стартуем 👌🏼', callback_data='стартуем')])
        keyboards = InlineKeyboardMarkup(
            inline_keyboard=kb_list,
            resize_keyboard=True,
            input_field_placeholder='добавляй рыбок:'
        )
        await call.message.answer('Кто играет?', reply_markup=keyboards)
    await state.set_state(Game.players.state)


@game_router.callback_query(Game.players)
async def game(call: CallbackQuery, state: FSMContext):
    if call.data != 'стартуем':
        player_input(call.data)
        game_players = await Database.get_users()
        kb_list = []
        players_in_game = get_players()
        for player in game_players:
            if player not in players_in_game:
                kb_list.append([InlineKeyboardButton(text=str(player), callback_data=str(player))])
        kb_list.append([InlineKeyboardButton(text='Стартуем 👌🏼', callback_data='стартуем')])
        new_keyboards = InlineKeyboardMarkup(
            inline_keyboard=kb_list,
            resize_keyboard=True,
            input_field_placeholder='добавляй рыбок:'
        )
        text_players = get_players_text()
        await call.message.answer(text=f'В игре: {text_players}', reply_markup=new_keyboards)
        return
    else:
        await state.update_data(players_in_game=get_players())
        await call.message.answer('Ну полетели 🎰?', reply_markup=start_game())
        await state.set_state(Game.new_game.state)


@game_router.callback_query(Game.new_game)
async def game(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text='ahahahahah')
    print(call.data)
    data = await state.get_data()
    print(data)


