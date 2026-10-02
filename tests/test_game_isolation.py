import importlib.util
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot
import pandas
import aiogram.types
import aiogram.fsm.context

from utils.game_state import games, get_game


def load_game_utils(source=None):
    keyboards = ModuleType('keyboards')
    for name in (
        'input_player_game_kb', 'start_game_kb', 'game_keyboards',
        'purchase_players_keyboards', 'exit_players_keyboards', 'main_kb',
        'game_admin_keyboards', 'change_purchase_players_keyboards',
        'back_players_keyboards', 'extra_players_keyboards',
    ):
        setattr(keyboards, name, AsyncMock(return_value=None))
    create_bot = ModuleType('create_bot')
    create_bot.bot = SimpleNamespace(send_photo=AsyncMock())
    services = ModuleType('services')
    services.create_game_db = AsyncMock()
    services.get_players_db = AsyncMock()
    services.update_game_db = AsyncMock()
    path = Path(__file__).resolve().parents[1] / 'utils' / 'game_utils.py'
    spec = importlib.util.spec_from_file_location('isolated_game_utils', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict('sys.modules', {
        'keyboards': keyboards, 'create_bot': create_bot, 'services': services,
    }):
        if source is None:
            spec.loader.exec_module(module)
        else:
            exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


game_utils = load_game_utils()


def callback(chat_id, data=''):
    return SimpleNamespace(
        data=data,
        message=SimpleNamespace(chat=SimpleNamespace(id=chat_id), answer=AsyncMock()),
        from_user=SimpleNamespace(id=123),
    )


class GameIsolationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        games.clear()
        game_utils.bot.send_photo.reset_mock()
        game_utils.create_game_db.reset_mock()
        game_utils.update_game_db.reset_mock()
        for chat_id, player, count in ((10, 'Alice', 2), (20, 'Bob', 5)):
            game_utils.player_input(chat_id, 'новая игра')
            game_utils.player_input(chat_id, player)
            get_game(chat_id).count = count

    async def test_starting_games_keeps_players_and_coefficients_separate(self):
        await game_utils.start_game(callback(10))
        await game_utils.start_game(callback(20))
        self.assertEqual(get_game(10).game_data['Alice']['Закуп,руб.'], 2000)
        self.assertEqual(get_game(20).game_data['Bob']['Закуп,руб.'], 5000)
        self.assertNotIn('Bob', get_game(10).game_data)
        self.assertNotIn('Alice', get_game(20).game_data)

    async def test_reset_clears_all_fields_only_in_selected_chat(self):
        first = get_game(10)
        first.start_status = True
        first.player_out_list.append('Carol')
        first.out_player = 'Carol'
        first.add_bank_player = 'Alice'
        first.game_id = 42
        game_utils.player_input(10, 'новая игра')
        reset = get_game(10)
        self.assertFalse(reset.start_status)
        self.assertEqual(reset.player_out_list, [])
        self.assertEqual(reset.player_list, [])
        self.assertEqual(reset.out_player, '')
        self.assertEqual(reset.add_bank_player, '')
        self.assertEqual(reset.game_id, 0)
        self.assertEqual(get_game(20).player_list, ['Bob'])
        self.assertEqual(get_game(20).count, 5)

    async def test_purchase_selection_does_not_leak_to_other_chat(self):
        await game_utils.start_game(callback(10))
        await game_utils.start_game(callback(20))
        await game_utils.update_add_on_player(callback(10, 'закуп Alice'))
        await game_utils.update_add_on_player(callback(20, 'закуп Bob'))
        await game_utils.add_on_utils(callback(10, 'фишки 500'))
        self.assertEqual(get_game(10).game_data['Alice']['Закуп,фш.'], 1500)
        self.assertEqual(get_game(20).game_data['Bob']['Закуп,фш.'], 1000)

    async def test_finishing_one_chat_updates_only_its_database_game(self):
        await game_utils.start_game(callback(10))
        await game_utils.start_game(callback(20))
        get_game(10).start_status = True
        get_game(10).game_id = 101
        get_game(20).start_status = True
        await game_utils.game_end_start(callback(10))
        message = SimpleNamespace(
            chat=SimpleNamespace(id=10), text='1200',
            from_user=SimpleNamespace(id=123), answer=AsyncMock(),
        )
        await game_utils.result_chips(message, SimpleNamespace(clear=AsyncMock()))
        game_utils.update_game_db.assert_awaited_once_with(get_game(10).game_data, 101)
        self.assertEqual(get_game(10).game_data['Alice']['Руб.'], 400)
        self.assertTrue(get_game(20).start_status)
        self.assertEqual(get_game(20).player_list, ['Bob'])
        self.assertEqual(get_game(20).game_data['Bob']['Статус'], 'В игре')

    async def test_rendered_images_are_independent_png_uploads(self):
        await game_utils.start_game(callback(10))
        await game_utils.start_game(callback(20))
        text_a, image_a = await game_utils.text_game(10)
        saved_a = image_a.data
        text_b, image_b = await game_utils.text_game(20)
        self.assertIn('1 к 2', text_a)
        self.assertIn('1 к 5', text_b)
        self.assertTrue(saved_a.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertTrue(image_b.data.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertNotEqual(saved_a, image_b.data)
        self.assertEqual(image_a.data, saved_a)

    async def test_database_ids_and_start_flags_belong_to_each_chat(self):
        await game_utils.start_game(callback(10))
        await game_utils.start_game(callback(20))
        game_utils.create_game_db.side_effect = [('02.10.2026', 101), ('03.10.2026', 202)]
        await game_utils.game_utils(callback(10))
        self.assertFalse(get_game(20).start_status)
        await game_utils.game_utils(callback(20))
        self.assertEqual(get_game(10).game_id, 101)
        self.assertEqual(get_game(20).game_id, 202)
        self.assertEqual(get_game(10).date, '02.10.2026')
        self.assertEqual(get_game(20).date, '03.10.2026')
        game_utils.create_game_db.side_effect = None
