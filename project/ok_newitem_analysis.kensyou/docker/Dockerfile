FROM python:3.11-slim

WORKDIR /app
COPY ../app /app

# データディレクトリを作成
RUN mkdir -p /app/data && chmod 777 /app/data

RUN pip install fastapi uvicorn python-multipart pytz pandas pytest pytest-asyncio

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
