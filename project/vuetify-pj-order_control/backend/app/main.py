from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import menu_api, order_api, voice

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
# app.include_router(menus.router, prefix="/menus", tags=["menus"])
app.include_router(order_api.router, prefix="/order", tags=["order"])
app.include_router(menu_api.router, prefix="/menu", tags=["menu"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])


