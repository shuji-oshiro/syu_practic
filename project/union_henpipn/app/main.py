import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()

sales_data = pd.DataFrame()

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    global sales_data
    sales_data = pd.read_csv(file.file ,encoding="CP932", header=1) 
    
    sales_data = sales_data.rename(columns={"得意先コード":"t_code" ,"店舗名":"tenpo_name","商品名":"item_name","当年純売金額":"sales_amount", "当年純売数量":"sales_count", "当年返品金額":"re_amout", "当年返品数量":"re_count"})
    
    # 特定の得意先のみ抽出
    sales_data = sales_data[sales_data["t_code"] == 112000]
    stores = sales_data.groupby(["tenpo_name"]).sum(numeric_only=True).reset_index()
    stores = stores.loc[:, ['tenpo_name', "sales_amount", "sales_count", "re_amout", "re_count"]]

    stores_list = stores.to_dict(orient="records")

    return JSONResponse(content={"stores": stores.loc[:,"tenpo_name"].tolist()})

@app.get("/api/details")
async def store_details(store: str):
    
    store_data = sales_data[sales_data['tenpo_name'] == store]
    products = store_data.groupby('item_name').agg({
        're_amout': 'sum',
        're_count': 'sum'
    }).reset_index()
    
    products = products[products["re_amout"] > 0]
    products = products.sort_values("re_amout",ascending=False)

    return JSONResponse(content={"products": products.to_dict(orient='records')})
    