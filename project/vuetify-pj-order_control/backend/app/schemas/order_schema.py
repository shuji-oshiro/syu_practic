from pydantic import BaseModel

class OrderIn(BaseModel):
    seat_id: int
    menu_id: int
    order_cnt: int

class OrderOut(BaseModel):
    seat_id: int
    order_date: str # フォーマットされた日時文字列
    food_name: str
    unit_price: int
    order_cnt: int

    class Config:
        orm_mode = True
