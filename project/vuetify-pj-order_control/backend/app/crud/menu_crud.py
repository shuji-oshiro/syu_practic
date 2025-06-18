import csv, os
from typing import List, Optional
from backend.app.models.db import get_db_connection
from backend.app.schemas.menu_schema import MenuOut, MenuIn, MenuUpdate

# メニュー情報をCSVファイルからデータベースに一括で挿入する関数
def import_menus_from_csv(file_path: str) -> list[MenuOut]:
    
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        for row in reader:
            food_name, unit_price, descrption, search_text = row
            cursor.execute("""
                INSERT INTO menus (name, price, description, search_text)
                VALUES (?, ?, ?, ?)
            """, (food_name, int(unit_price), descrption, search_text))

    conn.commit()
    conn.close()

    return get_menus()


# メニュー情報を取得する関数
def get_menus(menu_id: Optional[int] = None) -> List[MenuOut]:
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
        MenuOut(
            menu_id=row[0],
            food_name=row[1],
            unit_price=row[2],
            descrption=row[3],
            search_text=row[4]
        )
        for row in rows
    ]


# メニュー情報を追加する関数
def add_menu(menu_data: MenuIn) -> list[MenuOut]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO menus (name, price, description, search_text)
        VALUES (?, ?, ?, ?)
    """, (menu_data.food_name, menu_data.unit_price, menu_data.descrption, menu_data.search_text))

    conn.commit()
    conn.close()

    return get_menus()


# メニュー情報を更新する関数
def update_menu(menu_data: MenuUpdate) -> list[MenuOut]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE menus
        SET name = ?, price = ?, description = ?, search_text = ?
        WHERE id = ?
    """, (menu_data.food_name, menu_data.unit_price, menu_data.descrption, menu_data.search_text, menu_data.menu_id))

    conn.commit()
    conn.close()

    return get_menus(menu_data.menu_id)


# メニュー情報を削除する関数
def delete_menu(menu_id: Optional[int]) -> list[MenuOut]:
    if isinstance(menu_id, int):
        raise ValueError("menu_id must be an integer or None")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menus WHERE id = ?", (menu_id,))
    conn.commit()
    conn.close()

    return get_menus()