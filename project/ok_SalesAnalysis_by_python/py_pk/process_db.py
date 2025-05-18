# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:55:47 2025
共通データベースより売上情報の取得や更新を行う処理
@author: mkt05
"""
import os
import sqlite3
import logging
import pandas as pd
from py_pk.settings import Settings

COL_CSVTODB_DAY = {'得意先コード': 't_code',"ラインコード":"l_code","商品コード":"i_code","商品名":"i_name"}

# ログの設定
logging.basicConfig(
    filename='logfile/debug.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # エンコーディングを指定
)

print(Settings.DB_PATH)

class Process_db:    
    def __init__(self):        
        """
        初期処理　

        Returns
        -------
        None.

        """

    
    
    @classmethod      
    def Get_salesData(cls) -> pd.DataFrame:
        df = pd.DataFrame()      
        try:  
            # データベース接続 

            with sqlite3.connect(Settings.DB_PATH) as conn:
                df = pd.read_sql(f"SELECT * FROM sales_data", conn)
            
            return df            
        except Exception:               
            logging.exception(Exception)
            raise  

    @classmethod
    def Get_master(cls,tbl_name):        
        df = pd.DataFrame()  
        try:  
            # データベース接続
            with sqlite3.connect(Settings.DB_PATH) as conn:
                df = pd.read_sql(f"SELECT * FROM {tbl_name}", conn)
                          
            return df            
        except Exception:               
            logging.exception(Exception)
            raise
    
    @classmethod
    def Update_db(cls, df):
        """
        内部関数　DBの売上情報を更新する処理

        Parameters
        ----------
        df_a : TYPE
            DESCRIPTION.
        df_b : TYPE
            DESCRIPTION.
        tblName : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
                
        try:           
            with  sqlite3.connect(Settings.DB_PATH) as conn : 
                df.to_sql("sales_data", conn, if_exists="replace", index=None)
                conn.commit()            
            return df
            
        except Exception:              
            logging.exception(Exception)  
            raise  
           
    @classmethod
    def _read_salesinfo_day(cls,fle):
        """
        売上情報の読み
    
        Parameters
        ----------
        fle : tuple
            DESCRIPTION.
    
        Returns
        -------
        TYPE
            DESCRIPTION.
    
        """
        try:        
            df = pd.DataFrame()             
            
            for f in fle:
                # １行目の年月情報の文字列を取得しDate型の情報に変換する
                temp = pd.read_csv(f,encoding="CP932",header=None,nrows=1)                
                time_val = temp[0][0].split("　")[0].split(":")[1].split("～")            
                dt_year = time_val[0][:5]
                                        
                temp = pd.read_csv(f ,encoding="CP932", header=1) 
                    
                head_data = temp[["得意先コード","ラインコード","商品コード","商品名"]].rename(columns = COL_CSVTODB_DAY)
                               
                flg = True
                sales_data = temp.filter(like=f"納品金額{dt_year}", axis=1)   
                henpin_data = temp.filter(like=f"返品金額{dt_year}", axis=1)  
                
                
                for col, col2 in zip(sales_data.columns, henpin_data.columns):
                    copy_data = head_data.copy() 
                    copy_data["day"] = col[4:8]+col[9:11]+col[12:14]
                    
                    copy_data["amount"] = sales_data.loc[:,col] - henpin_data.loc[:,col2]

                                        
                    df = pd.concat([df,copy_data]) # 追加するデータフレームを結合

                    
                            
            #　欠損値を更新            
            df = df.fillna({"t_code":-1,"l_code":-1,"i_name":"その他","amount":0})    
            df = df[df["amount"]>0] 
            
            return df       
            
        except Exception: 
            logging.exception(Exception)       
            raise      
        
    
        
