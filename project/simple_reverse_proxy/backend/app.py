from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/api/aaa")
def read_aaa():
    return Response(content="VERY GOOD JOB", media_type="text/plain")
