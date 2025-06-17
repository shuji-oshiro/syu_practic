import time
import sqlite3
from typing import List
from backend.app.models.db import get_db_connection
from backend.app.schemas.order_schema import OrderIn, OrderOut

# 注文データのCRUD操作を行うモジュール
def insert_order(order: OrderIn) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    order_date = int(time.time())  # UNIXタイムスタンプ

    cursor.execute("""
        INSERT INTO orders (order_date, seat_id, menu_id, order_cnt)
        VALUES (?, ?, ?, ?)
    """, (order_date, order.seat_id, order.menu_id, order.order_cnt))

    conn.commit()
    conn.close()

# 注文の集計情報を取得する関数
def get_order_summary(seat_id: int) -> List[OrderOut]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # 注文の集計情報を取得するためのクエリ
    cursor.execute("""
        SELECT o.seat_id, o.order_date, m.food_name, m.unit_price, m.order_cnt 
        FROM orders o
        JOIN menus m ON o.menu_id = m.id
        WHERE o.seat_id = ?
        GROUP BY o.seat_id, o.order_date, m.food_name, m.unit_price
        ORDER BY o.order_date DESC
    """, (seat_id,))

    
    row = cursor.fetchone()
    conn.close()

    if row:
        # 注文の集計情報をOrderOutスキーマに変換
        # order_dateをUNIXタイムスタンプからフォーマットされた文字列に変換    
        order_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[1]))

        return [OrderOut(
            seat_id=row[0],
            order_date=order_date, 
            food_name=row[2],
            unit_price=row[3],
            order_cnt=row[4]
        )]
    else:
        return []
