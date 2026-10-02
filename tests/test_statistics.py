import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from utils.statistics import calculate_statistics
from tests.test_table_rendering import load_statistics


class StatisticsTests(unittest.TestCase):
    def test_no_games_returns_empty_statistics(self):
        self.assertEqual(calculate_statistics([]), {})

    def test_games_without_players_return_empty_statistics(self):
        self.assertEqual(calculate_statistics([{}, {}]), {})

    def test_single_game_classifies_win_loss_and_draw(self):
        for earned, win, loss, draw, winrate in (
            (500, 1, 0, 0, '100.0 %'),
            (-500, 0, 1, 0, '0.0 %'),
            (0, 0, 0, 1, '0.0 %'),
        ):
            with self.subTest(earned=earned):
                self.assertEqual(calculate_statistics([{'Alice': {'Руб.': earned}}]), {
                    'Alice': {'games': 1, 'win': win, 'loss': loss, 'draw': draw,
                              'earned': earned, 'winrate': winrate},
                })

    def test_multiple_games_accumulate_counts_and_net_earnings(self):
        games = [{'Alice': {'Руб.': earned}} for earned in (1000, -700, 0, 200)]
        self.assertEqual(calculate_statistics(games), {
            'Alice': {'games': 4, 'win': 2, 'draw': 1, 'loss': 1,
                      'earned': 500, 'winrate': '50.0 %'},
        })

    def test_players_are_counted_only_in_games_they_played(self):
        games = [
            {'Alice': {'Руб.': 500}, 'Bob': {'Руб.': -500}},
            {'Bob': {'Руб.': 200}, 'Carol': {'Руб.': -200}},
            {},
            {'Alice': {'Руб.': 0}},
        ]
        self.assertEqual(calculate_statistics(games), {
            'Alice': {'games': 2, 'win': 1, 'draw': 1, 'loss': 0,
                      'earned': 500, 'winrate': '50.0 %'},
            'Bob': {'games': 2, 'win': 1, 'draw': 0, 'loss': 1,
                    'earned': -300, 'winrate': '50.0 %'},
            'Carol': {'games': 1, 'win': 0, 'draw': 0, 'loss': 1,
                      'earned': -200, 'winrate': '0.0 %'},
        })

    def test_winrate_rounds_repeating_percentages(self):
        games = [
            {'Alice': {'Руб.': 1}, 'Bob': {'Руб.': -1}},
            {'Alice': {'Руб.': -1}, 'Bob': {'Руб.': 1}},
            {'Alice': {'Руб.': -1}, 'Bob': {'Руб.': 1}},
        ]
        result = calculate_statistics(games)
        self.assertEqual(result['Alice']['winrate'], '33.33 %')
        self.assertEqual(result['Bob']['winrate'], '66.67 %')

    def test_recalculation_is_stable_and_does_not_change_source_games(self):
        games = [{'Alice': {'Руб.': 100, 'Фишки': 1100, 'Статус': 'Вышел'}}]
        before = deepcopy(games)
        first = calculate_statistics(games)
        first['Alice']['earned'] = 9999
        self.assertEqual(calculate_statistics(games)['Alice']['earned'], 100)
        self.assertEqual(games, before)

    def test_game_order_does_not_affect_totals(self):
        games = [
            {'Alice': {'Руб.': 300}},
            {'Alice': {'Руб.': -100}, 'Bob': {'Руб.': 100}},
            {'Bob': {'Руб.': 0}},
        ]
        self.assertEqual(calculate_statistics(games), calculate_statistics(list(reversed(games))))


class StatisticsUpdateTests(unittest.IsolatedAsyncioTestCase):
    async def test_calculated_totals_are_saved_and_image_is_sorted_by_earnings(self):
        statistics = load_statistics()
        statistics.get_result_games_db.return_value = [
            {'Alice': {'Руб.': 100}, 'Bob': {'Руб.': -100}},
            {'Alice': {'Руб.': 0}},
        ]
        statistics.get_players_db.return_value = [
            SimpleNamespace(login='Bob', games=1, win=0, draw=0, loss=1,
                            winrate='0.0 %', earned=-100),
            SimpleNamespace(login='Alice', games=2, win=1, draw=1, loss=0,
                            winrate='50.0 %', earned=100),
        ]
        with patch.object(statistics, 'render_table', AsyncMock(return_value=b'image')) as render:
            photo = await statistics.update_player_statistics()
        statistics.update_player_db.assert_awaited_once_with({
            'Alice': {'games': 2, 'win': 1, 'draw': 1, 'loss': 0,
                      'earned': 100, 'winrate': '50.0 %'},
            'Bob': {'games': 1, 'win': 0, 'draw': 0, 'loss': 1,
                    'earned': -100, 'winrate': '0.0 %'},
        })
        render.assert_awaited_once_with({
            'Игрок': ['Alice', 'Bob'], 'Игр': [2, 1], 'Побед': [1, 0],
            'В ноль': [1, 0], 'Проёб': [0, 1], 'Винрейт': ['50.0 %', '0.0 %'],
            'Результат': ['100 руб.', '-100 руб.'],
        }, size=(8, 8))
        self.assertEqual(photo.data, b'image')
        self.assertEqual(photo.filename, 'statistics.png')
