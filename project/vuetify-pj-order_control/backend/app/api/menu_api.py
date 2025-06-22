# app/main.py
import csv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from backend.app.crud import menu_crud
from backend.app.database.database import get_db
from backend.app.schemas.menu_schema import MenuIn, MenuUpdate, MenuOut,MenuInputCsv


router = APIRouter()

# メニュー情報の取得
# メニューIDを指定してメニュー情報を取得する
@router.get("/{menu_id}", response_model=MenuOut)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    return menu_crud.get_menu_by_id(db, menu_id)

# 全てのメニュー情報を取得
# 取得したいメニュー情報は、全てのメニュー情報を取得する
@router.get("/", response_model=list[MenuOut])
def get_all_menus(db: Session = Depends(get_db)):
    return menu_crud.get_menus(db)

# メニュー情報の追加
@router.put("/", response_model=list[MenuOut])
def add_menu(menu: MenuIn, db: Session = Depends(get_db)):
    return menu_crud.add_menu(db, menu)

# メニュー情報の一括更新
@router.post("/", response_model=list[MenuOut])
def import_menu(csvinfo: MenuInputCsv, db: Session = Depends(get_db)):

    with open(csvinfo.file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        menus = []
        for row in reader:
            food_name, unit_price, descrption, search_text = row
            menuin = MenuIn(
                name=food_name,
                price=int(unit_price),
                description=descrption,
                search_text=search_text
            )
            menus.append(menuin)

    return menu_crud.import_menus_from_csv(db, menus)

# メニュー情報の更新
@router.patch("/", response_model=list[MenuOut])
def update_menu(menu_update: MenuUpdate, db: Session = Depends(get_db)):
    return menu_crud.update_menu(db, menu_update)

# メニュー情報の削除
@router.delete("/{menu_id}", response_model=list[MenuOut])
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    return menu_crud.delete_menu(db, menu_id)