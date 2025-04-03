'''
Created on 2025/03/19

@author: mkt05
'''

import pandas as pd
from py_pk.settings import Settings
from py_pk.process_db import Process_db
from py_pk.sampledata import Sampledata
import logging
from tkinter import messagebox as msg
from datetime import datetime as dt
import sys

logging.basicConfig(filename='logfile/logger.log', level=logging.ERROR)

class Analysis_data:
    '''
    classdocs
    '''
    def __init__(self):        
        
        if sys.gettrace() is not None:  # デバッグ実行コード
            self.df, self.df_brand, self.df_line = Sampledata.CreateSalesData()
        else:        
            df = Process_db.Get_salesData()
            # データ型を変換
            self.df = df.astype({col: dtype for col, dtype in Settings.DIC_AS_TYPES.items() if col in df.columns})
            
            self.df_brand = Process_db.Get_master(Settings.TBLNAME_BRAND)
            self.df_line = Process_db.Get_master(Settings.TBLNAME_LINE)
        
        self.pre_charts = {
            'timeseries': [],
            'histogram': [],
            'scatterplot': []
        }                
           
            
    def get_datacondition(self, brand=None, line=None, items=None, from_date=None, to_date=None, target_week=None, flg_without=False):
        """
        Filter and process sales data based on various criteria.
        
        Args:
            brand (str): Brand name filter
            line (str): Line name filter
            items (list): List of item names to filter
            from_date (datetime): Start date for filtering
            to_date (datetime): End date for filtering
            target_week (list): List of weekday numbers to filter
        
        Returns:
            pd.DataFrame: Filtered and processed dataframe
        """
        try:
            
            df_out = self.df.copy()
            df_out = df_out.merge(self.df_brand, on='t_code', how='left').fillna("その他取引先")
            df_out = df_out.merge(self.df_line, on='l_code', how='left').fillna("その他ライン")
    
            # Apply filters
            if brand:
                df_out = df_out[df_out["t_name"] == brand]
            
            if line:
                df_out = df_out[df_out["l_name"] == line]
                        
            if flg_without: #和菓子の売上を除く処理
                df_out = df_out[~df_out["l_code"].isin([Settings.CODE_WAGASHI])]               
                
            if items:
                # 商品コードと商品名が一致していない状況があるので、組み合わせで抽出する
                df_out["i_name_and_i_code"] = df_out['i_code'].astype(str).str.cat(df_out['i_name'], sep=',')
                df_out = df_out[df_out["i_name_and_i_code"].isin(items)]                
                       

            # 日付文字列データをDateTimeに変換
            df_out["day_DateTime"] = pd.to_datetime(df_out["day"], format=Settings.FORMAT_YMD)
                                            
            # Date range filter    
            df_out = df_out[(df_out["day_DateTime"] >= from_date) & (df_out["day_DateTime"] <= to_date)]
                        
            # Week filter
            if target_week:
                df_out = df_out.set_index("day_DateTime")
                df_out = df_out[df_out.index.weekday.isin(target_week)]
                df_out = df_out.reset_index(drop=False)
        
            return df_out
        
        except Exception:
            logging.exception(Exception)
            raise
    
    def update_salesData(self, fle) -> bool:
        
        try:
            df_base = self.df
            df = Process_db._read_salesinfo_day(fle)
            df_add = df.astype({col: dtype for col, dtype in Settings.DIC_AS_TYPES.items() if col in df.columns})
            
            
            # 同日付の売上情報が含まれている場合
            a = df_add["day"]
            b = df_base["day"]
            c = set(a) & set(b)
                        
            if len(c) > 0:                  
                msgVal = sorted(c)                        
                message_text = "\n".join([str(msgVal[0]),"～",str(msgVal[-1])])
                
                flg_answer = msg.askyesnocancel(msg.INFO,f"同日付の売上情報が含まれています。更新しますか？\n{message_text}")
                
                if flg_answer is None:
                    msg.showinfo(msg.INFO, "売上情報の更新処理を中断しました。")
                    return pd.DataFrame()
                
                elif flg_answer: 
                    df_base = df_base[~df_base["day"].isin(c)] #元のデータを活かす   
                else: 
                    df_add = df_add[~df_add["day"].isin(c)] #新たに読み込みしたデータを活かす

            df_new = pd.concat([df_add, df_base])            
            
            self.df = Process_db.Update_db(df_new)

        except Exception:
            logging.exception(Exception)            
            raise          
    
    def get_from_and_to(self):
        _from = dt.strptime(str(min(self.df["day"].unique())), Settings.FORMAT_YMD)
        _to = dt.strptime(str(max(self.df["day"].unique())), Settings.FORMAT_YMD)
        
        return _from, _to
        
        
    