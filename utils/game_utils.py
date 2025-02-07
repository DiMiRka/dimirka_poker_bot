import pandas as pd
import matplotlib.pyplot as plt

from aiogram.types import CallbackQuery, FSInputFile

from keyboards.inline_kbs import input_player_game_kb, start_game_kb, game_keyboards, purchase_players_keyboards
from db_hadler.db_class import Database
from create_bot import bot

pd.set_option('display.max_columns', None)  # Настройка таблицы pandas
game_users = list()  # Список всех игроков в базе данных

start_status = False  # Статус запущенной игры
player_list = list()  # Список игроков текущей игры
text_players = str()  # Оформление текста со списком игроков, участвующих в игре
date = str()  # Дата текущей игры
game_id = int()  # id текущей игры
count = int()  # Коэффициент фишки к рублю текущей игры
game_data = dict()  # Процесс игры
add_on_player = str()  # Учет игрока для докупа фишек в процессе игры


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


async def update_count(c: int):
    """Обновляем коэффициент фишки к рублю текущей игры"""
    global count
    count = c


async def get_count():
    """Получаем коэффициент фишки к рублю текущей игры"""
    return count


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


async def update_add_on_player(call: CallbackQuery):
    global add_on_player
    add_on_player = call


async def input_players_start(call: CallbackQuery):
    """Добавить игроков в текущую игру перед стартом"""
    if call.data.startswith('фишка'):
        new_keyboards = input_player_game_kb(game_users=game_users, player_list=player_list, start=start_status)
        await call.message.answer(text='Кто играет?', reply_markup=new_keyboards)
    else:
        print(call.data[14:])
        player_input(call.data[14:])
        new_keyboards = input_player_game_kb(game_users=game_users, player_list=player_list, start=start_status)
        await call.message.answer(text=f'В игре: {text_players}', reply_markup=new_keyboards)


async def input_players(call: CallbackQuery):
    """"Выбрать игрока для добавления в текущую игру"""
    new_keyboards = input_player_game_kb(game_users=game_users, player_list=player_list, start=start_status)
    await call.message.answer(text=f'Кто эта жертва?👀', reply_markup=new_keyboards)


async def input_players_game(call: CallbackQuery):
    """"Добавить игрока в текущую игру"""
    player_input(call.data[13:])
    game_data[call.data[13:]] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * count, 'Статус': 'В игре', 'Фишки': 0, 'Руб.': 0}
    photo = FSInputFile('game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                         show_caption_above_media=True)


async def add_on_players(call: CallbackQuery):
    """Выбрать игрока для докупа фишек в текущую игру"""
    await call.message.answer(text='Кто в проёбе?', reply_markup=purchase_players_keyboards(player_list))


async def add_on(call: CallbackQuery):
    """Докупить игроку фишки в текущей игре"""
    chips = call.split()[1]
    player = add_on_player
    game_data[player]['Закуп,фш.'] = game_data[player].get('Закуп,фш.') + int(chips)
    game_data[player]['Закуп,руб.'] = game_data[player].get('Закуп,руб.') + int(chips) * count
    photo = FSInputFile('game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                         show_caption_above_media=True)


async def text_start():
    """Оформление текста перед стартом игры"""
    text = 'Ну полетели 🎰\n-------------------'
    text += f'\n1 фишка = {count} руб.\n-------------------\nВ игре:'
    for player in player_list:
        text += f'\n{player}'
    return text


async def start_game(call: CallbackQuery):
    for player in player_list:
        game_data[player] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * count, 'Статус': 'В игре',
                             'Фишки': 0, 'Руб.': 0}
    text = await text_start()
    await call.message.answer(text=text, reply_markup=start_game_kb())


async def text_game():
    """Оформление текста игры"""
    text = f'Игра {date}\nКоэффициент: 1 к {count}'
    table_game = dict()
    for key in game_data.keys():
        table_game.setdefault('Игрок', []).append(key)
        for k, v in game_data.get(key).items():
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


async def game_utils(call: CallbackQuery):
    """Оформление сообщения процесса игры"""
    global start_status
    if not start_status:
        await Database.insert_new_game(count=count)
        await update_date()
        await update_game_id()
        text = await text_game()
        photo = FSInputFile('game_image.png')
        start_status = True
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                             show_caption_above_media=True)
    else:
        pass
