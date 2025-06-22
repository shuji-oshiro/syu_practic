from datetime import datetime
from sqlalchemy import String,func,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.database import Base
from sqlalchemy.orm import relationship

# DBモデルの定義
# ここでは、SQLAlchemyのORMを使ってデータベースのテーブルを定義します。
# この例では、ユーザーテーブルを定義しています。
class Menu(Base):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)
    price: Mapped[int] = mapped_column(nullable=False) 
    description: Mapped[str] = mapped_column(String, nullable=True)
    search_text: Mapped[str] = mapped_column(String, index=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="menu")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_date: Mapped[datetime] = mapped_column(default=func.now())
    seat_id: Mapped[int] = mapped_column(index=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"), index=True)
    order_cnt: Mapped[int] = mapped_column(nullable=False)

    menu: Mapped["Menu"] = relationship("Menu", back_populates="orders")

