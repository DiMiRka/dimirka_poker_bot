from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline_kbs import main_kb, admin_main_kb

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
