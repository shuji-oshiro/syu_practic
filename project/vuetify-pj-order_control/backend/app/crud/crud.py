# app/crud.py

from sqlalchemy.orm import Session
from backend.app.models import models
from backend.app.schemas import schemas


def create_user(db: Session, user: schemas.UserCreate):
    try:
        # ユーザーをデータベースに追加
        db_user = models.User(name=user.name, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)  # ここで自動的に ID が入る
        return db_user
    except Exception as e:
        db.rollback()   



def get_users(db: Session):
    return db.query(models.User).all()

# app/crud.py

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(db: Session, user_update: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_update.id).first()
    if not user:
        return None
    if user_update.name is not None:
        setattr(user, "name", user_update.name)
    if user_update.email is not None:
        setattr(user, "email", user_update.email)
    db.commit()
    db.refresh(user)
    return user