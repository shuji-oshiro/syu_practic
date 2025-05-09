# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txtをコピー
COPY ./requirements.txt ./

# 必要なパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリファイルをコピー
COPY . .

# アプリを起動
CMD ["python", "app.py"]
