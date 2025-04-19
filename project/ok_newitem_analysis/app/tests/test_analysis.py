import pytest
import pandas as pd
from io import BytesIO
from fastapi import UploadFile
from app.src.analysis import process_csv_files

@pytest.mark.asyncio
async def test_process_csv_files():
    # テストデータの作成
    csv_data1 = "商品コード,商品名,売上目標,売上実績\nA001,商品A,1000,1200\nA002,商品B,2000,1800\n"
    csv_data2 = "商品コード,商品名,売上目標,売上実績\nB001,商品D,3000,3500\nB002,商品E,2500,2300\n"
    
    # UploadFileオブジェクトの作成
    file1 = UploadFile(
        file=BytesIO(csv_data1.encode()),
        filename="test_data1.csv"
    )
    file2 = UploadFile(
        file=BytesIO(csv_data2.encode()),
        filename="test_data2.csv"
    )
    
    # 関数の実行
    result = await process_csv_files([file1, file2])
    
    # 結果の検証
    assert result["total_rows"] == 4
    assert result["total_files"] == 2
    assert "商品コード" in result["columns"]
    assert "売上実績" in result["columns"]
    assert "numeric_summary" in result


