# show_picture

Python/Tkinter を用いた画像・動画サムネイルビューアです。指定フォルダ内のファイルを一覧表示し、タグによるフィルタや日付範囲の検索、ダブルクリックでのファイルオープンなどが行えます。

## 特徴
- 画像と動画を自動でサムネイル生成して一覧表示
- タグの追加・編集を行う簡易メニューを右クリックから表示
- `.env` で指定したフォルダとタグ管理 JSON を利用
- 作成日による絞り込み（日付入力欄）

## セットアップ
1. Python 3.11 以上を用意してください。
2. `pyproject.toml` の依存パッケージをインストールします。
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows は venv\Scripts\activate
   pip install -r uv.lock
   ```
3. プロジェクトルートに `.env` を作成し、次の環境変数を設定します。
   ```
   IMAGE_FOLDER=/path/to/pictures
   PICTURE_TAGS_JSON=/path/to/image_tag_map.json
   ```

## 実行方法
仮想環境を有効化した状態で下記コマンドを実行します。
```bash
python main.py
```
起動後、指定フォルダの画像・動画がサムネイル表示され、タグ選択や日付フィルタが利用できます。ダブルクリックでファイルを既定のアプリで開きます。

## フォルダ構成
```
project/show_picture/
├── main.py          # GUI アプリ本体
├── logic.py         # タグ処理等のロジック
├── dummyMenu.py     # タグ編集用の簡易メニュー
├── image_tag_map.json  # タグ情報サンプル
├── pyproject.toml   # 依存定義
└── uv.lock          # ロックファイル
```

## ライセンス
学習目的のためのサンプルコードです。商用利用はご遠慮ください。
