from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from create_bot import admins


def main_kb(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text="🃏 Начать игру")],
        [KeyboardButton(text="🦈 Добавить игрока")],
        [KeyboardButton(text="📋 Статистика игроков")]
    ]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Воспользуйтесь меню:')
    return keyboard


def start_game():
    kb_list = [
        [KeyboardButton(text='1 руб.')],
        [KeyboardButton(text='2 руб.')],
        [KeyboardButton(text='3 руб.')],
        [KeyboardButton(text='4 руб.')],
        [KeyboardButton(text='5 руб.')]
    ]
    keyboards = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выберите соотношение 1 фишки к руб.'
    )
    return keyboards
