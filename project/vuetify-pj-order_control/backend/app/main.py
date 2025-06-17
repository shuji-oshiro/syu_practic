from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.models.db import init_menus_db, init_orders_db
from backend.app.api import menus, orders, voice

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(menus.router, prefix="/menus", tags=["menus"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])

# DB初期化
init_menus_db()
init_orders_db()
