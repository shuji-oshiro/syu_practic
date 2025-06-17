from fastapi import APIRouter, HTTPException
from typing import List
from backend.app.schemas.order_schema import OrderIn, OrderOut
from backend.app.crud import order_crud

router = APIRouter()

@router.post("/", response_model=List[OrderOut])
async def input_orders_data(order: OrderIn):
    try:
        order_crud.insert_order(order)
        return order_crud.get_order_summary(order.menu_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注文登録エラー: {str(e)}")
