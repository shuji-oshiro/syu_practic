
このプロジェクト（task_send_mail_learning_typescript）は、TypeScriptで書かれたアプリケーションで、
主にタスク管理やメール送信などの機能を学習・実装するためのものです。  


## 0. 操作方法

1.タスク管理画面の表示
URLへのパラメータ設定有無により表示内容が変わる

すべてのタスクとメールアドレスを表示
http://{稼働しているＰＣのＩＰアドレス}:3000/

メールアドレスを指定すると、そのメールアドレスのタスクのみを表示します。タスクの追加や削除はできません。
http://{稼働しているＰＣのＩＰアドレス}:3000/?user={メールアドレス}

2.タスクの管理
タスク完了
タスク毎に設定されているメールアドレス右部に表示されるチェックボックスをＯＮにする
再度ＯＦＦにするとタスク未完了でメールが送信される

3.タスクの追加
新しいタスクに任意の文字を入力
初期値は下部に表示されているメールアドレスがタスク管理の対象
タスク追加ボタンで、タスクと関連するメールアドレスが登録される
管理対象のメールアドレスを追加する事ができる
管理対象外のメールアドレスを削除する事ができる

4.タスクの削除
タスクを削除するには、タスクの右側にある✖ボタンをクリック

5.初期設定メールアドレスの取り込み
送信先メールアドレスの初期設定ボタンを押下するとファイルダイアログが表示される
指定のファイルを選択し、初期設定メールアドレスを新しく更新する
アドレス一覧のファイルはメールアドレスのカンマ区切りで保存



---

## 1. 実行環境

- **Docker対応**  

docker-compose を使用して、アプリをビルドし、コンテナとして起動できます。

開発時:
docker-compose up --build
→ コード変更が即時反映されます（ts-node利用）

本番ビルド:
docker-compose -f docker-compose.yml up --build -d
→ TypeScriptがビルドされ、dist 配下のJSで起動


  起動（バックグラウンド）:
  docker-compose up -d

  停止と削除（ボリュームも含む）:
  docker-compose down --volumes



## 2. 開発環境セットアップ

- **Node.jsとnpmのインストール**  
  Node.js公式サイトからインストールし、バージョン確認。

- **npm初期化**  
  `npm init -y` で `package.json` を作成。

- **TypeScript導入**  
  ```
  npm install typescript --save-dev
  npx tsc --init
  ```

- **型定義ファイル**  
  Node.jsの型定義を追加（`@types/node`）。

---

## 3. TypeScriptのビルド・実行

- **TypeScriptのコンパイル**  
  `npx tsc` で `src` ディレクトリ配下のTypeScriptファイルをコンパイルし、`dist` ディレクトリに出力（`tsconfig.json`で設定）。

- **JavaScriptの実行**  
  `node dist/xxx.js` でコンパイル後のファイルを実行。

---

## 4. tsconfig.jsonの主な設定

- `outDir`: コンパイル後の出力先（例: `./dist`）
- `rootDir`: ソースファイルの場所（例: `./src`）
- `module`: モジュールシステム（CommonJS）
- `target`: 出力するJavaScriptのバージョン（ES2020）
- `esModuleInterop`, `moduleResolution`, `strict` など

---

## 5. 処理の流れ

1. **サーバー起動**  
   `src/gui/server.ts` からサーバーが起動し、WebアプリやAPIとして動作。

2. **タスク管理やメール送信**  
   プロジェクト名やディレクトリ名から、タスク管理やメール送信の機能。

3. **フロントエンド/GUI**  
   `src/gui/` 配下にフロントエンドやWebサーバーの実装がある可能性。

---

## 6. まとめ

- TypeScriptで書かれたサーバーサイドアプリケーション
- Dockerまたは直接Node.jsで実行可能
- タスク管理やメール送信の学習用プロジェクト
- 標準的なTypeScript/Node.jsプロジェクト構成

---

project-root/
├── src/                # TypeScriptソースコード
├── dist/               # コンパイル後のJavaScript（自動生成物）
├── node_modules/       # 依存パッケージ（自動生成物）
├── package.json        # npmパッケージ管理ファイル
├── package-lock.json   # 依存関係のバージョン固定ファイル
├── tsconfig.json       # TypeScript設定ファイル
├── .gitignore          # Git管理除外リスト
└── README.md           # プロジェクト説明

