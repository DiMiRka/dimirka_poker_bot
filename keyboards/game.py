from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import admins


async def make_count():
    """Клавиатура коэффициента фишки к рублю"""
    kb_list = [
        [InlineKeyboardButton(text='1 руб.', callback_data='фишка 1')],
        [InlineKeyboardButton(text='2 руб.', callback_data='фишка 2')],
        [InlineKeyboardButton(text='3 руб.', callback_data='фишка 3')],
        [InlineKeyboardButton(text='4 руб.', callback_data='фишка 4')],
        [InlineKeyboardButton(text='5 руб.', callback_data='фишка 5')]
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboards


async def start_game_kb():
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


async def game_keyboards(user_telegram_id: int):
    """Клавиатура процесса игры"""
    kb_list = [
        [InlineKeyboardButton(text='Добавить игрока 🎣', callback_data='добавить игрока')],
        [InlineKeyboardButton(text='Докупить игрока 💲', callback_data='докупить')],
        [InlineKeyboardButton(text='Выход игрока 🚪', callback_data='выйти')],
        [InlineKeyboardButton(text='Закончить игру 🔚', callback_data='закончить')]
    ]
    if user_telegram_id in admins:
        kb_list.append([InlineKeyboardButton(text="️Админ панель ⚙", callback_data='админ панель игры')])

    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


async def game_admin_keyboards():
    """Клавиатура админ панели в процессе игры"""
    kb_list = [
        [InlineKeyboardButton(text='Поменять закуп игрока 💲', callback_data='поменять закуп')],
        [InlineKeyboardButton(text='Вернуть игрока в игру 🎣', callback_data='возврат игрока')],
        [InlineKeyboardButton(text='Убрать лишнего игрока 🔙', callback_data='убрать лишнего')],
    ]
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


async def input_player_game_kb(game_users: list, player_list: list, start: bool):
    """Клавиатура добавления игроков в игру"""
    builder = InlineKeyboardBuilder()
    if not start:
        for player in game_users:
            if player not in player_list:
                builder.button(text=str(player), callback_data=f'игрок в старт {str(player)}')
        builder.adjust(3)
        builder.row(InlineKeyboardButton(text='Готово 👌🏼', callback_data='стартуем'))

    else:
        for player in game_users:
            if player not in player_list:
                builder.button(text=str(player), callback_data=f'игрок в игру {str(player)}')
        builder.adjust(3)
    keyboards = builder.as_markup()
    return keyboards


async def purchase_players_keyboards(players: list):
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


async def purchase():
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


async def exit_players_keyboards(players: list):
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


async def back_players_keyboards(players: list):
    """Клавиатура выбора игрока вышедшего из текущей игры для возврата в игру"""
    kb_list = []
    for player in players:
        kb_list.append([InlineKeyboardButton(text=player, callback_data=f'вернуть {player}')])
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


async def extra_players_keyboards(players: list):
    """Клавиатура выбора игрока из текущей игры для удаления из игры"""
    kb_list = []
    for player in players:
        kb_list.append([InlineKeyboardButton(text=player, callback_data=f'удалить {player}')])
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards


async def exit_player(chips):
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


async def change_purchase_players_keyboards(players: list):
    """Клавиатура выбора игрока из текущей игры для закупа фишек"""
    kb_list = []
    for player in players:
        kb_list.append([InlineKeyboardButton(text=player, callback_data=f'поменять {player}')])
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboards
