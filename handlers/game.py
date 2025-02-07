import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_hadler.db_class import Database
from create_bot import bot
from keyboards.inline_kbs import start_game, make_count, game_keyboards, purchase_players_keyboards, purchase, exit_players_keyboards, exit_player, main_kb
from utils.game_utils import player_input, get_players, text_game, input_players_start, text_start, input_players, update_users, get_users, update_date, update_game_id, get_game_id

game_router = Router()


class Game(StatesGroup):
    start = State()
    players = State()
    new_game = State()
    end_game = State()


@game_router.callback_query(F.data == 'начать игру')
async def start(call: CallbackQuery, state: FSMContext):
    player_input('новая игра')
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=call.from_user.id):
        await asyncio.sleep(2)
        await update_users()
        await call.message.answer('1 фишка равняется:', reply_markup=make_count())
        await state.set_state(Game.start.state)


@game_router.message(Command('start_game'))
async def start(message: Message, state: FSMContext):
    player_input('новая игра')
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await update_users()
        await message.answer('1 фишка равняется:', reply_markup=make_count())
        await state.set_state(Game.start.state)


@game_router.callback_query(Game.start)
async def players(call: CallbackQuery, state: FSMContext):
    print(call.data)
    await state.update_data(count=int(call.data))
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await asyncio.sleep(1)
        game_players = await get_users()
        kb_list = []
        for player in game_players:
            if player not in get_players():
                kb_list.append([InlineKeyboardButton(text=player, callback_data=player)])
        keyboards = InlineKeyboardMarkup(
            inline_keyboard=kb_list,
            resize_keyboard=True
        )
        await call.message.answer('Кто играет?', reply_markup=keyboards)
        await state.set_state(Game.players.state)


@game_router.callback_query(Game.players)
async def game_start(call: CallbackQuery, state: FSMContext):
    if call.data != 'стартуем':
        await input_players_start(call=call)
        return
    else:
        async with ChatActionSender.typing(bot=bot, chat_id=call.message.from_user.id):
            await asyncio.sleep(2)
            await state.update_data(players_in_game=get_players())
            data = await state.get_data()
            count = data.get('count')
            game_date = dict()
            for player in data.get('players_in_game'):
                game_date[player] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * count, 'Статус': 'В игре',
                                     'Фишки': 0, 'Руб.': 0}
            await state.update_data(game=game_date)
            text = await text_start(data=data)
            await call.message.answer(f'{text}', reply_markup=start_game())
            await state.set_state(Game.new_game.state)


@game_router.callback_query(Game.new_game)
async def game(call: CallbackQuery, state: FSMContext):
    print(call.data)
    game_players = await get_users()
    data = await state.get_data()
    count = data.get('count')
    game_date = data.get('game')

    if call.data == 'битва':
        async with ChatActionSender.typing(bot=bot, chat_id=call.message.from_user.id):
            await asyncio.sleep(2)
            await Database.insert_new_game(count=count)
            await update_date()
            await update_game_id()
            text = await text_game(data=game_date, count=count)
            photo = FSInputFile('game_image.png')
            await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                                 show_caption_above_media=True)
            await state.set_state(Game.new_game.state)
            return

    if call.data == 'добавить игрока':
        await input_players(call=call)
        await state.set_state(Game.new_game.state)
        return

    if call.data in game_players:
        print(call.data)
        player_input(call.data)
        game_date[call.data] = {'Закуп,фш.': 1000, 'Закуп,руб.': 1000 * count, 'Статус': 'В игре',
                                'Фишки': 0, 'Руб.': 0}
        photo = FSInputFile('game_image.png')
        text = await text_game(data=game_date, count=count)
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                             show_caption_above_media=True)
        await state.set_state(Game.new_game.state)
        return

    if call.data == 'докупить':
        players_in_game = get_players()
        await call.message.answer(text='Кто в проёбе?', reply_markup=purchase_players_keyboards(players_in_game))
        await state.set_state(Game.new_game.state)
        return

    if call.data.startswith('закуп'):
        player = call.data[6:]
        await state.update_data(purchase=player)
        await call.message.answer(text='Сколько докупаем?', reply_markup=purchase())
        await state.set_state(Game.new_game.state)
        return

    if call.data.startswith('фишки'):
        chips = call.data.split()[1]
        data = await state.get_data()
        player = data.get('purchase')
        game_date[player]['Закуп,фш.'] = game_date[player].get('Закуп,фш.') + int(chips)
        game_date[player]['Закуп,руб.'] = game_date[player].get('Закуп,руб.') + int(chips) * count
        photo = FSInputFile('game_image.png')
        text = await text_game(data=game_date, count=count)
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                             show_caption_above_media=True)
        await state.set_state(Game.new_game.state)
        return

    if call.data == 'выйти':
        players_in_game = get_players()
        await call.message.answer(text='Кто выходит?', reply_markup=exit_players_keyboards(players_in_game))
        await state.set_state(Game.new_game.state)
        return

    if call.data.startswith('выход'):
        player = call.data[6:]
        await state.update_data(exit=player)
        await call.message.answer(text='Количество фишек на выходе?', reply_markup=None)
        await state.set_state(Game.new_game.state)
        return

    if call.data.isnumeric():
        print(call.data)
        data = await state.get_data()
        player = data.get('exit')
        chips = int(call.data)
        count = data.get('count')
        game_date[player]['Статус'] = 'Вышел'
        game_date[player]['Фишки'] = chips
        game_date[player]['Руб.'] = (chips * count) - game_date[player].get('Закуп,руб.')
        photo = FSInputFile('game_image.png')
        text = await text_game(data=game_date, count=count)
        await state.set_state(Game.new_game.state)
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, reply_markup=game_keyboards(), caption=text,
                             show_caption_above_media=True)

    if call.data == 'закончить':
        data = await state.get_data()
        game_end = data.get('game')
        players_in_game = list()

        for pl in game_end.keys():
            if game_end[pl]['Статус'] == 'В игре':
                players_in_game.append(pl)

        player = players_in_game[0]
        await call.message.answer(f'Подведем итоги 😉\nУ {player} на кармане:', reply_markup=None)
        await state.set_state(Game.end_game.state)


@game_router.message(Game.end_game)
async def end_game(message: Message, state: FSMContext):
    chips = int(message.text)
    data = await state.get_data()
    count = data.get('count')
    game_end = data.get('game')
    players_in_game = list()
    game_id = await get_game_id()

    for pl in game_end.keys():
        if game_end[pl]['Статус'] == 'В игре':
            players_in_game.append(pl)

    if players_in_game:
        player = players_in_game[0]
        game_end[player]['Фишки'] = int(chips)
        game_end[player]['Руб.'] = (chips * count) - game_end[player].get('Закуп,руб.')
        game_end[player]['Статус'] = 'Вышел'

        if len(players_in_game) > 1:
            next_player = players_in_game[1]
            await message.answer(text=f'{next_player} на кармане:')
            return
        else:
            await Database.update_game(game=game_end, game_id=game_id)
            text = await text_game(data=game_end, count=count)
            text += '\nИТОГИ 💰'
            photo = FSInputFile('game_image.png')
            await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=None, caption=text,
                                 show_caption_above_media=True)
            await message.answer(text='До следующего раза, брат 🤙', reply_markup=main_kb(message.from_user.id))


@game_router.message(F.text.isnumeric())
async def out(message: Message, state: FSMContext):
    data = await state.get_data()
    player = data.get('exit')
    chips = message.text
    await message.answer(text=f'{player} по съебам\nВ кармане {chips} фш.', reply_markup=exit_player(chips=chips))
    await state.set_state(Game.new_game.state)
