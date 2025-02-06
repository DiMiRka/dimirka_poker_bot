from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from keyboards.inline_kbs import main_kb

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Вызов стартовой клавиатуры"""
    await message.answer('Салам браток 🤙',
                         reply_markup=main_kb(message.from_user.id))
