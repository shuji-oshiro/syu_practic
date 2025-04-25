import json
import pytest
#import pandas as pd
#from io import BytesIO
#from pathlib import Path
#from fastapi import UploadFile
#from src.main import get_tasks

# @pytest.mark.asyncio
# async def test_get_tasks():
    
#     """CSVファイル処理のテスト"""
#     # テストデータファイルのパス設定
#     test_data_dir = Path(__file__).parent / "testdata"
    
#     # タスク一覧取得
#     response = await get_tasks()
#     assert response.status_code == 200
#     assert len(response.json()) > 0


def test_get_tasks(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)