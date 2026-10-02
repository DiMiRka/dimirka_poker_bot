import asyncio
import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch
from aiogram.types import CallbackQuery

from tests.test_game_isolation import game_utils, _callback
from tests.test_game_input import handlers
from utils.game_fsm import ChangePurchase, ResultGame
from utils.game_state import games, get_game, game_snapshot, restore_games


class GamePersistenceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        games.clear()
        self.saved = {}
        self.completed = {}
        self.state = SimpleNamespace(clear=AsyncMock(), set_state=AsyncMock(), get_state=AsyncMock(return_value=None))

        async def save(chat_id, state):
            self.saved[chat_id] = deepcopy(state)

        async def create(count, chat_id, state):
            self.saved[chat_id] = dict(deepcopy(state), date='02.10.2026', game_id=101,
                                       phase='playing', start_status=True)
            return '02.10.2026', 101

        async def finish(chat_id, results, game_id):
            self.completed[game_id] = deepcopy(results)
            self.saved.pop(chat_id, None)

        for name, replacement in {
            'save_active_game_db': AsyncMock(side_effect=save),
            'create_game_db': AsyncMock(side_effect=create),
            'finish_game_db': AsyncMock(side_effect=finish),
            'get_players_db': AsyncMock(return_value=[SimpleNamespace(login='Alice')]),
            '_text_game': AsyncMock(return_value=('Игра', b'image')),
        }.items():
            patcher = patch.object(game_utils, name, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _message(self, text='/resume_game', user_id=123, chat_id=10):
        return SimpleNamespace(text=text, chat=SimpleNamespace(id=chat_id),
                               from_user=SimpleNamespace(id=user_id), answer=AsyncMock())

    def _restart(self):
        restore_games(deepcopy(self.saved))
        self.state = SimpleNamespace(clear=AsyncMock(), set_state=AsyncMock(), get_state=AsyncMock(return_value=None))

    async def _start_game(self):
        await game_utils.begin_game(self._message('/start_game'), self.state)
        await game_utils.update_count(10, 2)
        await game_utils.input_players_start(_callback(10, 'игрок в старт Alice'))
        await game_utils.start_game(_callback(10))
        await game_utils.game_utils(_callback(10))

    async def test_preparation_stages_survive_restart(self):
        await game_utils.begin_game(self._message('/start_game'), self.state)
        self._restart()
        self.assertEqual(get_game(10).phase, 'coefficient')
        await game_utils.resume_game(self._message(), self.state)
        await game_utils.update_count(10, 2)
        await game_utils.input_players_start(_callback(10, 'игрок в старт Alice'))
        self._restart()
        self.assertEqual(get_game(10).player_list, ['Alice'])
        self.assertEqual(get_game(10).phase, 'players')
        await game_utils.start_game(_callback(10))
        self._restart()
        self.assertEqual(get_game(10).phase, 'ready')
        await game_utils.resume_game(self._message(), self.state)
        game_utils.create_game_db.assert_not_awaited()

    async def test_purchase_and_running_game_survive_restart_without_duplicate_game(self):
        await self._start_game()
        await game_utils.update_add_on_player(_callback(10, 'закуп Alice'))
        self._restart()
        await game_utils.resume_game(self._message(), self.state)
        await game_utils.add_on_utils(_callback(10, 'фишки 500'))
        self._restart()
        self.assertEqual(get_game(10).game_data['Alice']['Закуп,фш.'], 1500)
        self.assertEqual(get_game(10).pending_action, '')
        await game_utils.resume_game(self._message(), self.state)
        game_utils.create_game_db.assert_awaited_once()
        self.assertEqual(get_game(10).game_id, 101)

    async def test_exit_question_and_selected_player_survive_restart(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        self._restart()
        message = self._message()
        await game_utils.resume_game(message, self.state)
        self.state.set_state.assert_awaited_once_with(ResultGame.result_bank)
        message.answer.assert_awaited_once_with('Alice на кармане:')
        await game_utils.result_chips(self._message('1250'), self.state)
        self._restart()
        self.assertEqual(get_game(10).game_data['Alice']['Руб.'], 500)
        self.assertEqual(get_game(10).pending_action, '')

    async def test_purchase_correction_question_survives_restart(self):
        await self._start_game()
        await game_utils.update_change_on_player(_callback(10, 'поменять Alice'))
        self._restart()
        await game_utils.resume_game(self._message(), self.state)
        self.state.set_state.assert_awaited_once_with(ChangePurchase.change)
        await game_utils.change_purchase_utils(self._message('2000'))
        self._restart()
        self.assertEqual(get_game(10).game_data['Alice']['Закуп,руб.'], 4000)
        self.assertEqual(get_game(10).pending_action, '')

    async def test_finishing_game_survives_restart_and_removes_active_record(self):
        await self._start_game()
        await game_utils.input_players_game(_callback(10, 'игрок в игру Bob'))
        await game_utils.game_end_start(_callback(10))
        self._restart()
        self.assertEqual(get_game(10).phase, 'finishing')
        await game_utils.result_chips(self._message('1500'), self.state)
        self._restart()
        self.assertEqual(get_game(10).out_player, 'Bob')
        self.assertEqual(get_game(10).game_data['Alice']['Руб.'], 1000)
        await game_utils.resume_game(self._message(), self.state)
        await game_utils.result_chips(self._message('500'), self.state)
        self.assertEqual(self.completed[101]['Bob']['Руб.'], -1000)
        self.assertNotIn(10, self.saved)
        self._restart()
        self.assertNotIn(10, games)

    async def test_new_game_does_not_replace_unfinished_game(self):
        await self._start_game()
        before = game_snapshot(10)
        await game_utils.begin_game(self._message('/start_game'), self.state)
        self.assertEqual(game_snapshot(10), before)
        self.assertEqual(self.saved[10], before)

    async def test_other_user_cannot_resume_pending_input(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        self._restart()
        await game_utils.resume_game(self._message(user_id=999), self.state)
        self.state.clear.assert_not_awaited()
        self.state.set_state.assert_not_awaited()

    async def test_invalid_input_does_not_change_saved_snapshot(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        before = deepcopy(self.saved)
        await game_utils.result_chips(self._message('не число'), self.state)
        self.assertEqual(self.saved, before)

    async def test_returned_player_remains_in_active_list_after_restart(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        await game_utils.result_chips(self._message('1000'), self.state)
        await game_utils.game_back_player_end(_callback(10, 'вернуть Alice'))
        self._restart()
        self.assertEqual(get_game(10).player_list, ['Alice'])
        self.assertEqual(get_game(10).player_out_list, [])

    async def test_finish_when_all_players_have_already_left(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        await game_utils.result_chips(self._message('1000'), self.state)
        self.assertFalse(await game_utils.game_end_start(_callback(10)))
        self.assertNotIn(10, self.saved)
        self.assertIn(101, self.completed)

    async def test_middleware_restores_raw_fsm_state_before_filters(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        self._restart()
        middleware = handlers.GamePersistenceMiddleware()
        data = {'state': self.state, 'raw_state': None}
        handler = AsyncMock()
        await middleware(handler, self._message('1250'), data)
        self.assertEqual(data['raw_state'], ResultGame.result_bank.state)
        handler.assert_awaited_once()

    async def test_middleware_serializes_operations_for_same_chat(self):
        await self._start_game()
        middleware = handlers.GamePersistenceMiddleware()
        active = 0
        maximum = 0

        async def handler(event, data):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0)
            active -= 1

        await asyncio.gather(*(middleware(handler, self._message(), {}) for _ in range(3)))
        self.assertEqual(maximum, 1)

    async def test_database_failure_restores_memory_and_does_not_confirm_change(self):
        await self._start_game()
        before = deepcopy(self.saved[10])
        middleware = handlers.GamePersistenceMiddleware()

        async def handler(event, data):
            await game_utils.update_count(10, 5)
            await event.answer('Сохранено')

        message = self._message()
        with patch.object(game_utils, 'save_active_game_db', AsyncMock(side_effect=RuntimeError('DB unavailable'))):
            with patch.dict(middleware.__call__.__globals__, {
                'load_active_games_db': AsyncMock(return_value=deepcopy(self.saved)),
            }):
                with self.assertRaises(RuntimeError):
                    await middleware(handler, message, {})
        self.assertEqual(game_snapshot(10), before)
        message.answer.assert_not_awaited()

    async def test_startup_restores_games_and_keeps_pending_telegram_updates(self):
        await self._start_game()
        before = deepcopy(self.saved)
        games.clear()
        create_bot = ModuleType('create_bot')
        create_bot.bot = SimpleNamespace(set_my_commands=AsyncMock(), delete_webhook=AsyncMock())
        create_bot.dp = SimpleNamespace()
        services = ModuleType('services')
        services.load_active_games_db = AsyncMock(return_value=before)
        mocks = {'create_bot': create_bot, 'services': services}
        for name, attribute in (
            ('handlers.start', 'start_router'), ('handlers.game', 'game_router'),
            ('handlers.player', 'player_router'), ('handlers.player_statistics', 'statistics_router'),
        ):
            module = ModuleType(name)
            setattr(module, attribute, object())
            mocks[name] = module
        path = Path(__file__).resolve().parents[1] / 'aiogram_run.py'
        spec = importlib.util.spec_from_file_location('isolated_bot_runtime', path)
        runtime = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', mocks):
            spec.loader.exec_module(runtime)
        with patch('builtins.print'):
            await runtime._on_startup()
        self.assertEqual(game_snapshot(10), before[10])
        create_bot.bot.delete_webhook.assert_awaited_once_with(drop_pending_updates=False)
        commands = create_bot.bot.set_my_commands.call_args.args[0]
        self.assertIn('resume_game', [command.command for command in commands])

    async def test_old_preparation_button_cannot_reset_running_game(self):
        await self._start_game()
        before = game_snapshot(10)
        event = CallbackQuery.model_construct(
            id='test', from_user=SimpleNamespace(id=123), chat_instance='test',
            message=self._message('Игра'), data='стартуем',
        )
        handler = AsyncMock()
        with patch.object(CallbackQuery, 'answer', AsyncMock()) as answer:
            await handlers.GamePersistenceMiddleware()(handler, event, {})
        handler.assert_not_awaited()
        answer.assert_awaited_once()
        self.assertEqual(game_snapshot(10), before)

    async def test_finished_game_rejects_old_buttons(self):
        get_game(10).phase = 'finished'
        event = CallbackQuery.model_construct(
            id='test', from_user=SimpleNamespace(id=123), chat_instance='test',
            message=self._message('Игра'), data='битва',
        )
        handler = AsyncMock()
        with patch.object(CallbackQuery, 'answer', AsyncMock()):
            await handlers.GamePersistenceMiddleware()(handler, event, {})
        handler.assert_not_awaited()

    async def test_pending_operation_rejects_other_user_before_mutation(self):
        await self._start_game()
        await game_utils.player_out_game(_callback(10, 'выход Alice'))
        handler = AsyncMock()
        await handlers.GamePersistenceMiddleware()(handler, self._message('1000', user_id=999), {})
        handler.assert_not_awaited()
        self.assertEqual(get_game(10).pending_action, 'result')
