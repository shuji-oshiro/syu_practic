import pandas as pd
from fastapi import UploadFile
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def create_debug_csv_file(filename: str, data: dict) -> UploadFile:
    """
    デバッグ用のCSVファイルを作成する
    
    パラメータ:
    - filename: 作成するファイルの名前
    - data: データフレームのデータ（辞書形式）
    
    戻り値:
    - UploadFileオブジェクト
    """
    df = pd.DataFrame(data)
    content = df.to_csv(index=False).encode('utf-8')
    file = BytesIO(content)
    return UploadFile(
        filename=filename,
        file=file
    )

def get_debug_test_files() -> list[UploadFile]:
    """
    デバッグ用のテストファイルを作成する
    
    作成されるファイル:
    1. 通常のCSVファイル（3行のデータ）
    2. 異なる列を持つCSVファイル（2行のデータ）
    3. 空のCSVファイル
    4. 不正なCSVファイル（列数が一致しない）
    
    戻り値:
    - UploadFileオブジェクトのリスト
    """
    # 1. 通常のCSVファイル
    normal_data = {
        'product_code': ['A001', 'A002', 'A003'],
        'product_name': ['商品1', '商品2', '商品3'],
        'sales': [100, 200, 300],
        'quantity': [10, 20, 30]
    }
    normal_file = create_debug_csv_file('normal.csv', normal_data)
    
    # 2. 異なる列を持つCSVファイル
    different_columns_data = {
        'product_code': ['B001', 'B002'],
        'quantity': [40, 50]
    }
    different_columns_file = create_debug_csv_file('different_columns.csv', different_columns_data)
    
    # 3. 空のCSVファイル
    empty_df = pd.DataFrame()
    empty_content = empty_df.to_csv(index=False).encode('utf-8')
    empty_file = BytesIO(empty_content)
    empty_upload_file = UploadFile(
        filename="empty.csv",
        file=empty_file
    )
    
    # 4. 不正なCSVファイル
    invalid_content = b"column1,column2\n1,2,3\n4,5"  # 列数が一致しない
    invalid_file = BytesIO(invalid_content)
    invalid_upload_file = UploadFile(
        filename="invalid.csv",
        file=invalid_file
    )
    
    return [
        normal_file,
        different_columns_file,
        empty_upload_file,
        invalid_upload_file
    ] 