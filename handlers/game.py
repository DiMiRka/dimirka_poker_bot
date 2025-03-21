from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import logging


from keyboards.inline_kbs import (make_count, purchase)
from utils.game_utils import (player_input, input_players_start, input_players, update_users, update_count,
                              start_game, game_utils, input_players_game, add_on_players, update_add_on_player,
                              add_on_utils, player_out_game, start_out_player, result_chips, game_end_start,
                              admin_board_game, update_change_on_player, change_purchase_players, change_purchase_utils,
                              game_back_player, game_back_player_end, out_extra_player, delete_extra_player)

game_router = Router()


class ChangePurchase(StatesGroup):
    change = State()


class ResultGame(StatesGroup):
    result_bank = State()


@game_router.callback_query(F.data == 'начать игру')
async def start(call: CallbackQuery):
    player_input('новая игра')
    await update_users()
    await call.message.answer('1 фишка равняется:', reply_markup=make_count())


@game_router.message(Command('start_game'))
async def start(message: Message):
    player_input('новая игра')
    await update_users()
    await message.answer('1 фишка равняется:', reply_markup=make_count())


@game_router.callback_query(lambda call: call.data.startswith('фишка') or call.data.startswith('игрок в старт'))
async def players_in_start(call: CallbackQuery):
    if call.data.startswith('фишка'):
        await update_count(int(call.data[-1]))
        await input_players_start(call)
        logging.info(f'{call.data}')
    else:
        await input_players_start(call)
        logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'стартуем')
async def game_start(call: CallbackQuery):
    await start_game(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'битва')
async def game(call: CallbackQuery):
    await game_utils(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'добавить игрока')
async def players_in_game(call: CallbackQuery):
    await input_players(call=call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data.startswith('игрок в игру'))
async def add_player_in_game(call: CallbackQuery):
    await input_players_game(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'докупить')
async def add_on_player(call: CallbackQuery):
    await add_on_players(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data.startswith('закуп'))
async def add_on(call: CallbackQuery):
    await update_add_on_player(call)
    await call.message.answer(text='Сколько докупаем?', reply_markup=purchase())
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data.startswith('фишки'))
async def add_on_end(call: CallbackQuery):
    await add_on_utils(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'выйти')
async def start_out(call: CallbackQuery):
    await start_out_player(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data.startswith('выход'))
async def player_out(call: CallbackQuery, state: FSMContext):
    await player_out_game(call)
    await state.set_state(ResultGame.result_bank)
    logging.info(f'{call.data}')


@game_router.message(ResultGame.result_bank)
async def total_chips(message: Message, state: FSMContext):
    await result_chips(message, state=state)


@game_router.callback_query(lambda call: call.data == 'закончить')
async def end_game(call: CallbackQuery, state: FSMContext):
    await game_end_start(call)
    await state.set_state(ResultGame.result_bank)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'админ панель игры')
async def admin_bord(call: CallbackQuery):
    await admin_board_game(call)


@game_router.callback_query(lambda call: call.data == 'поменять закуп')
async def admin_change_purchase(call: CallbackQuery):
    await change_purchase_players(call)


@game_router.callback_query(lambda call: call.data.startswith('поменять'))
async def add_on(call: CallbackQuery, state: FSMContext):
    await update_change_on_player(call)
    await state.clear()
    await call.message.answer(text='Итоговый закуп:', reply_markup=None)
    await state.set_state(ChangePurchase.change.state)


@game_router.message(ChangePurchase.change)
async def change_purchase(message: Message, state: FSMContext):
    await change_purchase_utils(message)
    await state.clear()


@game_router.callback_query(lambda call: call.data == 'возврат игрока')
async def player_back(call: CallbackQuery):
    await game_back_player(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data.startswith('вернуть'))
async def player_back_end(call: CallbackQuery):
    await game_back_player_end(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data == 'убрать лишнего')
async def extra_player(call: CallbackQuery):
    await out_extra_player(call)
    logging.info(f'{call.data}')


@game_router.callback_query(lambda call: call.data.startswith('удалить'))
async def delete_player_game(call: CallbackQuery):
    await delete_extra_player(call)
    logging.info(f'{call.data}')
