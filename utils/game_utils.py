import pandas as pd
import matplotlib.pyplot as plt

from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext

from keyboards import (input_player_game_kb, start_game_kb, game_keyboards, purchase_players_keyboards,
                       exit_players_keyboards, main_kb, game_admin_keyboards, change_purchase_players_keyboards,
                       back_players_keyboards, extra_players_keyboards)
from create_bot import bot
from services import create_game_db, get_players_db, update_game_db

pd.set_option('display.max_columns', None)  # Настройка таблицы pandas
game_users = list()  # Список всех игроков в базе данных

start_status = False  # Статус запущенной игры
player_list = list()  # Список игроков текущей игры
player_out_list = list()  # Список игроков, закончивших текущую игру
text_players = str()  # Оформление текста со списком игроков, участвующих в игре
date = str()  # Дата текущей игры
game_id = int()  # id текущей игры
count = int()  # Коэффициент фишки к рублю текущей игры
game_data = dict()  # Процесс игры
add_bank_player = str()  # Учет игрока для докупа/изменения фишек в процессе игры
out_player = str()  # Учет игрока для выхода из игры


def player_input(text):
    """Добавить игрока в текущую игру"""
    global player_list, text_players, date, game_users, game_data
    if text == 'новая игра':
        '''Обновляем учетные переменные по текущей игре'''
        player_list = list()
        text_players = str()
        date = str()
        game_users = list()
        game_data = dict()
    else:
        player_list.append(text)  # Добавляем игрока в список игроков текущей игры
        text_players += f'\n{text}'  # Актуализируем текст со списком игроков, участвующих в игре


async def update_users():
    """Обновляем список игроков с базы данных"""
    global game_users
    users = await get_players_db()
    game_users = [user.login for user in users]


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


async def get_players():
    """Получить список игроков текущей игры"""
    return player_list


def get_players_text():
    """Получить оформленный текст со списком игроков в игре"""
    return text_players


async def update_add_on_player(call: CallbackQuery):
    global add_bank_player
    add_bank_player = call.data[6:]


async def update_change_on_player(call: CallbackQuery):
    global add_bank_player
    add_bank_player = call.data[9:]


async def update_out_layer(call: CallbackQuery):
    global out_player
    out_player = call.data[6:]


async def input_players_start(call: CallbackQuery):
    """Добавить игроков в текущую игру перед стартом"""
    if call.data.startswith('фишка'):
        new_keyboards = input_player_game_kb(game_users=game_users, player_list=player_list, start=start_status)
        await call.message.answer(text='Кто играет?', reply_markup=await new_keyboards)
    else:
        player_input(call.data[14:])
        new_keyboards = input_player_game_kb(game_users=game_users, player_list=player_list, start=start_status)
        await call.message.answer(text=f'В игре: {text_players}', reply_markup=await new_keyboards)


async def input_players(call: CallbackQuery):
    """"Выбрать игрока для добавления в текущую игру"""
    new_keyboards = input_player_game_kb(game_users=game_users, player_list=player_list, start=start_status)
    await call.message.answer(text=f'Кто эта жертва?👀', reply_markup=await new_keyboards)


async def input_players_game(call: CallbackQuery):
    """"Добавить игрока в текущую игру"""
    player_input(call.data[13:])
    game_data[call.data[13:]] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * count, 'Статус': 'В игре', 'Фишки': 0, 'Руб.': 0}
    photo = FSInputFile('utils/game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id), caption=text,
                         show_caption_above_media=True)


async def add_on_players(call: CallbackQuery):
    """Выбрать игрока для докупа фишек в текущую игру"""
    await call.message.answer(text='Кто в проёбе?', reply_markup=await purchase_players_keyboards(player_list))


async def add_on_utils(call: CallbackQuery):
    """Докупить игроку фишки в текущей игре"""
    chips = call.data.split()[1]
    player = add_bank_player
    game_data[player]['Закуп,фш.'] = game_data[player].get('Закуп,фш.') + int(chips)
    game_data[player]['Закуп,руб.'] = game_data[player].get('Закуп,руб.') + int(chips) * count
    photo = FSInputFile('utils/game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id), caption=text,
                         show_caption_above_media=True)


async def start_out_player(call: CallbackQuery):
    """Выбрать игрока для выхода из текущей игры"""
    await call.message.answer(text='Кто по съебам?', reply_markup=await exit_players_keyboards(player_list))


async def player_out_game(call: CallbackQuery):
    """Определить количество фишек игрока на выходе из игры"""
    await update_out_layer(call)
    player_out_list.append(out_player)
    player_list.remove(out_player)
    await call.message.answer(text='Количество фишек на кармане?', reply_markup=None)


async def result_chips(message: Message, state: FSMContext):
    """Подсчитать результаты вышедшего игрока и обновить статус на Вышел"""
    global start_status, out_player
    if start_status:  # В случае выхода игрока в процессе игры
        await state.clear()
        chips = int(message.text)
        game_data[out_player]['Статус'] = 'Вышел'
        game_data[out_player]['Фишки'] = chips
        game_data[out_player]['Руб.'] = (chips * count) - game_data[out_player].get('Закуп,руб.')
        photo = FSInputFile('utils/game_image.png')
        text = await text_game()
        await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=await game_keyboards(message.from_user.id), caption=text,
                             show_caption_above_media=True)
    else:  # В случае окончания игры
        chips = int(message.text)
        game_data[out_player]['Статус'] = 'Вышел'
        game_data[out_player]['Фишки'] = chips
        game_data[out_player]['Руб.'] = (chips * count) - game_data[out_player].get('Закуп,руб.')
        if player_list:  # Зацикливаем процесс подсчета результатов в конце игры до выхода всех игроков
            out_player = player_list.pop(0)
            await message.answer(text=f'{out_player} на кармане:')
        else:  # Выводим итоги оконченной игры
            await update_game_db(game_data, game_id)
            await state.clear()
            text = await text_game()
            text += '\nИТОГИ 💰'
            photo = FSInputFile('utils/game_image.png')
            await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=None, caption=text,
                                 show_caption_above_media=True)
            await message.answer(text='До следующего раза, брат 🤙', reply_markup=await main_kb(message.from_user.id))


async def text_start():
    """Оформление текста перед стартом игры"""
    text = 'Ну полетели 🎰\n-------------------'
    text += f'\n1 фишка = {count} руб.\n-------------------\nВ игре:'
    for player in player_list:
        text += f'\n{player}'
    return text


async def start_game(call: CallbackQuery):
    """Процесс запуска игры"""
    for player in player_list:
        game_data[player] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * count, 'Статус': 'В игре',
                             'Фишки': 0, 'Руб.': 0}
    text = await text_start()
    await call.message.answer(text=text, reply_markup=await start_game_kb())


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
    plt.savefig(f'utils/game_image.png', bbox_inches='tight')
    print(tb)
    return text


async def game_utils(call: CallbackQuery):
    """Оформление сообщения процесса игры"""
    global start_status, date, game_id
    if not start_status:
        date, game_id = await create_game_db(count=count)
        text = await text_game()
        photo = FSInputFile('utils/game_image.png')
        start_status = True
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id), caption=text,
                             show_caption_above_media=True)
    else:
        pass


async def game_end_start(call: CallbackQuery):
    """Процесс запуска завершения игры"""
    global start_status, out_player
    if start_status:
        out_player = player_list.pop(0)
        start_status = False
        await call.message.answer(f'Подведем итоги 😉\nУ {out_player} на кармане:', reply_markup=None)


async def admin_board_game(call: CallbackQuery):
    """Админ панель в процессе игры"""
    await call.message.answer('Что делаем?', reply_markup=await game_admin_keyboards())


async def change_purchase_players(call: CallbackQuery):
    """Выбрать игрока для смены закупа в процессе игры"""
    await call.message.answer(text='Кто?', reply_markup=await change_purchase_players_keyboards(player_list))


async def change_purchase_utils(message: Message):
    """Поменять игроку докуп в текущей игре"""
    chips = message.text
    player = add_bank_player
    game_data[player]['Закуп,фш.'] = int(chips)
    game_data[player]['Закуп,руб.'] = int(chips) * count
    photo = FSInputFile('utils/game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=await game_keyboards(message.from_user.id), caption=text,
                         show_caption_above_media=True)


async def game_back_player(call: CallbackQuery):
    """Выбрать игрока которого вернем в игру"""
    await call.message.answer(text='Кто?', reply_markup=await back_players_keyboards(player_out_list))


async def game_back_player_end(call: CallbackQuery):
    """Вернуть игрока в текущую игру"""
    player = call.data.split()[1]
    player_out_list.remove(player)
    game_data[player]['Статус'] = 'В игре'
    game_data[player]['Фишки'] = 0
    game_data[player]['Руб.'] = 0
    photo = FSInputFile('utils/game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id),
                         caption=text,
                         show_caption_above_media=True)


async def out_extra_player(call: CallbackQuery):
    """Выбрать игрока для выхода из текущей игры"""
    await call.message.answer(text='Кто?', reply_markup=await extra_players_keyboards(player_list))


async def delete_extra_player(call: CallbackQuery):
    """Удалить игрока из текущей игры"""
    player = call.data.split()[1]
    player_list.remove(player)
    del game_data[player]
    photo = FSInputFile('utils/game_image.png')
    text = await text_game()
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id),
                         caption=text,
                         show_caption_above_media=True)
