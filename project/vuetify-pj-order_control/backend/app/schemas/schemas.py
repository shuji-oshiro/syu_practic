# app/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

# リクエスト用（ユーザー作成）
class UserCreate(BaseModel):
    name: str
    email: EmailStr

# レスポンス用（ユーザー取得）
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

        # app/schemas.py

class UserUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None

