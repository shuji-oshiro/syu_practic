import csv, os
from typing import List, Optional
from backend.app.models.db import get_db_connection
from backend.app.schemas.menu_schema import MenusOut

# メニュー情報をCSVファイルからデータベースに挿入する関数
def insert_menus_from_csv(file_path: str) -> None:
    
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue  # スキップ
            food_name, unit_price, descrption, search_text = row
            cursor.execute("""
                INSERT INTO menus (name, price, description, search_text)
                VALUES (?, ?, ?, ?)
            """, (food_name, int(unit_price), descrption, search_text))

    conn.commit()
    conn.close()

# メニュー情報を取得する関数
def get_menus(menu_id: Optional[int] = None) -> List[MenusOut]:
    conn = get_db_connection()
    cursor = conn.cursor()

    if menu_id is None:
        cursor.execute("SELECT id, name, price, description, search_text FROM menus")
        rows = cursor.fetchall()
    else:
        cursor.execute("SELECT id, name, price, description, search_text FROM menus WHERE id = ?", (menu_id,))
        rows = cursor.fetchall()

    conn.close()
    return [
        MenusOut(
            menu_id=row[0],
            food_name=row[1],
            unit_price=row[2],
            descrption=row[3],
            search_text=row[4]
        )
        for row in rows
    ]
