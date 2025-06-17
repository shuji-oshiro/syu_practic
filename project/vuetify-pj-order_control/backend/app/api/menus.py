import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from backend.app.schemas.menu_schema import MenusOut
from backend.app.crud import menu_crud

router = APIRouter()

# メニュー登録と取得のエンドポイント
@router.post("/", response_model=List[MenusOut])
async def input_menus_data(file: UploadFile = File(...)):
    try:
        temp_path = "temp.csv"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        menu_crud.insert_menus_from_csv(temp_path)
        os.remove(temp_path)
        return menu_crud.get_menus()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー登録エラー: {str(e)}")

# メニュー取得のエンドポイント
@router.get("/", response_model=List[MenusOut])
async def get_menus(menu_id: Optional[int] = None):
    try:
        return menu_crud.get_menus(menu_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー取得エラー: {str(e)}")
