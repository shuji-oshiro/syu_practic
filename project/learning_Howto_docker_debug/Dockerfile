# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 必要なパッケージをインストール
RUN pip install debugpy

COPY app.py .

# コンテナ起動時にdebugpyを使ってアプリを起動
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "app.py"]
