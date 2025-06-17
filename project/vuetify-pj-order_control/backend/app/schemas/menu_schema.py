from pydantic import BaseModel

class MenusOut(BaseModel):
    menu_id: int
    food_name: str
    unit_price: int
    descrption: str
    search_text: str

    class Config:
        orm_mode = True
