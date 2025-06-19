from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLiteを使用する場合は、ファイルパスを指定します。
# DATABASE_URL = "sqlite:///./users.db"  # ← ファイルで保存
DATABASE_URL = 'sqlite:///file:mem1?mode=memory&cache=shared -uri true'

# SQLAlchemy が DBと通信するためのエンジンを作成
engine = create_engine(
    # check_same_thread=False：SQLiteでは複数スレッドから接続するために必要な設定（FastAPIは非同期なので必須）
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    
)
# sessionmaker(...)：DBへの操作（SELECT / INSERT など）をするための セッション生成器
# autocommit=False：自動で commit しない（明示的に db.commit() が必要）
# autoflush=False：自動でフラッシュしない（明示的に db.flush() が必要）
# bind=engine：先ほど作成したDBと通信するためのエンジンをバインドする
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base()：SQLAlchemyのORMを使うためのベースクラスを生成
# これを継承したクラスがDBモデル（テーブル）となる
Base = declarative_base()
