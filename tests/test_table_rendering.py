import asyncio
import importlib.util
import threading
import unittest
from io import BytesIO
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

from PIL import Image
from matplotlib.figure import Figure

from tests.test_game_isolation import game_utils
from utils.game_state import games, get_game
from utils import table_image


def load_statistics(source=None):
    services = ModuleType('services')
    services.get_result_games_db = AsyncMock(return_value=[])
    services.update_player_db = AsyncMock()
    services.get_players_db = AsyncMock(return_value=[SimpleNamespace(
        login='Alice', games=1, win=1, draw=0, loss=0, winrate='100 %', earned=100,
    )])
    services.get_games_db = AsyncMock()
    keyboards = ModuleType('keyboards')
    keyboards.last_game_kb = AsyncMock()
    path = Path(__file__).resolve().parents[1] / 'utils' / 'statistic_utils.py'
    spec = importlib.util.spec_from_file_location('isolated_statistics', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict('sys.modules', {'services': services, 'keyboards': keyboards}):
        if source is None:
            spec.loader.exec_module(module)
        else:
            exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


statistics = load_statistics()


class TableRenderingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        games.clear()
        self.results = {
            'Alice': {'Закуп,фш.': 1000, 'Закуп,руб.': 1000, 'Статус': 'В игре', 'Фишки': 0, 'Руб.': 0},
        }
        get_game(10).game_data = self.results
        get_game(10).count = 1

    async def assert_loop_runs_during_render(self, operation):
        loop = asyncio.get_running_loop()
        released = threading.Event()
        observations = []
        main_thread = threading.get_ident()
        original = Figure.savefig

        def savefig(figure, *args, **kwargs):
            loop.call_soon_threadsafe(released.set)
            observations.append((threading.get_ident(), released.wait(timeout=1)))
            return original(figure, *args, **kwargs)

        with patch.object(Figure, 'savefig', savefig):
            await operation()
        self.assertEqual(len(observations), 1)
        self.assertNotEqual(observations[0][0], main_thread)
        self.assertTrue(observations[0][1], 'Event loop was blocked during rendering')

    async def test_current_game_does_not_block_event_loop(self):
        await self.assert_loop_runs_during_render(lambda: game_utils.text_game(10))

    async def test_statistics_does_not_block_event_loop(self):
        await self.assert_loop_runs_during_render(statistics.update_player_statistics)

    async def test_past_game_does_not_block_event_loop(self):
        game = {'date': '02.10.2026', 'count': 1, 'game': self.results}
        await self.assert_loop_runs_during_render(lambda: statistics.get_last_game(game))

    async def test_concurrent_requests_return_valid_independent_images(self):
        active = 0
        maximum = 0
        original = Figure.savefig

        def savefig(figure, *args, **kwargs):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            try:
                return original(figure, *args, **kwargs)
            finally:
                active -= 1

        game = {'date': '02.10.2026', 'count': 1, 'game': self.results}
        with patch.object(Figure, 'savefig', savefig):
            current, stats, past = await asyncio.gather(
                game_utils.text_game(10), statistics.update_player_statistics(),
                statistics.get_last_game(game),
            )
        self.assertEqual(maximum, 1)
        for photo in (current[1], stats, past[1]):
            with Image.open(BytesIO(photo.data)) as image:
                self.assertEqual(image.format, 'PNG')
                image.verify()
        self.assertNotEqual(current[1].data, stats.data)
        self.assertEqual(current[1].data, past[1].data)

    async def test_worker_uses_snapshot_when_game_changes(self):
        loop = asyncio.get_running_loop()
        entered = asyncio.Event()
        released = threading.Event()
        captured = []

        def render(data, size):
            loop.call_soon_threadsafe(entered.set)
            if not released.wait(timeout=2):
                raise TimeoutError('Test worker was not released')
            captured.append(data['Закуп,руб.'][0])
            return b'image'

        with patch.object(table_image, '_render_table', render):
            task = asyncio.create_task(game_utils.text_game(10))
            try:
                await asyncio.wait_for(entered.wait(), timeout=2)
                self.results['Alice']['Закуп,руб.'] = 2000
                released.set()
                await task
            finally:
                released.set()
                await task
        self.assertEqual(captured, [1000])
