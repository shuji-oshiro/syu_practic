from pydantic import BaseModel

class MenuOut(BaseModel):
    menu_id: int
    food_name: str
    unit_price: int
    descrption: str
    search_text: str

    class Config:
        orm_mode = True

class MenuIn(BaseModel):
    food_name: str
    unit_price: int
    descrption: str
    search_text: str

    class Config:
        orm_mode = True

class MenuUpdate(BaseModel):
    menu_id: int
    food_name: str
    unit_price: int
    descrption: str
    search_text: str

    class Config:
        orm_mode = True
