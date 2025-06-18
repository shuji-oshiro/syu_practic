import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")
DB_PATH = os.getenv("DB_PATH")
    
print(f"--DB_PATH--: {DB_PATH}")

def init_menus_db():
    if not DB_PATH:
        raise ValueError("DB_PATH is not set in the environment variables.")
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT,
            search_text TEXT NOT NULL
        )
        """)
    except sqlite3.OperationalError as e:
        print(f"Error initializing menus database: {e}")
    finally:
        conn.commit()
        conn.close()

def init_orders_db():
    if not DB_PATH:
        raise ValueError("DB_PATH is not set in the environment variables.")    
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date INTEGER NOT NULL,
            seat_id TEXT NOT NULL,
            menu_id INTEGER NOT NULL,
            order_cnt INTEGER NOT NULL
        )
        """)
    except sqlite3.OperationalError as e:
        print(f"Error initializing orders database: {e}")
        sys.exit(1)
    finally:
        conn.commit()
        conn.close()

def get_db_connection():  
    # テスト実行中の場合はメモリ内データベースを使用
    if os.getenv("PYTEST_RUNNING") == "1":
        return sqlite3.connect(
            "file:memdb1?mode=memory&cache=shared", uri=True, check_same_thread=False
        )

    if not DB_PATH:
        raise ValueError("DB_PATH is not set in the environment variables.")
    
    return sqlite3.connect(DB_PATH)
