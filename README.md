## このリポジトリについて

このプロジェクトは、個人の学習および技術検証を目的としたものです。  
内容は随時変更・更新される可能性があります。  
ソースコードや設定等は、あくまで自分用のメモ的な意味合いを持っています。


- **FastAPI** と **Docker** を用いて構築した、**iPhone/GoogleのAPI通信
- 社内販売情報による売上分析システム**の学習プロジェクトです。  
- 個人の勉強・技術検証を目的としており、内容は随時更新・変更される可能性があります。

## 使用技術

- Python 3.x
- FastAPI
- Docker / Docker Compose
- Pandas /　（データ分析）
- sklearn
- その他、必要に応じて追加

## 学習目的

- FastAPI の基本構成とエンドポイント設計の理解
- Docker による開発環境のコンテナ化
- 売上データの集計・可視化の基礎
- API を使った分析処理の実装

## 新規参加者向けガイド

このリポジトリは個人学習・技術検証用のコードをまとめたもので、主に FastAPI、Docker、データ分析関連の学習を目的としています。  また、開発でよく使うコマンドや環境構築のメモが `personal_study_commands.md` に整理されています。

### リポジトリ全体構成
- **プロジェクトルート**  
  - `README.md` — リポジトリ全体の目的と使用技術を記載  
  - `personal_study_commands.md` — Git や Docker などの基本操作集  
  - `project/` ディレクトリ — 各学習プロジェクトを格納

- **主なサブプロジェクト（`project/` 配下）**
  - `add_pictureTag/` — Tkinter で作成した画像・動画のタグ付けツール。フォルダ内の画像を表示し、トグルボタンでタグ付けして `tags.json` に保存できます。
  - `learning_Howto_docker_debug/` — Dockerコンテナ内でのデバッグ手順をまとめたサンプル。  
  - `learning_Sales_summary/` — FastAPI と nginx を使った売上集計システム。CSV アップロード・集計処理・フロントエンド画面などを含みます。
  - `learning_loginprocess/` — FastAPI によるシンプルなログイン実装例。メール認証コードを使う 2 段階認証の流れや環境構築方法がまとめられています。
  - `show_picture/` — 画像・動画サムネイル表示アプリ。Tkinter ベースでタグ管理や日付フィルタ機能を提供。
  - `ok_SalesAnalysis_by_python/` — Tkinter を使った売上データ分析ツール。Excel への出力機能など業務向けの機能を備えます。
  - `ok_SaleseAnalysis_by_python_and_Flask/` — Flask と jQuery DataTables を組み合わせた売上分析Webアプリ。
  - `ok_task_Send_mail/` — TypeScript/Node.js で書かれたタスク管理・メール送信アプリ。Docker を用いた開発・本番ビルド方法が説明されています。
  - `sukitto_learnig/` — 機械学習入門書「スッキリわかる〜」のコードを含む学習用ディレクトリ。

### 重要なポイント
1. **サブプロジェクト単位で環境が異なる**  
   Python プロジェクト（FastAPI/Tkinter 等）と TypeScript プロジェクトが混在しています。各 README を参考に必要な依存パッケージをインストールしてください。
2. **Docker を活用した開発が多い**  
   いくつかのプロジェクトでは Dockerfile や `docker-compose.yml` が用意されています。README で示された `docker-compose up --build` などの手順を確認しましょう。
3. **コマンドのチートシートを活用**  
   Git 操作や仮想環境の作成手順など、基本的な開発コマンドが `personal_study_commands.md` にまとまっています。
4. **動作確認方法は README に記載**  
   それぞれのサブプロジェクトの README に、起動コマンドやテスト実行手順、開発環境の準備方法が書かれています。まず README を読む習慣を付けてください。

### 次に学ぶことの指針
- **FastAPI 入門**  
  `learning_Sales_summary` や `learning_loginprocess` を通じて、FastAPI のエンドポイント設計や認証処理、Docker を使ったデプロイ方法を学べます。
- **デスクトップアプリ開発**  
  `add_pictureTag` や `ok_SalesAnalysis_by_python` で、Tkinter を使った GUI 開発の基礎や、データ可視化の方法を学習できます。
- **Web フロントエンドとバックエンドの連携**  
  `ok_SaleseAnalysis_by_python_and_Flask` プロジェクトでは、Flask（または FastAPI）とフロントエンド（HTML/JS）の連携例を確認できます。
- **TypeScript/Node.js**  
  `ok_task_Send_mail` をもとに、TypeScript でのサーバー実装や Docker を利用したビルド・デプロイ手順を学んでみてください。
- **機械学習入門**  
  `sukitto_learnig` ディレクトリには、機械学習書籍のサンプルコードや練習用スクリプトがあります。実データを使ったモデル構築の流れを体験できます。

### まとめ
このリポジトリは複数の学習用サンプルが集まった「実験場」です。まずは各サブプロジェクトの README を読み、必要な環境を整えたうえで動かしてみることをおすすめします。疑問点があれば `personal_study_commands.md` にあるコマンド集やコメントを参考に、少しずつ手を動かしながら学習を進めてみてください。

