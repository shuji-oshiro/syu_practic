from sqlalchemy import Column, Integer, String
from backend.app.database.database import Base

# DBモデルの定義
# ここでは、SQLAlchemyのORMを使ってデータベースのテーブルを定義します。
# この例では、ユーザーテーブルを定義しています。
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
