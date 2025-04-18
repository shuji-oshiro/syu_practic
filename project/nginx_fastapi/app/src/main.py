# app/main.py
import sys
import os
import json
import pytz
import logging
import datetime
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, UploadFile, File
from analysis.analysis import process_csv_files

# データ保存用のディレクトリとファイルパス
DATA_DIR = "data"
LOG_DIR = "logs"
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
LOG_FOLDER = os.path.join(LOG_DIR)

# データディレクトリが存在しない場合は作成
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ログ設定をまとめて定義
LOG_CONFIG = {
    'dir': LOG_DIR,
    'level': logging.DEBUG,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S %Z',
    'timezone': 'Asia/Tokyo'
}

# ログディレクトリ作成
os.makedirs(LOG_CONFIG['dir'], exist_ok=True)

# ロギング設定を一括で行う
logging.basicConfig(
    level=LOG_CONFIG['level'],
    format=LOG_CONFIG['format'],
    datefmt=LOG_CONFIG['datefmt'],
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOG_CONFIG['dir'], 'app.log'))
    ]
)

# タイムゾーン設定
logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone(LOG_CONFIG['timezone'])).timetuple()
logger = logging.getLogger(__name__)


app = FastAPI()


# 商品データを読み込む関数
def load_products() -> Dict[str, dict]:
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 商品データを保存する関数
def save_products(products: Dict[str, dict]):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

class Product(BaseModel):
    product_code: str
    product_name: str
    sales_target: int

@app.get("/api/products")
async def get_products() -> List[dict]:
    """商品一覧を取得"""
    logger.debug("商品一覧を取得")
    products = load_products()
    return list(products.values())

@app.post("/api/products")
async def create_product(product: Product):
    """商品を登録"""
    logger.debug(f"商品を登録: {product}")
    products = load_products()
    
    if product.product_code in products:
        raise HTTPException(status_code=400, detail="商品コードが既に存在します")
    
    products[product.product_code] = product.dict()
    save_products(products)
    return {"message": "商品を登録しました"}

@app.delete("/api/products/{product_code}")
async def delete_product(product_code: str):
    """商品を削除"""
    logger.debug(f"商品を削除: {product_code}")
    products = load_products()
    
    if product_code not in products:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    
    del products[product_code]
    save_products(products)
    return {"message": "商品を削除しました"}

@app.post("/api/analyze")
async def analyze_files(files: List[UploadFile] = File(...)):
    """CSVファイルを分析"""
    logger.debug(f"分析リクエストを受信: {len(files)}個のファイル")
    return await process_csv_files(files)
