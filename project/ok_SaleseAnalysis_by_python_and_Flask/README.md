# ok_SaleseAnalysis_by_python_and_Flask

Web上でCSV販売データを集計・表示するFlaskアプリです。jQueryとDataTablesを使い、受け取ったデータをドリルダウン表示できます。

## 紹介

* CSVファイルから、売上情報とコース情報をアップロード
* 「チェーン店別」「コース別」「商品別」の3種類の集計ビューを切り替え
* 上位から下位へテーブルをクリックしてドリルダウン
* DataTablesによる表形式表示でソートやスクロールなどに対応
* データアップロード後、ビュー変更時に実行する初期化処理

## ファイル構成

```
project/ok_SaleseAnalysis_by_python_and_Flask/
├── app.py                # Flask 本体
├── Dockerfile            # Docker 構築用
├── requirements.txt      # Python依存
├── templates/
│   └── index.html        # フロント端
├── static/
│   └── css/style.css     # CSS
├── disp_customer_code.csv   # 受発売客コード組み
├── cours_info.json          # コース情報の統合
└── readme                # 日本語の概観
```

## 動作環境

Python 3.11 以上で動作するよう作っています。Docker を使った展開も可能です。

### Docker で起動

```bash
docker build -t sales_ana .
docker run -p 5000:5000 sales_ana
```

### ローカル実行

```bash
pip install -r requirements.txt
python app.py
```

起動後に http://localhost:5000 へアクセスすると画面が表示されます。

## 使い方

1. 「売上情報の読み込み」ボタンから売上CSVをアップロード
2. 「コース情報更新」ボタンからコースCSVを読み込み
3. ラジオボタンで表示したい集計ビューを選択
4. テーブルの行をクリックし、下位情報をドリルダウン

## ライセンス

学習用のサンプルコードです。商用利用は控えてください。

