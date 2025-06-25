from .baseSchema import BaseSchema

class MenuOut(BaseSchema):
    id: int    
    category_id: int
    name: str
    price: int
    description: str
    search_text: str

class MenuIn(BaseSchema):
    category_id: int
    name: str
    price: int
    description: str
    search_text: str

class MenuUpdate(BaseSchema):
    menu_id: int
    category_id: int
    name: str
    price: int
    description: str
    search_text: str


