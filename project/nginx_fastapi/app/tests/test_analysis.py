import os
import sys
import pytz
import pytest
import datetime
import logging
import pandas as pd
from io import BytesIO
from fastapi import UploadFile, HTTPException

# プロジェクトのルートディレクトリをPythonパスに追加
# これにより、テスト実行時にプロジェクトのモジュールを正しくインポートできるようになります
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 絶対インポートを使用
from app.src.analysis import process_csv_files

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log')
    ]
)
# タイムゾーンを日本時間に設定
logging.Formatter.converter = lambda *args: datetime.datetime.now(pytz.timezone('Asia/Tokyo')).timetuple()
logger = logging.getLogger(__name__)

@pytest.fixture
def sample_csv_content():
    """
    テスト用のCSVデータを作成するフィクスチャ
    
    作成されるデータ:
    - product_code: 商品コード（A001, A002, A003）
    - product_name: 商品名（商品1, 商品2, 商品3）
    - sales: 売上（100, 200, 300）
    - quantity: 数量（10, 20, 30）
    
    戻り値:
    - CSVデータのバイト列（UTF-8エンコード）
    """
    data = {
        'product_code': ['A001', 'A002', 'A003'],
        'product_name': ['商品1', '商品2', '商品3'],
        'sales': [100, 200, 300],
        'quantity': [10, 20, 30]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

@pytest.fixture
def sample_csv_file(sample_csv_content):
    """
    テスト用のUploadFileオブジェクトを作成するフィクスチャ
    
    パラメータ:
    - sample_csv_content: 別のフィクスチャから取得したCSVデータ
    
    戻り値:
    - FastAPIのUploadFileオブジェクト（ファイル名: test.csv）
    """
    file = BytesIO(sample_csv_content)
    return UploadFile(
        filename="test.csv",
        file=file
    )

@pytest.mark.asyncio
async def test_process_single_csv_file(sample_csv_file):
    """
    単一のCSVファイルを処理するテスト
    
    テスト内容:
    1. 単一のCSVファイルを処理できることを確認
    2. 処理結果の各フィールドが正しいことを検証
       - total_files: 1
       - total_rows: 3
       - columns: 正しい列名が含まれているか
       - numeric_summary: 数値列（sales, quantity）の基本統計量が含まれているか
    """
    logger.info("単一CSVファイルの処理テストを開始")
    result = await process_csv_files([sample_csv_file])
    
    assert result['total_files'] == 1
    assert result['total_rows'] == 3
    assert set(result['columns']) == {'product_code', 'product_name', 'sales', 'quantity'}
    assert 'numeric_summary' in result
    assert 'sales' in result['numeric_summary']
    assert 'quantity' in result['numeric_summary']
    logger.info("単一CSVファイルの処理テストが完了")

@pytest.mark.asyncio
async def test_process_multiple_csv_files(sample_csv_file):
    """
    複数のCSVファイルを処理するテスト
    
    テスト内容:
    1. 複数のCSVファイルを処理できることを確認
    2. 2つ目のファイルを作成（異なるデータ）
    3. 両方のファイルを処理し、結果を検証
       - total_files: 2
       - total_rows: 5（3行 + 2行）
       - file_names: 両方のファイル名が含まれているか
    """
    logger.info("複数CSVファイルの処理テストを開始")
    # 2つ目のファイルを作成
    data2 = {
        'product_code': ['B001', 'B002'],
        'product_name': ['商品4', '商品5'],
        'sales': [400, 500],
        'quantity': [40, 50]
    }
    df2 = pd.DataFrame(data2)
    content2 = df2.to_csv(index=False).encode('utf-8')
    file2 = BytesIO(content2)
    upload_file2 = UploadFile(
        filename="test2.csv",
        file=file2
    )
    
    result = await process_csv_files([sample_csv_file, upload_file2])
    
    assert result['total_files'] == 2
    assert result['total_rows'] == 5
    assert len(result['file_names']) == 2
    logger.info("複数CSVファイルの処理テストが完了")

@pytest.mark.asyncio
async def test_process_empty_csv():
    """
    空のCSVファイルを処理するテスト
    
    テスト内容:
    1. 空のCSVファイルを処理できることを確認
    2. 空のデータフレームからCSVを作成
    3. 処理結果を検証
       - total_files: 1
       - total_rows: 0
       - columns: 空のリスト
    """
    logger.info("空CSVファイルの処理テストを開始")
    empty_df = pd.DataFrame()
    empty_content = empty_df.to_csv(index=False).encode('utf-8')
    empty_file = BytesIO(empty_content)
    upload_file = UploadFile(
        filename="empty.csv",
        file=empty_file
    )
    
    result = await process_csv_files([upload_file])
    
    assert result['total_files'] == 1
    assert result['total_rows'] == 0
    assert len(result['columns']) == 0
    logger.info("空CSVファイルの処理テストが完了")

@pytest.mark.asyncio
async def test_process_invalid_csv():
    """
    不正なCSVファイルを処理するテスト
    
    テスト内容:
    1. 列数が一致しない不正なCSVファイルを作成
    2. 処理時にHTTPExceptionが発生することを確認
    3. エラーのステータスコードとメッセージを検証
    """
    logger.info("不正なCSVファイルの処理テストを開始")
    invalid_content = b"column1,column2\n1,2,3\n4,5"  # 列数が一致しない不正なCSVデータ
    invalid_file = BytesIO(invalid_content)
    upload_file = UploadFile(
        filename="invalid.csv",
        file=invalid_file
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await process_csv_files([upload_file])
    assert exc_info.value.status_code == 400
    assert "形式が不正です" in str(exc_info.value.detail)
    logger.info("不正なCSVファイルの処理テストが完了")

@pytest.mark.asyncio
async def test_process_csv_with_different_columns():
    """
    異なる列を持つCSVファイルを処理するテスト
    
    テスト内容:
    1. 異なる列を持つ2つのCSVファイルを作成
       - 1つ目: product_code, sales
       - 2つ目: product_code, quantity
    2. 両方のファイルを処理し、結果を検証
       - total_files: 2
       - columns: 両方のファイルの列が含まれているか
       - total_rows: 4（2行 + 2行）
    """
    logger.info("異なる列を持つCSVファイルの処理テストを開始")
    # 1つ目のファイル
    data1 = {
        'product_code': ['A001', 'A002'],
        'sales': [100, 200]
    }
    df1 = pd.DataFrame(data1)
    content1 = df1.to_csv(index=False).encode('utf-8')
    file1 = BytesIO(content1)
    upload_file1 = UploadFile(
        filename="test1.csv",
        file=file1
    )
    
    # 2つ目のファイル（異なる列）
    data2 = {
        'product_code': ['B001', 'B002'],
        'quantity': [10, 20]
    }
    df2 = pd.DataFrame(data2)
    content2 = df2.to_csv(index=False).encode('utf-8')
    file2 = BytesIO(content2)
    upload_file2 = UploadFile(
        filename="test2.csv",
        file=file2
    )
    
    result = await process_csv_files([upload_file1, upload_file2])
    
    assert result['total_files'] == 2
    assert set(result['columns']) == {'product_code', 'sales', 'quantity'}
    assert result['total_rows'] == 4
    logger.info("異なる列を持つCSVファイルの処理テストが完了") 