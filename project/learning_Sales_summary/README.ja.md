# learning_Sales_summary 日本語版 README

このディレクトリは FastAPI と nginx を使った **売上集計システム** の学習用プロジェクトです。
フロントエンドから CSV をアップロードすると、バックエンドで集計処理を行い結果を JSON で返します。

## 概要
- **フロントエンド (`frontend/`)**
  - 商品コードや商品名、売上目標を入力する Web 画面を提供します。
  - CSV ファイルのアップロードボタンから売上データを送信できます。
- **バックエンド (`app/`、FastAPI)**
  - アップロードされた CSV を読み込み、商品ごと・取引先ごとの売上を集計します。
  - 目標達成率の計算や、空ファイル・欠損カラムなどのエラーチェックも行います。
- **nginx**
  - 静的ファイルの配信と FastAPI へのリバースプロキシを担当します。
- **Docker 構成**
  - nginx コンテナと FastAPI コンテナを用意し、`docker-compose` で起動します。

## 環境
- Python 3.11
- FastAPI / Uvicorn
- Docker, Docker Compose
- その他依存パッケージは `requirements.txt` を参照してください。

## 実行手順
1. 本番想定の構成で起動する場合
   ```bash
   docker-compose up --build
   ```
   その後 `http://localhost/` にアクセスします。
2. 開発用コンテナを利用する場合
   ```bash
   docker-compose -f docker-compose.dev.yml build
   docker-compose -f docker-compose.dev.yml up
   ```
3. テストの実行
   ```bash
   cd project/learning_Sales_summary
   pytest
   ```

## ディレクトリ構成
- `frontend/` - HTML、JavaScript、CSS
- `app/` - FastAPI アプリケーション
- `docker/` - Dockerfile などビルド用設定
- `nginx/` - nginx 設定ファイル
- `tests/` - 自動テスト用スクリプト

この README は元の英語 README を日本語に翻訳し、環境や実行手順を追記したものです。
