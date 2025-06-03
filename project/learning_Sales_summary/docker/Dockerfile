# Stage 1: Copy frontend files (HTML, JS, CSS)
FROM nginx:latest AS nginx-stage
COPY ../nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ../frontend /usr/share/nginx/html

# Stage 2: Python FastAPI
FROM python:3.11-slim AS app-stage

# 作業ディレクトリ
WORKDIR /app

#TODO: 依存関係インストール
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install fastapi uvicorn python-multipart pytz pandas pytest pytest-asyncio


# アプリケーション本体
COPY ../app /app

# データディレクトリを作成（必要なら）
RUN mkdir -p /app/data /app/logs && chmod 755 /app/data

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
