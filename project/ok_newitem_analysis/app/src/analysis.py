import io
import sys
import pytz
import json
import logging
import datetime
import pandas as pd
from typing import List
from pathlib import Path
from fastapi import UploadFile, HTTPException


# ロガーの作成
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# フォーマッターの設定
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)

# タイムゾーンを日本時間に設定
formatter.converter = lambda *args: datetime.datetime.now(pytz.timezone('Asia/Tokyo')).timetuple()

# テスト実行中でない場合のみファイルハンドラーを追加
if not sys.modules.get('pytest'):
    # ファイルハンドラーの作成
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# コンソールハンドラーは常に追加
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


async def process_csv_files(files: List[UploadFile]) -> dict:
    """
    複数のCSVファイルを処理し、集計結果を返す
    """
    all_data = []
    error_status = 0
    
    for file in files:
        try:
            # ファイルの内容を読み込む
            content = await file.read()
            content_str = content.decode('utf-8')
            
            # CSVファイルの検証
            df = pd.read_csv(io.StringIO(content_str))
            
            # 空のデータフレームチェック
            if df.empty:
                logger.warning(f"売上情報ファイル {file.filename} は空です")
                error_status = 1
                return {"error_status": error_status}

            # 必須カラムの存在チェック
            required_columns = ['取引先コード', '取引先名', '商品コード', '商品名', '店舗名', '売上金額', '売上数量']
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"売上情報ファイル {file.filename} に必要なカラムが不足しています: {col}")
                    error_status = 2
                    return {"error_status": error_status} 

            # データ型の検証
            try:
                df['売上金額'] = pd.to_numeric(df['売上金額'])
                df['売上数量'] = pd.to_numeric(df['売上数量'])
            except ValueError:
                logger.error(f"売上情報ファイル {file.filename} の数値データが不正です")
                error_status = 3
                return {"error_status": error_status}


            all_data.append(df)
            logger.debug(f"売上情報ファイル {file.filename} を読み込みました。行数: {len(df)}")

        except Exception as e:
            logger.error(f"売上情報ファイル {file.filename} の読み込み処理中にエラーが発生しました: {str(e)}")
            error_status = 4
            return {"error_status": error_status}

    try:
        # すべてのデータフレームを結合
        combined_df = pd.concat(all_data, ignore_index=True)  


       # 抽出条件となる商品コードを取得
        # テスト実行中のみファイルハンドラーで処理
        if sys.modules.get('pytest'):
            json_path = Path(__file__).parent.parent / "data" / "products.json"
        else:  
            json_path = "data/products.json"

        # フィルタ条件をリスト化
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        df = pd.DataFrame(json_data.values())

        combined_df = combined_df.loc[
            combined_df['商品コード'].astype(str).isin(df['product_code'].astype(str))
        ]

        # 取引先・商品ごとの集計
        summary_by_client_product = combined_df[combined_df['売上金額'] > 0].groupby(
            ['取引先コード', '取引先名', '商品コード', '商品名']
            ).agg({
                '売上金額': 'sum',
                '売上数量': 'sum',
                '店舗名': lambda x: x.nunique()  # 店舗数をカウント
            }).reset_index()

        # 取引先・商品ごとの集計
        summary_by_product = combined_df[combined_df['売上金額'] > 0].groupby(
            ['商品コード']
        ).agg({
            '売上金額': 'sum',
            '売上数量': 'sum',
            '店舗名': lambda x: x.nunique()  # 店舗数をカウント
        }).reset_index()

        
        summary_by_product = pd.merge(
            df.assign(product_code=df["product_code"].astype(str)),
            summary_by_product.assign(商品コード=summary_by_product["商品コード"].astype(str)),
            on=None, left_on="product_code", right_on="商品コード", how="inner"
        )
        summary_by_product["達成率"] = summary_by_product["売上金額"] / summary_by_product["sales_target"]

        summary_by_product.rename(columns={"product_name": "商品名", "sales_target": "目標値"}, inplace=True)  


        # 売上金額の降順でソート
        summary_by_client_product = summary_by_client_product.sort_values(by='売上金額', ascending=False)

        return {
            "error_status": error_status,
            "summary_by_product": summary_by_product.to_json(orient='records', force_ascii=False),
            "summary_by_client_product": summary_by_client_product.to_json(orient='records', force_ascii=False)
            
        }

    except Exception as e:
        logger.error(f"集計処理中にエラーが発生しました: {str(e)}")
        return {"error_status": 5}
    

