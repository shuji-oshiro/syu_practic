import io
import sys
import asyncio
import logging
import pandas as pd
from typing import List
from conftest import DEBUG  # config.pyからDEBUGをインポート
from fastapi import UploadFile, HTTPException
from app.tests.debug_utils import get_debug_test_files

# ロガーの設定
logger = logging.getLogger(__name__)

async def process_csv_files(files: List[UploadFile] = None) -> dict:
    """
    複数のCSVファイルを処理し、集計結果を返す
    
    実装されている機能:
    1. 複数のCSVファイルの読み込みと検証
    2. 空のCSVファイルの処理
    3. 不正なCSVファイルの検出とエラー処理
    4. データフレームの結合と集計
    5. 数値データの基本統計量の計算
    
    パラメータ:
    - files: 処理するCSVファイルのリスト（FastAPIのUploadFileオブジェクト）
            デバッグモード時はNoneを指定するとテストデータが使用される
    
    戻り値:
    - 集計結果を含む辞書
      - total_rows: 全データの行数
      - total_files: 処理したファイル数
      - columns: 全データの列名リスト
      - numeric_summary: 数値データの基本統計量
      - file_names: 処理したファイル名のリスト
    """
    
    all_data = []
    
    for file in files:
        try:
            # ファイルの内容を読み込む
            content = await file.read()
            
            # CSVファイルの検証
            # 1. ファイルが空でないか確認
            content_str = content.decode('utf-8')
            lines = content_str.splitlines()
            if not lines:
                logger.warning(f"ファイル {file.filename} は空です。")
                continue
            
            # 2. 各行の列数が一致するか確認
            header = lines[0].split(',')
            for i, line in enumerate(lines[1:], 1):
                if len(line.split(',')) != len(header):
                    logger.error(f"ファイル {file.filename} の {i+1} 行目で列数が一致しません")
                    raise ValueError("列数が一致しません")
            
            # 3. pandasを使用してCSVをデータフレームに変換
            df = pd.read_csv(io.StringIO(content_str))
            if df.empty:
                logger.warning(f"ファイル {file.filename} は空です。")
                continue
            all_data.append(df)
            logger.debug(f"ファイル {file.filename} を読み込みました。行数: {len(df)}")
        except pd.errors.EmptyDataError:
            # 4. 空のCSVファイルのエラー処理
            logger.warning(f"ファイル {file.filename} は空のCSVファイルです。")
            continue
        except Exception as e:
            # 5. その他のエラー処理（不正なCSVファイルなど）
            logger.error(f"ファイル {file.filename} の処理中にエラーが発生しました: {str(e)}")
            raise HTTPException(status_code=400, detail=f"ファイル {file.filename} の形式が不正です: {str(e)}")
    
    # 6. 有効なデータがない場合の処理
    if not all_data:
        return {
            "total_rows": 0,
            "total_files": len(files),
            "columns": [],
            "numeric_summary": {},
            "file_names": [file.filename for file in files]
        }
    
    try:
        # 7. すべてのデータフレームを結合
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 8. 基本的な集計処理
        summary = {
            "total_rows": len(combined_df),
            "total_files": len(files),
            "columns": list(combined_df.columns),
            "numeric_summary": combined_df.describe().to_dict() if combined_df.select_dtypes(include=['number']).columns.any() else {},
            "file_names": [file.filename for file in files]
        }
        
        logger.debug(f"集計処理が完了しました。総行数: {summary['total_rows']}")
        return summary
    except Exception as e:
        # 9. 集計処理中のエラー処理
        logger.error(f"集計処理中にエラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=f"集計処理中にエラーが発生しました: {str(e)}")

# デバッグモード時のテスト実行
if __name__ == "__main__":
    # config.pyから取得したDEBUGの値を使用
    if DEBUG:
        # デバッグモード時はテストデータを使用
        logger.info("デバッグモード: テストデータを使用します")
        files = get_debug_test_files()
        async def run_debug():
            result = await process_csv_files(files)
            print("処理結果:", result)
        
        asyncio.run(run_debug())