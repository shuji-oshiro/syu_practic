import random
import aiosmtplib
from email.message import EmailMessage
from itsdangerous import URLSafeSerializer
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings
from pydantic import Field


app = FastAPI()
templates = Jinja2Templates(directory="templates")
serializer = URLSafeSerializer("SECRET_KEY")

USERS = {
    "testuser": {"password": "testpass", "email": "syutv117@gmail.com"}
}
auth_codes = {}

class Settings(BaseSettings):
    smtp_user: str = Field(..., env="SMTP_USER")
    smtp_pass: str = Field(..., env="SMTP_PASS")
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()

# メール送信
async def send_email(to_email, code):
    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = to_email
    message["Subject"] = "認証コード"
    message.set_content(f"あなたの認証コードは {code} です。")
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_pass,
        start_tls=True,
    )

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = USERS.get(username)
    if user and user["password"] == password:
        code = str(random.randint(100000, 999999))
        auth_codes[username] = code
        await send_email(user["email"], code)
        return templates.TemplateResponse("verify.html", {"request": request, "username": username, "error": None})
    return templates.TemplateResponse("login.html", {"request": request, "error": "ログイン失敗"})

@app.post("/verify", response_class=HTMLResponse)
async def verify(
    request: Request,
    username: str = Form(...),
    code: str = Form(...)
):
    if auth_codes.get(username) == code:
        token = serializer.dumps({"user": username})
        response = RedirectResponse(url="/mypage", status_code=302)
        response.set_cookie("session", token, httponly=True)


        return response
    return templates.TemplateResponse("verify.html", {"request": request, "username": username, "error": "認証コードが違います"})

@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request):
    token = request.cookies.get("session")
    if not token:
        return RedirectResponse(url="/")
    try:
        data = serializer.loads(token)
        user = data["user"]
    except Exception:
        return RedirectResponse(url="/")
    return HTMLResponse(f"<h2>{user}さん、ようこそ！</h2><a href='/logout'>ログアウト</a>")

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    return response