# app/main.py
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/submit")
def handle_form(name: str = Form(...)):
    return JSONResponse(content={"msg": f"こんにちは、{name}さん！"})
