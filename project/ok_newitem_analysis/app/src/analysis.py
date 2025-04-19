import io
import sys
import pytz
import logging
import datetime
import pandas as pd
from typing import List
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
    
    for file in files:

        try:
            # ファイルの内容を読み込む
            content = await file.read()
            
            # CSVファイルの検証
            content_str = content.decode('utf-8')
            lines = content_str.splitlines()
            if not lines:
                logger.warning(f"ファイル {file.filename} は空です。")
                continue
            
            header = lines[0].split(',')
            for line in lines[1:]:
                if len(line.split(',')) != len(header):
                    raise ValueError("列数が一致しません")
            
            df = pd.read_csv(io.StringIO(content_str))
            if df.empty:
                logger.warning(f"ファイル {file.filename} は空です。")
                continue
            all_data.append(df)
            logger.debug(f"ファイル {file.filename} を読み込みました。行数: {len(df)}")
        except pd.errors.EmptyDataError:
            logger.warning(f"ファイル {file.filename} は空のCSVファイルです。")
            continue
        except Exception as e:
            logger.error(f"ファイル {file.filename} の処理中にエラーが発生しました: {str(e)}")
            raise HTTPException(status_code=400, detail=f"ファイル {file.filename} の形式が不正です: {str(e)}")
    
    if not all_data:
        return {
            "total_rows": 0,
            "total_files": len(files),
            "columns": [],
            "numeric_summary": {},
            "file_names": [file.filename for file in files]
        }
    
    try:
        # すべてのデータフレームを結合
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 基本的な集計処理
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
        logger.error(f"集計処理中にエラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=f"集計処理中にエラーが発生しました: {str(e)}") 

