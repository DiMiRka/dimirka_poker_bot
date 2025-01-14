from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import admins


def main_kb(user_telegram_id: int):
    kb_list = [
        [InlineKeyboardButton(text="🃏 Начать игру", callback_data='начать игру')],
        [InlineKeyboardButton(text="🦈 Добавить игрока", callback_data='добавить игрока')],
        [InlineKeyboardButton(text="📋 Статистика игроков", callback_data='cтатистика игроков')]
    ]
    if user_telegram_id in admins:
        kb_list.append([InlineKeyboardButton(text="⚙️ Админ панель", callback_data='админ панель')])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True)
    return keyboard


def make_count():
    kb_list = [
        [InlineKeyboardButton(text='1 руб.', callback_data='1')],
        [InlineKeyboardButton(text='2 руб.', callback_data='2')],
        [InlineKeyboardButton(text='3 руб.', callback_data='3')],
        [InlineKeyboardButton(text='4 руб.', callback_data='4')],
        [InlineKeyboardButton(text='5 руб.', callback_data='5')]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выберите соотношение 1 фишки к руб.'
    )
    return keyboards


def start_game():
    kb_list = [
        [InlineKeyboardButton(text='✔️', callback_data='битва')],
        [InlineKeyboardButton(text='Добавить еще игроков 🖕', callback_data='ц')]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards
