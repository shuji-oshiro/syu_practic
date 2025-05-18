# 個人学習用：開発環境・コマンド集

---

## 目次
- [Git 基本コマンド](#git-基本コマンド)
- [Python 仮想環境・パッケージ管理](#python-仮想環境パッケージ管理)
- [Docker 操作・開発環境構築](#docker-操作開発環境構築)
- [Ubuntu/WSL 操作](#ubuntuwsl-操作)
- [ターミナル便利操作](#ターミナル便利操作)
- [技術選定・要件整理テンプレート](#技術選定要件整理テンプレート)

---

## Git 基本コマンド

### リポジトリの初期化・コミット
**新しいプロジェクトをGitで管理したいときに使います。**
```sh
git init                # Git管理を開始
git add *               # すべてのファイルをステージ
git commit -m "initial commit"  # 最初のコミット
```

### リモートリポジトリのクローン
**GitHubなどのリモートリポジトリからプロジェクトをコピーしたいとき。**
```sh
git clone [リモートリポジトリパス]
```
> 例: `git clone https://github.com/ユーザー名/リポジトリ名.git`

### リモートリポジトリの解除
**リモートとの紐付けを外したいとき。**
```sh
git remote remove origin
```

### Git管理から外す
**Gitの管理自体を完全にやめたい場合。**
```sh
rm -rf .git
```

### ファイルの追加・除外
**変更したファイルや新規ファイルをコミット対象にするコマンド。**
```sh
git add .         # すべて追加
git add *.css     # CSSファイルのみ追加
git add -n        # 追加予定ファイルを確認
git add -u        # 更新・削除のみ
git rm --cached   # add済みファイルを除外
```

### コミット
**変更内容を履歴として記録します。**
```sh
git commit -a     # 変更のあったファイルすべて
git commit --amend # 直前のコミット修正
```

### コミットの取り消し・復元
**間違えたコミットや削除を元に戻したいとき。**
```sh
git reset --soft HEAD~2   # 2件分をワークディレクトリ保持で取り消し
git reset --hard HEAD~2   # 2件分を完全に取り消し
git restore .             # commit前の削除ファイル復元
git checkout HEAD -- .    # restoreで復元できない場合
```

### リモートの最新状態に戻す
**ローカルの状態をリモートの最新に完全に合わせたいとき。**
```sh
git fetch origin
git reset --hard origin/master
```

### ブランチ操作
**新機能開発や修正作業を分岐して行いたいとき。**
```sh
git branch [branch_name]      # 作成
git checkout [branch_name]    # 移動
git branch -d [branch_name]   # 削除
git branch -m [branch_name]   # 名前変更
git branch                    # 一覧
git branch -a                 # 全ブランチ
git branch -r                 # リモートブランチ
git checkout -b branch_name origin/branch_name # リモートブランチへ
```

### 差分・ログ
**どこが変わったか、履歴を確認したいとき。**
```sh
git diff
git diff HEAD^
git diff --name-only HEAD^
git log
git reflog
```

### プルリクエストの流れ
**GitHubでの共同開発の基本的な流れです。**
1. ブランチ作成: `git checkout -b <ブランチ名>`
2. 変更・コミット: `git add .` → `git commit -a -m "メッセージ"`
3. プッシュ: `git push origin <ブランチ名>`
4. GitHubでPR作成・マージ
5. mainへ戻る: `git checkout main`
6. 最新化: `git pull origin main --rebase`
7. 作業ブランチ削除: `git branch -d <ブランチ名>`

---

## Python 仮想環境・パッケージ管理

### venvによる仮想環境
**プロジェクトごとに依存パッケージを分離したいとき。**
```sh
python -m venv .venv                # 仮想環境作成
.\.venv\Scripts\activate            # 有効化（Windows）
pip install ...                     # 必要なパッケージをインストール
deactivate                          # 仮想環境の終了
Remove-Item -Recurse -Force .venv   # 仮想環境の削除（PowerShell）
```
> 仮想環境を使うことで、他プロジェクトとパッケージのバージョンが混ざらず安全です。

### pipreqsでrequirements.txt自動生成
**実際にimportしているパッケージだけをリストアップしたいとき。**
```sh
pipreqs . --force --encoding=utf-8
```
> 余計なパッケージが入らず、すっきりしたrequirements.txtが作れます。

### pip freezeで全パッケージ出力
**仮想環境にインストールされている全パッケージを記録したいとき。**
```sh
pip freeze > requirements.txt
```
> ただし、不要なパッケージも含まれる場合があります。

### パッケージのアップデート
```sh
python -m pip install --upgrade pip
```
> `-U`オプションでも同じ意味です。

### uvによる管理
**高速なパッケージ管理ツール。pipの代替としても使えます。**
```sh
uv self update
uv init <projectname>
uv venv
.venv\Scripts\activate
uv add <package>
uv run <script.py>
```
> pipよりも速く、依存関係の管理も強力です。

---

## Docker 操作・開発環境構築

### 基本動作確認
**Dockerが正しく動作しているか確認。**
```sh
docker version
```
- `docker: command not found` → クライアント未インストール or Docker Desktop未起動
- `permission denied` → `sudo usermod -aG docker $USER` で権限追加（要再起動）

### サンプル実行
**Dockerの動作確認用。**
```sh
docker run hello-world
```
> 返信があればOK！

### ポートバインド例
**ホストとコンテナのポートをつなげて、Webアプリなどにアクセスできるように。**
```sh
docker run -p 5000:5000 myapp
```
> 例：`http://localhost:5000` でアクセス可能

### Dockerfile例
**Pythonアプリの最小構成例。**
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
CMD ["python", "main.py"]
```
> プロジェクト直下に `Dockerfile` を置きましょう。

### イメージビルド・実行
```sh
docker build -t my-python-app .
docker run my-python-app
docker run -v $(pwd)/app:/app my-python-app # ホストのappディレクトリをコンテナにマウント
```
> -v オプションで、ホストのファイルをコンテナと共有できます。

### コンテナ・イメージ管理
```sh
docker ps         # 稼働中コンテナ一覧
docker ps -a      # 全コンテナ
docker stop <ID>  # コンテナ停止
docker container prune # 未使用コンテナ削除（yで実行）
docker image ls   # イメージ一覧
docker rmi <イメージ名> # イメージ削除
```
> コンテナやイメージは不要になったらこまめに削除しましょう。

### Docker Desktop/WSL連携
- **Docker Desktop停止**: タスクトレイの🐳→「Quit Docker Desktop」
- **WSL内Docker停止**: `wsl --shutdown`
> WSLのシャットダウンでDockerも間接的に止まります。

### docker-compose
**複数コンテナをまとめて管理したいときに便利。**
```sh
docker-compose up --build
docker-compose down
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```
> `docker-compose.yml` を用意しておくと、開発・本番環境の切り替えも簡単です。

---

## Ubuntu/WSL 操作

### Ubuntuログイン
**WindowsからLinux環境（WSL）に入る方法。**
```sh
wsl
wsl -d Ubuntu -u root   # rootユーザーでログイン
```

### ユーザー作成・権限付与
```sh
adduser <username>                # 新規ユーザー作成
sudo usermod -aG docker $USER     # dockerグループに追加
```
> dockerコマンドをsudoなしで使いたい場合はグループ追加が必要です。

### ルートユーザー変更
```sh
ubuntu config --default-user <username>
```
> デフォルトのログインユーザーを変更できます。

### WSL管理
```sh
wsl --shutdown           # WSLシャットダウン
wsl --terminate Ubuntu   # 強制停止
wsl --status             # 状態確認
wsl --unregister Ubuntu  # Ubuntu削除（データ全消去）
wsl --install -d Ubuntu  # 再インストール
```
> `wsl --unregister`は全データ消去なので注意！

---

## ターミナル便利操作

### インタラクティブ検索（履歴検索）
**過去に使ったコマンドを素早く呼び出せます。**
1. ターミナルで何も入力していない状態で `Ctrl + R` を押す
2. `(reverse-i-search)` と表示されたらキーワード入力（例: docker）
3. 履歴から該当コマンドをインクリメンタルに検索
4. 見つかったらEnterで実行、左右キーで編集も可能

> 長いコマンドや複雑なコマンドも、履歴からすぐ再利用できて超便利！

---

## AIを活用したコーディングを行う際に必要な、技術選定・要件整理テンプレート

**新しい開発や設計時に、抜け漏れなく要件を整理できます。**

1. **やりたいこと・ゴール**
   - 例：FastAPIでタスク管理APIを作りたい。タスクの登録・取得・削除ができるようにしたい。

2. **使用する技術・環境**
   - 言語・バージョン（例：Python 3.12）
   - フレームワークやライブラリ（例：FastAPI、Pydantic）
   - 実行環境（例：ローカルPC、Dockerコンテナ内、WSL2上のUbuntuなど）

3. **現在の状況**
   - 既存コード（例：main.pyにサンプルコードあり）
   - フォルダ構成（例：app/ 配下にsrc/とtests/あり）

4. **希望する仕様・制約**
   - 必須機能（例：エラーハンドリングあり、日本語エラーメッセージ）
   - セキュリティ要件（例：認証必須、CSRF対策）
   - パフォーマンス（例：大量データに耐えたい）
   - 外部連携・データ保存先（例：DB未使用、JSONファイルに保存）

5. **出力・スタイルの希望**
   - 1ファイル or 複数ファイル？
   - コメント（docstring）つける？
   - テストコードも一緒にほしい？
   - 最小構成でいい？（サンプル動作できればOK？）

6. **想定される使用シーン**
   - 例：社内ツール用、商用API、個人学習用

---

### さらに分かりやすくするポイント

- **なぜこのコマンドを使うのか？** → 目的や背景をコメントで補足
- **よくあるエラーや注意点** → 例やヒントを記載
- **実行例や出力例** → 実際のコマンド例を多めに

---

このファイルは個人学習用のまとめです。自分のペースで見返し、実際に手を動かしながら理解を深めてください！
