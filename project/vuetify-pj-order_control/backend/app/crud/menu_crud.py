# app/crud.py
import csv
from fastapi import HTTPException
import backend.app.models.model as model
from sqlalchemy.orm import Session
from backend.app.schemas.menu_schema import MenuIn, MenuUpdate


def get_menus(db: Session): 
    return db.query(model.Menu).all()

def get_menu_by_id(db: Session, menu_id: int):
    return db.query(model.Menu).filter(model.Menu.id == menu_id).first()


# メニュー情報をCSVファイルからデータベースに一括で挿入する関数
def import_menus_from_csv(db: Session, file_path: str):
    
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        for row in reader:
            food_name, unit_price, descrption, search_text = row
            db_menu = model.Menu(
                name=food_name,
                price=int(unit_price),
                description=descrption,
                search_text=search_text
            )
            db.add(db_menu)
            db.refresh(db_menu)  # ここで自動的に ID が入る

    db.commit()
    db.flush()  # データベースに変更を反映

    return get_menus(db)    


def add_menu(db: Session, menu: MenuIn):
    try:        
        # ユーザーをデータベースに追加
        db_menu = model.Menu(
                name=menu.name,
                price=int(menu.price),
                description=menu.description,
                search_text=menu.search_text
            )
        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)  # ここで自動的に ID が入る
        return db_menu
    except Exception as e:
        db.rollback()   
        raise HTTPException(status_code=500, detail="Invalid input data")



def update_menu(db: Session, menu_update: MenuUpdate):
    # 更新処理
    db_menu = db.query(model.Menu).filter(model.Menu.id == menu_update.menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    try:        
        db_menu.name = menu_update.name
        db_menu.price = menu_update.price
        db_menu.description = menu_update.description
        db_menu.search_text = menu_update.search_text
        db.commit()
        db.refresh(db_menu)
        return db_menu
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Invalid input data")
