from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import admins


def main_kb(user_telegram_id: int):
    """"Клавиатура меню"""
    kb_list = [
        [InlineKeyboardButton(text="🃏 Начать игру", callback_data='начать игру')],
        [InlineKeyboardButton(text="🦈 Добавить игрока", callback_data='новый игрок')],
        [InlineKeyboardButton(text="📋 Статистика игроков", callback_data='cтатистика игроков')]
    ]
    if user_telegram_id in admins:
        kb_list.append([InlineKeyboardButton(text="⚙️ Админ панель", callback_data='админ панель')])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True)
    return keyboard


def admin_main_kb():
    kb_list = [
        [InlineKeyboardButton(text="📋 Статистика игроков", callback_data='cтатистика игроков')]
    ]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True)
    return keyboard
