import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

from tests.test_game_isolation import game_utils
from utils.game_state import games, get_game


def _load_handlers():
    keyboards = ModuleType('keyboards')
    keyboards.make_count = AsyncMock()
    keyboards.purchase = AsyncMock()
    path = Path(__file__).resolve().parents[1] / 'handlers' / 'game.py'
    spec = importlib.util.spec_from_file_location('isolated_game_handlers', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict('sys.modules', {
        'keyboards': keyboards, 'utils.game_utils': game_utils,
    }):
        spec.loader.exec_module(module)
    return module


handlers = _load_handlers()


class GameInputTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        games.clear()
        self.game = get_game(10)
        self.game.count = 2
        self.game.game_id = 101
        self.game.out_player = 'Alice'
        self.game.add_bank_player = 'Alice'
        self.game.game_data = {
            'Alice': {'Закуп,фш.': 1000, 'Закуп,руб.': 2000, 'Статус': 'В игре', 'Фишки': 0, 'Руб.': 0},
        }
        self.state = SimpleNamespace(clear=AsyncMock())
        game_utils.bot.send_photo.reset_mock()
        game_utils.update_game_db.reset_mock()
        self.render = patch.object(game_utils, '_text_game', AsyncMock(return_value=('Игра', b'image')))
        self.render.start()
        self.addCleanup(self.render.stop)

    def _message(self, text):
        return SimpleNamespace(
            text=text, chat=SimpleNamespace(id=10), from_user=SimpleNamespace(id=123),
            answer=AsyncMock(),
        )

    async def test_invalid_exit_input_keeps_state_and_results_in_both_modes(self):
        for started in (True, False):
            for text in ('abc', '12.5', '-1', '', None):
                with self.subTest(started=started, text=text):
                    self.game.start_status = started
                    before = deepcopy(self.game)
                    message = self._message(text)
                    await game_utils.result_chips(message, self.state)
                    self.assertEqual(self.game, before)
                    self.state.clear.assert_not_awaited()
                    game_utils.update_game_db.assert_not_awaited()
                    game_utils.bot.send_photo.assert_not_awaited()
                    message.answer.assert_awaited_once()

    async def test_valid_exit_after_mistake_uses_same_player_and_allows_zero(self):
        self.game.start_status = True
        await game_utils.result_chips(self._message('ошибка'), self.state)
        self.state.clear.assert_not_awaited()
        await game_utils.result_chips(self._message(' 0 '), self.state)
        result = self.game.game_data['Alice']
        self.assertEqual(result['Статус'], 'Вышел')
        self.assertEqual(result['Фишки'], 0)
        self.assertEqual(result['Руб.'], -2000)
        self.state.clear.assert_awaited_once()
        game_utils.update_game_db.assert_not_awaited()

    async def test_finishing_game_moves_to_next_player_without_clearing_fsm(self):
        self.game.start_status = False
        self.game.player_list = ['Bob']
        message = self._message('1500')
        await game_utils.result_chips(message, self.state)
        self.assertEqual(self.game.game_data['Alice']['Руб.'], 1000)
        self.assertEqual(self.game.out_player, 'Bob')
        self.assertEqual(self.game.player_list, [])
        self.state.clear.assert_not_awaited()
        game_utils.update_game_db.assert_not_awaited()
        message.answer.assert_awaited_once_with(text='Bob на кармане:')

    async def test_finishing_last_player_saves_results_and_clears_fsm(self):
        self.game.start_status = False
        await game_utils.result_chips(self._message('1250'), self.state)
        self.assertEqual(self.game.game_data['Alice']['Фишки'], 1250)
        self.assertEqual(self.game.game_data['Alice']['Руб.'], 500)
        game_utils.update_game_db.assert_awaited_once_with(self.game.game_data, 101)
        self.state.clear.assert_awaited_once()

    async def test_invalid_purchase_input_keeps_data_and_fsm(self):
        for text in ('abc', '12.5', '-1', '', None):
            with self.subTest(text=text):
                before = deepcopy(self.game)
                message = self._message(text)
                await handlers._change_purchase(message, self.state)
                self.assertEqual(self.game, before)
                self.state.clear.assert_not_awaited()
                game_utils.bot.send_photo.assert_not_awaited()
                message.answer.assert_awaited_once()

    async def test_valid_purchase_after_mistake_updates_amount_and_clears_fsm(self):
        await handlers._change_purchase(self._message('ошибка'), self.state)
        self.state.clear.assert_not_awaited()
        await handlers._change_purchase(self._message(' 1500 '), self.state)
        self.assertEqual(self.game.game_data['Alice']['Закуп,фш.'], 1500)
        self.assertEqual(self.game.game_data['Alice']['Закуп,руб.'], 3000)
        self.state.clear.assert_awaited_once()

    async def test_zero_purchase_is_valid(self):
        await handlers._change_purchase(self._message('0'), self.state)
        self.assertEqual(self.game.game_data['Alice']['Закуп,фш.'], 0)
        self.assertEqual(self.game.game_data['Alice']['Закуп,руб.'], 0)
        self.state.clear.assert_awaited_once()
