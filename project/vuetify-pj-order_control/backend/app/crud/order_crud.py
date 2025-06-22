# app/crud.py
from fastapi import HTTPException
import backend.app.models.model as model
from sqlalchemy.orm import Session
from backend.app.schemas.order_schema import OrderOut, OrderIn



def get_orders(db: Session, seat_id: int):
    return db.query(model.Order).filter(model.Order.seat_id == seat_id)



def add_order(db: Session, order: OrderIn):
    try:        
        db_order = model.Order(
                seat_id=order.seat_id,
                menu_id=order.menu_id,
                order_cnt=order.order_cnt
            )
        db.add(db_order)
        db.commit()
        db.refresh(db_order) 
        return db_order
    except Exception as e:
        db.rollback()   
        raise HTTPException(status_code=500, detail="Invalid input data")

