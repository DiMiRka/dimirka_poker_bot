import pandas as pd
import matplotlib.pyplot as plt

from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from db_hadler.db_class import Database

pd.set_option('display.max_columns', None)
player_list = list()
text_players = str()
date = str()
game_users = list()
game_id = int()


def player_input(text):
    global player_list, text_players, date, game_users, game_id
    if text == 'новая игра':
        player_list = list()
        text_players = str()
        date = str()
        game_users = list()
        game_id = int()

    else:
        player_list.append(text)
        text_players += f'\n{text}'


async def update_users():
    global game_users
    game_users = await Database.get_users_bd()


async def get_users():
    return game_users


def get_players():
    return player_list


def get_players_text():
    return text_players


async def update_date():
    global date
    date = await Database.get_date()


async def get_date():
    return date


async def update_game_id():
    global game_id
    game_id = await Database.get_game_id()


async def get_game_id():
    return game_id


async def input_players_start(call: CallbackQuery):
    player_input(call.data)
    game_players = await get_users()
    kb_list = []
    players_in_game = get_players()
    for player in game_players:
        if player not in players_in_game:
            kb_list.append([InlineKeyboardButton(text=str(player), callback_data=str(player))])
    kb_list.append([InlineKeyboardButton(text='Готово 👌🏼', callback_data='стартуем')])
    new_keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        input_field_placeholder='добавляй рыбок:'
    )
    await call.message.answer(text=f'В игре: {text_players}', reply_markup=new_keyboards)


async def input_players(call: CallbackQuery):
    game_players = game_users
    kb_list = []
    players_in_game = get_players()
    for player in game_players:
        if player not in players_in_game:
            kb_list.append([InlineKeyboardButton(text=str(player), callback_data=str(player))])
    new_keyboards = InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
    )
    await call.message.answer(text=f'Кто эта жертва?👀', reply_markup=new_keyboards)


async def text_start(data):
    print(data)
    text = 'Ну полетели 🎰\n-------------------'
    count = data.get('count')
    players = data.get('players_in_game')
    text += f'\n1 фишка = {count} руб.\n-------------------\nВ игре:'
    for player in players:
        text += f'\n{player}'
    return text


async def text_game(data: dict, count: int):
    date_game = await get_date()
    print(date_game)
    count = count
    text = f'Игра {date_game}\nКоэффициент: 1 к {count}'
    table_game = dict()
    for key in data.keys():
        table_game.setdefault('Игрок', []).append(key)
        for k,v in data.get(key).items():
            table_game.setdefault(k, []).append(v)
    print(table_game)
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



