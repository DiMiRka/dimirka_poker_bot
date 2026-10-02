import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from decouple import Config, RepositoryEmpty
from sqlalchemy.engine import make_url

from db.config import get_database_url


class DatabaseConfigTests(unittest.TestCase):
    def setUp(self):
        self.config = patch('db.config.config', Config(RepositoryEmpty()))
        self.config.start()
        self.addCleanup(self.config.stop)

    def test_local_run_uses_pg_link(self):
        url = 'postgresql+asyncpg://local_user:local_password@localhost:5432/local_db'
        with patch.dict(os.environ, {'PG_LINK': url}, clear=True):
            self.assertEqual(get_database_url(), url)

    def test_container_uses_postgres_settings_instead_of_local_pg_link(self):
        with patch.dict(os.environ, {
            'PG_LINK': 'postgresql+asyncpg://local:password@localhost/local_db',
            'PG_HOST': 'db', 'POSTGRES_USER': 'docker_user',
            'POSTGRES_PASSWORD': 'docker_password', 'POSTGRES_DB': 'docker_db',
        }, clear=True):
            url = make_url(get_database_url())
        self.assertEqual(url.host, 'db')
        self.assertEqual(url.port, 5432)
        self.assertEqual(url.username, 'docker_user')
        self.assertEqual(url.password, 'docker_password')
        self.assertEqual(url.database, 'docker_db')

    def test_password_special_characters_survive_url_encoding(self):
        password = 'p@ss:/%#word'
        with patch.dict(os.environ, {
            'PG_HOST': 'db', 'POSTGRES_PASSWORD': password,
        }, clear=True):
            url = make_url(get_database_url())
        self.assertEqual(url.password, password)
        self.assertEqual(url.username, 'poker_user')
        self.assertEqual(url.database, 'poker_db')

    def test_custom_port_is_parsed_as_integer(self):
        with patch.dict(os.environ, {
            'PG_HOST': 'db', 'PG_PORT': '5433', 'POSTGRES_PASSWORD': 'test_password',
        }, clear=True):
            self.assertEqual(make_url(get_database_url()).port, 5433)

    def test_alembic_generates_migrations_offline_with_encoded_password(self):
        environment = dict(os.environ, PG_HOST='',
                           PG_LINK='postgresql+asyncpg://test_user:p%40ss%25word@localhost/test_db')
        result = subprocess.run(
            [sys.executable, '-m', 'alembic', 'upgrade', 'head', '--sql'],
            cwd=Path(__file__).resolve().parents[1], env=environment,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for table in ('games', 'players', 'game_player', 'active_games'):
            self.assertIn(f'CREATE TABLE {table}', result.stdout)
