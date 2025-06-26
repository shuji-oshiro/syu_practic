# app/main.py
import csv
from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException, UploadFile, File
from backend.app.crud import menu_crud
from backend.app.database.database import get_db
from backend.app.schemas.menu_schema import MenuIn, MenuUpdate, MenuOut

router = APIRouter()

# メニュー情報の取得
# メニューIDを指定してメニュー情報を取得する
@router.get("/{menu_id}", response_model=MenuOut)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    if menu_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid menu ID")  # メニューIDが0以下の場合は400エラーを返す
    result = menu_crud.get_menu_by_id(db, menu_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return result

# 全てのメニュー情報を取得
# 取得したいメニュー情報は、全てのメニュー情報を取得する
@router.get("/", response_model=list[MenuOut])
def get_all_menus(db: Session = Depends(get_db)):
    result = menu_crud.get_menus(db)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="No menus found")
    return result


# メニュー情報の追加
@router.put("/", response_model=list[MenuOut])
def add_menu(menu: MenuIn, db: Session = Depends(get_db)):
    return menu_crud.add_menu(db, menu)

# メニュー情報の一括更新
@router.post("/", response_model=list[MenuOut])
def import_menu(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = file.file.read().decode("utf-8")
        reader = csv.reader(contents.splitlines())
        next(reader)  # ヘッダー行をスキップする場合はコメントアウトを外す
        menus = []
        for row in reader:
            category_id, food_name, unit_price, description, search_text = row
            menuin = MenuIn(
                category_id=int(category_id),  # カテゴリIDは適宜設定してください
                name=food_name,
                price=int(unit_price),
                description=description,
                search_text=search_text
            )
            menus.append(menuin)

        return menu_crud.import_menus_from_csv(db, menus)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'メニュー情報の一括更新処理に失敗しました： {e}')

# メニュー情報の更新
@router.patch("/", response_model=list[MenuOut])
def update_menu(menu_update: MenuUpdate, db: Session = Depends(get_db)):
    return menu_crud.update_menu(db, menu_update)

# メニュー情報の削除
@router.delete("/{menu_id}", response_model=list[MenuOut])
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    return menu_crud.delete_menu(db, menu_id)