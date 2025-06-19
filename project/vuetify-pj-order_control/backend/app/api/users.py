# app/main.py

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models import models
from backend.app.schemas import schemas
from backend.app.crud import crud
from backend.app.database import database

# データベースのテーブルを作成
# これにより、models.pyで定義したテーブルがデータベースに作成されます。
# もしテーブルが既に存在する場合は何も行いません。
models.Base.metadata.create_all(bind=database.engine)

router = APIRouter()

# データベースセッションを取得するための依存関係
# FastAPIの依存性注入を使用して、各エンドポイントでデータベースセッションを取得します。
# これにより、各リクエストごとに新しいセッションが生成され、リクエストが終了したら自動的に閉じられます。
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        print("-------------Closing database session-------------")
        db.close()

# FastAPI実行の流れ
# 1.Depends(get_db) が評価されて db = SessionLocal() でセッションが生成される
# 2.yield db の db がエンドポイントに渡される
# 3.エンドポイントの処理が完了したら finally ブロックが実行され、db.close() でセッションが閉じられる

# ユーザー一覧
@router.get("/", response_model=list[schemas.UserRead])
def read_users(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    if user_id is not None:
        user = crud.get_user_by_id(db, user_id)
        return [user] if user else []  # 1件 or 空リスト
    else:
        # user_id が指定されていない場合は全ユーザーを返す
        return crud.get_users(db)

# ユーザー作成
@router.post("/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@router.patch("/", response_model=schemas.UserRead)
def update_user(user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = crud.update_user(db, user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
