from aiogram.types import CallbackQuery, BufferedInputFile, Message
from aiogram.fsm.context import FSMContext

from keyboards import (make_count, purchase, input_player_game_kb, start_game_kb, game_keyboards, purchase_players_keyboards,
                       exit_players_keyboards, main_kb, game_admin_keyboards, change_purchase_players_keyboards,
                       back_players_keyboards, extra_players_keyboards)
from create_bot import bot
from services import create_game_db, get_players_db, save_active_game_db, finish_game_db
from utils.game_state import get_game, reset_game, games, game_snapshot
from utils.table_image import render_table


def player_input(chat_id: int, text):
    """Добавить игрока в текущую игру"""
    game = get_game(chat_id)
    if text == 'новая игра':
        reset_game(chat_id)
    else:
        game.player_list.append(text)  # Добавляем игрока в список игроков текущей игры
        game.text_players += f'\n{text}'  # Актуализируем текст со списком игроков, участвующих в игре


async def update_users(chat_id: int):
    """Обновляем список игроков с базы данных"""
    game = get_game(chat_id)
    users = await get_players_db()
    game.game_users = [user.login for user in users]


async def get_users(chat_id: int):
    """Получить список игроков базы данных"""
    game = get_game(chat_id)
    return game.game_users


async def update_count(chat_id: int, c: int):
    """Обновляем коэффициент фишки к рублю текущей игры"""
    game = get_game(chat_id)
    game.count = c
    game.phase = 'players'
    await _save_game(chat_id)


async def get_count(chat_id: int):
    """Получаем коэффициент фишки к рублю текущей игры"""
    game = get_game(chat_id)
    return game.count


async def get_players(chat_id: int):
    """Получить список игроков текущей игры"""
    game = get_game(chat_id)
    return game.player_list


def get_players_text(chat_id: int):
    """Получить оформленный текст со списком игроков в игре"""
    game = get_game(chat_id)
    return game.text_players


async def update_add_on_player(call: CallbackQuery):
    game = get_game(call.message.chat.id)
    game.add_bank_player = call.data[6:]
    game.pending_action = 'purchase'
    game.pending_user_id = call.from_user.id
    await _save_game(call.message.chat.id)


async def update_change_on_player(call: CallbackQuery):
    game = get_game(call.message.chat.id)
    game.add_bank_player = call.data[9:]
    game.pending_action = 'change_purchase'
    game.pending_user_id = call.from_user.id
    await _save_game(call.message.chat.id)


async def _update_out_layer(call: CallbackQuery):
    game = get_game(call.message.chat.id)
    game.out_player = call.data[6:]


async def input_players_start(call: CallbackQuery):
    """Добавить игроков в текущую игру перед стартом"""
    game = get_game(call.message.chat.id)
    if call.data.startswith('фишка'):
        new_keyboards = input_player_game_kb(game_users=game.game_users, player_list=game.player_list, start=game.start_status)
        await _save_game(call.message.chat.id)
        await call.message.answer(text='Кто играет?', reply_markup=await new_keyboards)
    else:
        player_input(call.message.chat.id, call.data[14:])
        new_keyboards = input_player_game_kb(game_users=game.game_users, player_list=game.player_list, start=game.start_status)
        await _save_game(call.message.chat.id)
        await call.message.answer(text=f'В игре: {game.text_players}', reply_markup=await new_keyboards)


async def input_players(call: CallbackQuery):
    """"Выбрать игрока для добавления в текущую игру"""
    game = get_game(call.message.chat.id)
    new_keyboards = input_player_game_kb(game_users=game.game_users, player_list=game.player_list, start=game.start_status)
    await call.message.answer(text=f'Кто эта жертва?👀', reply_markup=await new_keyboards)


async def input_players_game(call: CallbackQuery):
    """"Добавить игрока в текущую игру"""
    game = get_game(call.message.chat.id)
    player_input(call.message.chat.id, call.data[13:])
    game.game_data[call.data[13:]] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * game.count, 'Статус': 'В игре', 'Фишки': 0, 'Руб.': 0}
    await _save_game(call.message.chat.id)
    text, photo = await _text_game(call.message.chat.id)
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id), caption=text,
                         show_caption_above_media=True)


async def add_on_players(call: CallbackQuery):
    """Выбрать игрока для докупа фишек в текущую игру"""
    game = get_game(call.message.chat.id)
    await call.message.answer(text='Кто в проёбе?', reply_markup=await purchase_players_keyboards(game.player_list))


async def add_on_utils(call: CallbackQuery):
    """Докупить игроку фишки в текущей игре"""
    game = get_game(call.message.chat.id)
    chips = call.data.split()[1]
    player = game.add_bank_player
    game.game_data[player]['Закуп,фш.'] = game.game_data[player].get('Закуп,фш.') + int(chips)
    game.game_data[player]['Закуп,руб.'] = game.game_data[player].get('Закуп,руб.') + int(chips) * game.count
    game.pending_action = ''
    game.pending_user_id = 0
    await _save_game(call.message.chat.id)
    text, photo = await _text_game(call.message.chat.id)
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id), caption=text,
                         show_caption_above_media=True)


async def start_out_player(call: CallbackQuery):
    """Выбрать игрока для выхода из текущей игры"""
    game = get_game(call.message.chat.id)
    await call.message.answer(text='Кто по съебам?', reply_markup=await exit_players_keyboards(game.player_list))


async def player_out_game(call: CallbackQuery):
    """Определить количество фишек игрока на выходе из игры"""
    game = get_game(call.message.chat.id)
    await _update_out_layer(call)
    game.player_out_list.append(game.out_player)
    game.player_list.remove(game.out_player)
    game.pending_action = 'result'
    game.pending_user_id = call.from_user.id
    await _save_game(call.message.chat.id)
    await call.message.answer(text='Количество фишек на кармане?', reply_markup=None)


async def _read_chips(message: Message) -> int | None:
    try:
        chips = int(message.text)
    except (TypeError, ValueError):
        chips = -1
    if chips < 0:
        await message.answer('Не тупи, бро, введи количество фишек целым числом не меньше 0')
        return None
    return chips


async def result_chips(message: Message, state: FSMContext):
    """Подсчитать результаты вышедшего игрока и обновить статус на Вышел"""
    game = get_game(message.chat.id)
    chips = await _read_chips(message)
    if chips is None:
        return
    result = game.game_data[game.out_player]
    result['Статус'] = 'Вышел'
    result['Фишки'] = chips
    result['Руб.'] = chips * game.count - result['Закуп,руб.']
    if game.start_status:  # В случае выхода игрока в процессе игры
        game.pending_action = ''
        game.pending_user_id = 0
        await _save_game(message.chat.id)
        await state.clear()
        text, photo = await _text_game(message.chat.id)
        await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=await game_keyboards(message.from_user.id), caption=text,
                             show_caption_above_media=True)
    else:  # В случае окончания игры
        if game.player_list:  # Зацикливаем процесс подсчета результатов в конце игры до выхода всех игроков
            game.out_player = game.player_list.pop(0)
            await _save_game(message.chat.id)
            await message.answer(text=f'{game.out_player} на кармане:')
        else:  # Выводим итоги оконченной игры
            await finish_game_db(message.chat.id, game.game_data, game.game_id)
            game.phase = 'finished'
            game.pending_action = ''
            game.pending_user_id = 0
            await state.clear()
            text, photo = await _text_game(message.chat.id)
            text += '\nИТОГИ 💰'
            await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=None, caption=text,
                                 show_caption_above_media=True)
            await message.answer(text='До следующего раза, брат 🤙', reply_markup=await main_kb(message.from_user.id))


async def _text_start(chat_id: int):
    """Оформление текста перед стартом игры"""
    game = get_game(chat_id)
    text = 'Ну полетели 🎰\n-------------------'
    text += f'\n1 фишка = {game.count} руб.\n-------------------\nВ игре:'
    for player in game.player_list:
        text += f'\n{player}'
    return text


async def start_game(call: CallbackQuery):
    """Процесс запуска игры"""
    game = get_game(call.message.chat.id)
    for player in game.player_list:
        game.game_data[player] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * game.count, 'Статус': 'В игре',
                             'Фишки': 0, 'Руб.': 0}
    game.phase = 'ready'
    await _save_game(call.message.chat.id)
    text = await _text_start(call.message.chat.id)
    await call.message.answer(text=text, reply_markup=await start_game_kb())


async def _text_game(chat_id: int):
    """Оформление текста игры"""
    game = get_game(chat_id)
    text = f'Игра {game.date}\nКоэффициент: 1 к {game.count}'
    table_game = dict()
    for key in game.game_data.keys():
        table_game.setdefault('Игрок', []).append(key)
        for k, v in game.game_data.get(key).items():
            table_game.setdefault(k, []).append(v)
    image = await render_table(table_game)
    return text, BufferedInputFile(image, filename='game.png')


async def game_utils(call: CallbackQuery):
    """Оформление сообщения процесса игры"""
    game = get_game(call.message.chat.id)
    if not game.start_status:
        game.date, game.game_id = await create_game_db(
            count=game.count, chat_id=call.message.chat.id, state=game_snapshot(call.message.chat.id),
        )
        game.start_status = True
        game.phase = 'playing'
        text, photo = await _text_game(call.message.chat.id)
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id), caption=text,
                             show_caption_above_media=True)
    else:
        pass


async def game_end_start(call: CallbackQuery):
    """Процесс запуска завершения игры"""
    game = get_game(call.message.chat.id)
    if game.start_status:
        if not game.player_list:
            await finish_game_db(call.message.chat.id, game.game_data, game.game_id)
            game.start_status = False
            game.phase = 'finished'
            await call.message.answer('Игра завершена.', reply_markup=await main_kb(call.from_user.id))
            return False
        game.out_player = game.player_list.pop(0)
        game.start_status = False
        game.phase = 'finishing'
        game.pending_action = 'result'
        game.pending_user_id = call.from_user.id
        await _save_game(call.message.chat.id)
        await call.message.answer(f'Подведем итоги 😉\nУ {game.out_player} на кармане:', reply_markup=None)
        return True
    return False


async def admin_board_game(call: CallbackQuery):
    """Админ панель в процессе игры"""
    await call.message.answer('Что делаем?', reply_markup=await game_admin_keyboards())


async def change_purchase_players(call: CallbackQuery):
    """Выбрать игрока для смены закупа в процессе игры"""
    game = get_game(call.message.chat.id)
    await call.message.answer(text='Кто?', reply_markup=await change_purchase_players_keyboards(game.player_list))


async def change_purchase_utils(message: Message) -> bool:
    """Поменять игроку докуп в текущей игре"""
    game = get_game(message.chat.id)
    chips = await _read_chips(message)
    if chips is None:
        return False
    player = game.add_bank_player
    game.game_data[player]['Закуп,фш.'] = chips
    game.game_data[player]['Закуп,руб.'] = chips * game.count
    game.pending_action = ''
    game.pending_user_id = 0
    await _save_game(message.chat.id)
    text, photo = await _text_game(message.chat.id)
    await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=await game_keyboards(message.from_user.id), caption=text,
                         show_caption_above_media=True)
    return True


async def game_back_player(call: CallbackQuery):
    """Выбрать игрока которого вернем в игру"""
    game = get_game(call.message.chat.id)
    await call.message.answer(text='Кто?', reply_markup=await back_players_keyboards(game.player_out_list))


async def game_back_player_end(call: CallbackQuery):
    """Вернуть игрока в текущую игру"""
    game = get_game(call.message.chat.id)
    player = call.data.split()[1]
    game.player_out_list.remove(player)
    game.player_list.append(player)
    game.game_data[player]['Статус'] = 'В игре'
    game.game_data[player]['Фишки'] = 0
    game.game_data[player]['Руб.'] = 0
    await _save_game(call.message.chat.id)
    text, photo = await _text_game(call.message.chat.id)
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id),
                         caption=text,
                         show_caption_above_media=True)


async def out_extra_player(call: CallbackQuery):
    """Выбрать игрока для выхода из текущей игры"""
    game = get_game(call.message.chat.id)
    await call.message.answer(text='Кто?', reply_markup=await extra_players_keyboards(game.player_list))


async def delete_extra_player(call: CallbackQuery):
    """Удалить игрока из текущей игры"""
    game = get_game(call.message.chat.id)
    player = call.data.split()[1]
    game.player_list.remove(player)
    del game.game_data[player]
    await _save_game(call.message.chat.id)
    text, photo = await _text_game(call.message.chat.id)
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=await game_keyboards(call.from_user.id),
                         caption=text,
                         show_caption_above_media=True)


async def _save_game(chat_id: int):
    await save_active_game_db(chat_id, game_snapshot(chat_id))


async def begin_game(message: Message, state: FSMContext):
    game = games.get(message.chat.id)
    if game is not None and game.phase != 'finished':
        await message.answer('В этом чате уже есть незавершённая игра. Продолжите через /resume_game.')
        return
    reset_game(message.chat.id)
    await update_users(message.chat.id)
    await _save_game(message.chat.id)
    await state.clear()
    await message.answer('1 фишка равняется:', reply_markup=await make_count())


async def resume_game(message: Message, state: FSMContext):
    from utils.game_fsm import ChangePurchase, ResultGame

    game = games.get(message.chat.id)
    if game is None or game.phase == 'finished':
        await message.answer('В этом чате нет незавершённой игры. Начните через /start_game.')
        return
    if game.pending_action and game.pending_user_id != message.from_user.id:
        await message.answer('Бот ждёт ответ от игрока, который начал эту операцию.')
        return
    await state.clear()
    if game.pending_action == 'result':
        await state.set_state(ResultGame.result_bank)
        await message.answer(f'{game.out_player} на кармане:')
    elif game.pending_action == 'change_purchase':
        await state.set_state(ChangePurchase.change)
        await message.answer(f'Итоговый закуп для {game.add_bank_player}:')
    elif game.pending_action == 'purchase':
        await message.answer(f'Сколько докупаем для {game.add_bank_player}?', reply_markup=await purchase())
    elif game.phase == 'coefficient':
        await message.answer('1 фишка равняется:', reply_markup=await make_count())
    elif game.phase == 'players':
        await message.answer(f'В игре: {game.text_players}', reply_markup=await input_player_game_kb(
            game_users=game.game_users, player_list=game.player_list, start=False,
        ))
    elif game.phase == 'ready':
        await message.answer(await _text_start(message.chat.id), reply_markup=await start_game_kb())
    else:
        text, photo = await _text_game(message.chat.id)
        await bot.send_photo(chat_id=message.chat.id, photo=photo,
                             reply_markup=await game_keyboards(message.from_user.id), caption=text,
                             show_caption_above_media=True)
