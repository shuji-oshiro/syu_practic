from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil, os, uuid, subprocess
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # VueのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
CONVERTED_DIR = "converted"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    input_path = f"{UPLOAD_DIR}/{uuid.uuid4()}.webm"
    output_path = f"{CONVERTED_DIR}/{uuid.uuid4()}.mp3"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["ffmpeg", "-i", input_path, output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {"url": f"/converted/{os.path.basename(output_path)}"}

@app.get("/converted/{filename}")
def get_file(filename: str):
    return FileResponse(f"{CONVERTED_DIR}/{filename}", media_type="audio/mpeg")
