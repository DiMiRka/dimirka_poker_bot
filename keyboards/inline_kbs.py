from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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


def make_count():
    """Клавиатура коэффициента фишки к рублю"""
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
        one_time_keyboard=True
    )
    return keyboards


def start_game():
    """Кнопка запуска игры"""
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
    """Клавиатура процесса игры"""
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


def input_player_game(game_users: list, player_list: list, start: bool):
    """Клавиатура добавления игроков в игру"""
    kb_list = []
    for player in game_users:
        if player not in player_list:
            kb_list.append([InlineKeyboardButton(text=str(player), callback_data=str(player))])
    if start:
        kb_list.append([InlineKeyboardButton(text='Готово 👌🏼', callback_data='стартуем')])
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True
    )
    return keyboards


def purchase_players_keyboards(players: list):
    """Клавиатура выбора игрока из текущей игры для закупа фишек"""
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
    """Клавиатура выбора количества фишек для закупа"""
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
    """Клавиатура выбора игрока из текущей игры для выхода из игры"""
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
    """Кнопка подтверждения выхода игрока из текущей игры"""
    kb_list = [
        [InlineKeyboardButton(text='Подтвердить', callback_data=chips)]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards
