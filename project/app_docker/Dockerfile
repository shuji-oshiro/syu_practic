# ベースイメージ（例: Python 3.11）
FROM python:3.11-slim

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係をコピー＆インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY app/ .

# 実行コマンド（例：main.py を実行）
CMD ["python", "main.py"]
