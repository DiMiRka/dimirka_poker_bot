from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import admins


def main_kb(user_telegram_id: int):
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
        [InlineKeyboardButton(text='Старт ✔️', callback_data='битва')]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


def game_keyboards():
    kb_list = [
        [InlineKeyboardButton(text='Добавить игрока 🎣', callback_data='добавить игрока')],
        [InlineKeyboardButton(text='Докуп 💲', callback_data='докупить')],
        [InlineKeyboardButton(text='Вышел 🚪', callback_data='выйти')],
        [InlineKeyboardButton(text='Закончить игру 🔚', callback_data='закончить')]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


def purchase_players_keyboards(players: list):
    kb_list = []
    for player in players:
        kb_list.append([InlineKeyboardButton(text=player, callback_data=f'закуп {player}')])
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


def purchase():
    kb_list = [
        [InlineKeyboardButton(text='500 фишек', callback_data='фишки 500')],
        [InlineKeyboardButton(text='1000 фишек', callback_data='фишки 1000')],
        [InlineKeyboardButton(text='2000 фишек', callback_data='фишки 2000')]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


def exit_players_keyboards(players: list):
    kb_list = []
    for player in players:
        kb_list.append([InlineKeyboardButton(text=player, callback_data=f'выход {player}')])
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


def exit_player(chips):
    kb_list = [
        [InlineKeyboardButton(text='Подтвердить', callback_data=chips)]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards
