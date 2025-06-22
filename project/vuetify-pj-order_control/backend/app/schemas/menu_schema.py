from .baseSchema import BaseSchema

class MenuOut(BaseSchema):
    id: int    
    name: str
    price: int
    description: str
    search_text: str

class MenuIn(BaseSchema):
    name: str
    price: int
    description: str
    search_text: str

class MenuUpdate(BaseSchema):
    menu_id: int
    name: str
    price: int
    description: str
    search_text: str


class MenuInputCsv(BaseSchema):
    file_path: str
