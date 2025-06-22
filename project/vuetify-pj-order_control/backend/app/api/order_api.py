# app/main.py

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from backend.app.crud import order_crud
from backend.app.models import model
from backend.app.database import database
from backend.app.schemas.order_schema import OrderIn,OrderOut

# データベースのテーブルを作成
# これにより、models.pyで定義したテーブルがデータベースに作成されます。
# もしテーブルが既に存在する場合は何も行いません。
model.Base.metadata.create_all(bind=database.engine)

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

router = APIRouter()

# シート単位の注文情報取得
@router.get("/{seat_id}", response_model=list[OrderOut])
def get_orders(seat_id: int, db: Session = Depends(get_db)):
    return order_crud.get_orders(db, seat_id)

# 注文情報追加
@router.post("/", response_model=list[OrderOut])
def add_order(orders: list[OrderIn], db: Session = Depends(get_db)):
    return order_crud.add_order(db, orders)

# 注文情報削除
@router.delete("/{order_id}", response_model=OrderOut)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return order_crud.delete_order(db, order_id)
