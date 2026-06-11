import logging
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from backend.config import settings


class DBConnect:
    logger = logging.getLogger('web_app.db_connect.DBConnect')

    @classmethod
    def _create_connect(cls):
        return psycopg.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )

    @classmethod
    @contextmanager
    def get_cursor(cls, dict_rows: bool = False):
        with DBConnect._create_connect() as conn:
            kwargs = {"row_factory": dict_row} if dict_rows else {}
            try:
                with conn.cursor(**kwargs) as cur:
                    yield cur
                    conn.commit()
            except Exception as ex:
                conn.rollback()
                raise Exception("Database error") from ex
