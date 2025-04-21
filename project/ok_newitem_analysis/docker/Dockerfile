FROM python:3.11-slim

WORKDIR /app
COPY ../app /app

# wheelファイルを追加（ローカルでダウンロードしたもの）
#COPY wheelhouse /wheelhouse


# データディレクトリを作成
RUN mkdir -p /app/data && chmod 777 /app/data

# wheel からパッケージをインストール（PyPIは使わない）
#RUN pip install --no-index --find-links=/wheelhouse fastapi uvicorn python-multipart pytz pandas pytest pytest-asyncio

RUN pip install fastapi uvicorn python-multipart pytz pandas pytest pytest-asyncio

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
