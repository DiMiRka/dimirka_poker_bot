import asyncio
from copy import deepcopy

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from services import load_active_games_db
from utils.game_fsm import ChangePurchase, ResultGame
from utils.game_state import GameState, games


_chat_locks: dict[int, asyncio.Lock] = {}


class GamePersistenceMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        message = event.message if isinstance(event, CallbackQuery) else event
        chat_id = message.chat.id
        lock = _chat_locks.setdefault(chat_id, asyncio.Lock())
        async with lock:
            if not isinstance(event, CallbackQuery) and 'state' in data:
                data['raw_state'] = await data['state'].get_state()
            game = games.get(chat_id)
            before = deepcopy(game)
            words = (message.text or '').split()
            is_resume = bool(words and words[0].split('@')[0] == '/resume_game')
            if isinstance(event, CallbackQuery) and event.data != 'начать игру':
                if game is None or game.phase == 'finished':
                    await event.answer('Начните игру через /start_game.', show_alert=True)
                    return
            if game and game.pending_action and not is_resume:
                if event.from_user.id != game.pending_user_id:
                    await message.answer('Бот ждёт ответ от игрока, который начал эту операцию.')
                    return
                if isinstance(event, CallbackQuery):
                    if game.pending_action != 'purchase' or not event.data.startswith('фишки '):
                        await event.answer('Завершите текущую операцию или используйте /resume_game.', show_alert=True)
                        return
                elif game.pending_action in ('result', 'change_purchase'):
                    state = data['state']
                    expected = ResultGame.result_bank if game.pending_action == 'result' else ChangePurchase.change
                    await state.set_state(expected)
                    data['raw_state'] = expected.state
                else:
                    await message.answer('Выберите количество докупаемых фишек на кнопках или используйте /resume_game.')
                    return
            if isinstance(event, CallbackQuery) and game and not game.pending_action:
                if event.data == 'битва':
                    phases = ('ready',)
                elif event.data == 'стартуем':
                    phases = ('players', 'ready')
                elif event.data.startswith('фишка '):
                    phases = ('coefficient', 'players')
                elif event.data.startswith('игрок в старт '):
                    phases = ('players',)
                elif event.data == 'начать игру':
                    phases = (game.phase,)
                else:
                    phases = ('playing',)
                if game.phase not in phases:
                    await event.answer('Эта кнопка относится к другому этапу игры. Используйте /resume_game.', show_alert=True)
                    return
            try:
                return await handler(event, data)
            except Exception:
                try:
                    saved = await load_active_games_db()
                    if chat_id in saved:
                        games[chat_id] = GameState(**saved[chat_id])
                    else:
                        games.pop(chat_id, None)
                except Exception:
                    if before is None:
                        games.pop(chat_id, None)
                    else:
                        games[chat_id] = before
                raise
