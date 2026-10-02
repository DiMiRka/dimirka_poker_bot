import importlib.util
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models.game import ActiveGame, Base, Game
from repositories.active_game import ActiveGameRepository


class ActiveGameRepositoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)

        @asynccontextmanager
        async def session():
            with Session(self.engine) as sql_session:
                proxy = SimpleNamespace(
                    execute=AsyncMock(side_effect=sql_session.execute),
                    add=sql_session.add,
                    flush=AsyncMock(side_effect=sql_session.flush),
                )
                try:
                    yield proxy
                    sql_session.commit()
                except Exception:
                    sql_session.rollback()
                    raise

        database = ModuleType('db.database')
        database.db = SimpleNamespace(session=session)
        path = Path(__file__).resolve().parents[1] / 'services' / 'game.py'
        spec = importlib.util.spec_from_file_location('isolated_persistent_game_services', path)
        self.services = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'db.database': database}):
            spec.loader.exec_module(self.services)

    async def test_upsert_load_and_delete_preserve_separate_chats(self):
        await self.services.save_active_game_db(-1001234567890, {'phase': 'players', 'count': 2})
        await self.services.save_active_game_db(20, {'phase': 'playing', 'count': 5})
        await self.services.save_active_game_db(-1001234567890, {'phase': 'ready', 'count': 3})
        self.assertEqual(await self.services.load_active_games_db(), {
            -1001234567890: {'phase': 'ready', 'count': 3},
            20: {'phase': 'playing', 'count': 5},
        })
        async with self.services.db.session() as session:
            await ActiveGameRepository(session).delete(-1001234567890)
        self.assertEqual(await self.services.load_active_games_db(), {
            20: {'phase': 'playing', 'count': 5},
        })

    async def test_creation_and_completion_use_database_transactions(self):
        date, game_id = await self.services.create_game_db(2, 10, {'phase': 'ready'})
        saved = await self.services.load_active_games_db()
        self.assertEqual(saved[10]['game_id'], game_id)
        self.assertEqual(saved[10]['date'], date)
        self.assertEqual(saved[10]['phase'], 'playing')
        results = {'Alice': {'Руб.': 500}}
        await self.services.finish_game_db(10, results, game_id)
        self.assertEqual(await self.services.load_active_games_db(), {})
        with Session(self.engine) as session:
            self.assertEqual(session.get(Game, game_id).game, results)

    async def test_failed_snapshot_save_rolls_back_new_game_row(self):
        with patch.object(ActiveGameRepository, 'save', AsyncMock(side_effect=RuntimeError('write failed'))):
            with self.assertRaises(RuntimeError):
                await self.services.create_game_db(2, 10, {'phase': 'ready'})
        with Session(self.engine) as session:
            self.assertEqual(session.scalars(select(Game)).all(), [])
            self.assertEqual(session.scalars(select(ActiveGame)).all(), [])

    async def test_failed_cleanup_rolls_back_final_results(self):
        _, game_id = await self.services.create_game_db(2, 10, {'phase': 'ready'})
        with patch.object(ActiveGameRepository, 'delete', AsyncMock(side_effect=RuntimeError('delete failed'))):
            with self.assertRaises(RuntimeError):
                await self.services.finish_game_db(10, {'Alice': {'Руб.': 500}}, game_id)
        with Session(self.engine) as session:
            self.assertEqual(session.get(Game, game_id).game, {})
            self.assertIsNotNone(session.get(ActiveGame, 10))
