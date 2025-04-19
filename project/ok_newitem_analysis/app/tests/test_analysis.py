import pytest
import pandas as pd
from io import BytesIO
from pathlib import Path
from fastapi import UploadFile
from app.src.analysis import process_csv_files


@pytest.mark.asyncio
async def test_process_csv_files():
    """CSVファイル処理のテスト"""
    # テストデータファイルのパス設定
    test_data_dir = Path(__file__).parent / "testdata"
    
    # 正常系テスト - 複数ファイル
    sample1_path = test_data_dir / "sample1.csv"
    sample2_path = test_data_dir / "sample2.csv"
    
    with open(sample1_path, "rb") as f1, open(sample2_path, "rb") as f2:
        file1 = UploadFile(filename="sample1.csv", file=BytesIO(f1.read()))
        file2 = UploadFile(filename="sample2.csv", file=BytesIO(f2.read()))
        
        result = await process_csv_files([file1, file2])
        
        assert result["error_status"] == 0
        assert len(result["summary_by_client_product"]) > 0

    # 空ファイルテスト
    empty_path = test_data_dir / "empty.csv"
    with open(empty_path, "rb") as f:
        empty_file = UploadFile(filename="empty.csv", file=BytesIO(f.read()))
        result = await process_csv_files([empty_file])
        assert result["error_status"] == 1

    # ファイルに必要なカラムが不足しているテスト
    missing_columns_path = test_data_dir / "missing_columns.csv"
    with open(missing_columns_path, "rb") as f:
        missing_columns_file = UploadFile(filename="missing_columns.csv", file=BytesIO(f.read()))
        result = await process_csv_files([missing_columns_file])
        assert result["error_status"] == 2

    # 数値が不正なテスト
    invalid_numeric_path = test_data_dir / "invalid.csv"
    with open(invalid_numeric_path, "rb") as f:
        invalid_numeric_file = UploadFile(filename="invalid_numeric.csv", file=BytesIO(f.read()))
        result = await process_csv_files([invalid_numeric_file])
        assert result["error_status"] == 3


    # 大規模データテスト
    sample3_path = test_data_dir / "sample3.csv" 
    with open(sample3_path, "rb") as f:
        large_file = UploadFile(filename="sample3.csv", file=BytesIO(f.read()))
        result = await process_csv_files([large_file])
        assert result["error_status"] == 0
        assert len(result["summary_by_client_product"]) > 0




