from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.inline_kbs import main_kb, admin_main_kb
from db_hadler.db_class import change_number_db

start_router = Router()


class ChangeDataBse(StatesGroup):
    change_bd = State()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Вызов стартовой клавиатуры"""
    await message.answer('Салам браток 🤙',
                         reply_markup=main_kb(message.from_user.id))


@start_router.callback_query(F.data == 'админ панель')
async def admin_board(call: CallbackQuery):
    await call.message.answer('Что делаем?', reply_markup=admin_main_kb())


@start_router.callback_query(F.data == 'изменить базу данных')
async def change_data_base(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Номер базы данных:')
    await state.set_state(ChangeDataBse.change_bd)


@start_router.message(ChangeDataBse.change_bd)
async def change_data_base_end(message: Message, state: FSMContext):
    number_bd = int(message.text)
    print(number_bd)
    await change_number_db(number_bd)
    await state.clear()
