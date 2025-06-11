# simple_reverse_proxy

この学習プロジェクトは、**nginx** をリバースプロキシとして使用し、小さな FastAPI バックエンドの前段に配置する構成を示しています。
Dockerコンテナでアプリを起動し、リモートでデバックポイント参照できる方法を学びます。

## 使い方

1. コンテナをビルドして起動します：
   ```bash
   docker-compose up --build
   ```
2. coursorのデバッグを実行　-> "Python: Attach to Backend"

デバッグなし 修正即反映 -> --reload 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
デバッグあり
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


3. Open `http://localhost` in your browser. Click the "取得" button to fetch data from the backend.

The backend will respond with the plain string `AAA`.

## Structure

- `backend/` - FastAPI application and Dockerfile
- `frontend/` - Static HTML/JavaScript served by nginx
- `nginx/` - nginx configuration
- `docker-compose.yml` - compose file running nginx and the backend
