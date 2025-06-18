# backend/test/conftest.py
import os
import pytest
import sqlite3
from backend.app.models.db import init_menus_db, init_orders_db, get_db_connection


@pytest.fixture(scope="session", autouse=True)
def setup_memory_db():
    os.environ["PYTEST_RUNNING"] = "1"  # テスト実行中のフラグを設定    
    conn = get_db_connection()  # メモリ内データベースを取得
    init_menus_db()
    init_orders_db()
    yield

    conn.close() # テスト後に接続を閉じる

