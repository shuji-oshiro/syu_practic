from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/api/aaa")
def read_aaa():
    return Response(content="AAA", media_type="text/plain")
