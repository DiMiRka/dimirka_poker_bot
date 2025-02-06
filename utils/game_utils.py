import pandas as pd
import matplotlib.pyplot as plt

from aiogram.types import CallbackQuery

from keyboards.inline_kbs import input_player_game
from db_hadler.db_class import Database

pd.set_option('display.max_columns', None)  # Настройка таблицы pandas
player_list = list()  # Список игроков текущей игры
text_players = str()  # Оформление текста со списком игроков, участвующих в игре
date = str()  # Учет даты текущей игры
game_users = list()  # Список всех игроков в базе данных
game_id = int()  # id текущей игры


def player_input(text):
    """Добавить игрока в текущую игру"""
    global player_list, text_players, date, game_users, game_id
    if text == 'новая игра':
        '''Обновляем учетные переменные по текущей игре'''
        player_list = list()
        text_players = str()
        date = str()
        game_users = list()
        game_id = int()

    else:
        player_list.append(text)  # Добавляем игрока в список игроков текущей игры
        text_players += f'\n{text}'  # Актуализируем текст со списком игроков, участвующих в игре


async def update_users():
    """Обновляем список игроков с базы данных"""
    global game_users
    game_users = await Database.get_users_bd()


async def get_users():
    """Получить список игроков базы данных"""
    return game_users


def get_players():
    """Получить список игроков ткущей игры"""
    return player_list


def get_players_text():
    """Получить оформленный текст со списком игроков в игре"""
    return text_players


async def update_date():
    """Обновить дату последней игры из базы данных"""
    global date
    date = await Database.get_date()


async def get_date():
    """Получить дату текущей игры"""
    return date


async def update_game_id():
    """Обновить id текущей игры"""
    global game_id
    game_id = await Database.get_game_id()


async def get_game_id():
    """Получить id текущей игры"""
    return game_id


async def input_players_start(call: CallbackQuery):
    """Добавить игроков в текущую игру перед стартом"""
    player_input(call.data)
    new_keyboards = input_player_game(game_users=game_users, player_list=player_list, start=True)
    await call.message.answer(text=f'В игре: {text_players}', reply_markup=new_keyboards)


async def input_players(call: CallbackQuery):
    """"Добавить игрока в текущую игру"""
    new_keyboards = input_player_game(game_users=game_users, player_list=player_list, start=False)
    await call.message.answer(text=f'Кто эта жертва?👀', reply_markup=new_keyboards)


async def text_start(data):
    """Оформление текста перед стартом игры"""
    text = 'Ну полетели 🎰\n-------------------'
    count = data.get('count')
    players = data.get('players_in_game')
    text += f'\n1 фишка = {count} руб.\n-------------------\nВ игре:'
    for player in players:
        text += f'\n{player}'
    return text


async def text_game(data: dict, count: int):
    """Оформление сообщения процесса игры"""
    text = f'Игра {date}\nКоэффициент: 1 к {count}'
    table_game = dict()
    for key in data.keys():
        table_game.setdefault('Игрок', []).append(key)
        for k, v in data.get(key).items():
            table_game.setdefault(k, []).append(v)
    tb = pd.DataFrame.from_dict(table_game)
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.set_size_inches(6, 4)
    fig.canvas.manager.full_screen_toggle()
    fig.set_facecolor('#4f4f4f')
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=tb.values,
             colLabels=tb.columns,
             loc='center',
             cellLoc='center',
             rowLoc='center',
             colColours=['YellowGreen'] * 6)
    plt.savefig(f'game_image.png', bbox_inches='tight')
    print(tb)
    return text
