import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from backend.app.schemas.menu_schema import MenuOut, MenuIn, MenuUpdate
from backend.app.crud import menu_crud

router = APIRouter()

# メニュー登録と取得のエンドポイント
@router.post("/", response_model=List[MenuOut])
async def input_menus_data(file: UploadFile = File(...)):
    try:
        temp_path = "temp.csv"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        menu_crud.import_menus_from_csv(temp_path)
        os.remove(temp_path)
        return menu_crud.get_menus()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー登録エラー: {str(e)}")


# メニュー取得のエンドポイント
@router.get("/", response_model=List[MenuOut])
async def get_menus(menu_id: Optional[int] = None):
    try:
        return menu_crud.get_menus(menu_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー取得エラー: {str(e)}")


# メニュー追加のエンドポイント
@router.put("/", response_model=List[MenuOut])
async def add_menus(menu: MenuIn):
    try:
        return menu_crud.add_menu(menu)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー追加エラー: {str(e)}")


# メニュー更新のエンドポイント
@router.patch("/", response_model=List[MenuOut])
async def update_menus(menu: MenuUpdate):
    try:
        return menu_crud.update_menu(menu)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー更新エラー: {str(e)}")


# メニュー削除のエンドポイント
@router.delete("/", response_model=List[MenuOut])
async def delete_menus(menu_id: Optional[int] = None):
    try:
        return menu_crud.delete_menu(menu_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メニュー取得エラー: {str(e)}")

