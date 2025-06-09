# ok_SalesAnalysis_by_python

デスクトップ向けの売上分析ツールです。Tkinter を利用した GUI から売上データの読み込み、集計、グラフ表示、Excel への出力までを行います。

## 特徴
- CSV から売上データを読み込んで内部 DB (SQLite) に更新
- 集計期間や曜日、取引先/ライン/商品名などを GUI 上で指定可能
- 日別・週別・月別での集計と前年/前月/前週との比較が可能
- 集計結果を表形式で表示し、折れ線グラフや棒グラフ、ヒストグラムなどで可視化
- 分析結果は Excel(xlsx) ファイルとして出力可能

## フォルダ構成
```
project/ok_SalesAnalysis_by_python/
├── __main__.py            # アプリケーション本体 (Tkinter GUI)
├── __main__.spec          # PyInstaller 用設定
├── requirements.txt       # 依存パッケージ
└── py_pk/
    ├── analysis_data.py   # データ読み込み・集計処理
    ├── process_db.py      # SQLite DB 操作
    ├── sampledata.py      # デバッグ用ダミーデータ生成
    ├── settings.py        # 設定値
    └── README             # 日本語解説
```

## セットアップ
1. Python 3.11 以上をインストールしてください。
2. 仮想環境を作成し依存パッケージをインストールします。
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows は venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. `py_pk/settings.py` にある `DB_PATH` を実際の SQLite データベースのパスに合わせて変更します。

## 実行方法
アプリケーションのエントリポイントは `__main__.py` です。以下のコマンドで GUI を起動できます。
```bash
python __main__.py
```
デバッグ実行時は `Sampledata` クラスによってダミーデータが生成されます。通常は `DB_PATH` で指定したデータベースを利用します。

## ライセンス
このリポジトリは学習目的で公開されています。商用利用はご遠慮ください。
