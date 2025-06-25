# app/crud.py
from fastapi import HTTPException
import backend.app.models.model as model
from sqlalchemy.orm import Session
from backend.app.schemas.category_schema import CategoryIn


# 注文情報のCRUD操作を行うモジュール
# カテゴリ情報の取得
# 取得したいカテゴリ情報は、カテゴリIDを指定して取得する
def get_category(db: Session):
    return db.query(model.Category).all()

def insert_category(db: Session, category: CategoryIn):
    db_category = model.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category