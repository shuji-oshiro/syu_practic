from .baseSchema import BaseSchema

class CategoryBase(BaseSchema):
    name: str
    description: str

class MenuOut(BaseSchema):
    id: int    
    category_id: int
    name: str
    price: int
    description: str
    search_text: str
    category: CategoryBase

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


