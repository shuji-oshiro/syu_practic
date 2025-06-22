from datetime import datetime
from sqlalchemy import String,func,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.database import Base
from sqlalchemy.orm import relationship

# DBモデルの定義
# ここでは、SQLAlchemyのORMを使ってデータベースのテーブルを定義します。


# メニュー情報を格納するテーブル

class Menu(Base):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True, index=True) # 主キー
    name: Mapped[str] = mapped_column(String, index=True, unique=True) # メニュー名
    price: Mapped[int] = mapped_column(nullable=False) # 価格
    description: Mapped[str] = mapped_column(String, nullable=True) # 説明
    search_text: Mapped[str] = mapped_column(String, index=True, nullable=False) # 検索テキスト

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="menu")

# 注文情報を格納するテーブル
# 注文はメニューに紐づく
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True) # 主キー
    order_date: Mapped[datetime] = mapped_column(default=func.now()) # 注文日時
    seat_id: Mapped[int] = mapped_column(index=True) # 座席ID
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"), index=True) # メニューID（外部キー）
    order_cnt: Mapped[int] = mapped_column(nullable=False) # 注文数

    menu: Mapped["Menu"] = relationship("Menu", back_populates="orders")

