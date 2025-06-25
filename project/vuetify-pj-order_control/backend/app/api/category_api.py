# app/main.py

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from backend.app.crud import category_crud
from backend.app.database.database import get_db
from backend.app.schemas.category_schema import CategoryOut, CategoryIn


router = APIRouter()

# カテゴリ情報の取得
@router.get("/", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return category_crud.get_category(db)

# カテゴリ情報の登録
@router.post("/", response_model=list[CategoryOut])
def create_category(category: CategoryIn, db: Session = Depends(get_db)):
    category_crud.insert_category(db, category)

    return category_crud.get_category(db)  # すべてのカテゴリ情報を返す

