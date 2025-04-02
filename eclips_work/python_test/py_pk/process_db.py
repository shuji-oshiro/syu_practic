# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:55:47 2025
共通データベースより売上情報の取得や更新を行う処理
@author: mkt05
"""

import pandas as pd
import sqlite3
import logging
from py_pk.settings import Settings

COL_CSVTODB_DAY = {'得意先コード': 't_code',"ラインコード":"l_code","商品コード":"i_code","商品名":"i_name"}

logging.basicConfig(filename='logfile/logger.log', level=logging.ERROR)

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
    def Update_db(cls, df, tblName):
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
                df.to_sql(tblName, conn, if_exists="replace", index=None)
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
                
                sales_data = temp.filter(like=f"納品金額{dt_year}", axis=1)   
                henpin_data = temp.filter(like=f"返品金額{dt_year}", axis=1)  
                
                index = 0
                for col in sales_data.columns:
                                     
                    head_data["day"] = col[4:8]+col[9:11]+col[12:14]
                    head_data2 = head_data.copy()
                    
                    head_data["kind"] = "1"
                    head_data2["kind"] = "0"
                    
                    head_data["amount"] = sales_data.iloc[:,index]
                    head_data2["amount"] = henpin_data.iloc[:,index]
                       
                    # 日別の売上情報は数量が存在しなしので0を設定
                    head_data["count"] = 0
                    head_data2["amount"] = 0
                                        
                    df = pd.concat([df,head_data.query("amount>0"),head_data2.query("amount>0")]) 
                    
                    index += 1
                            
            #　欠損値を更新            
            df = df.fillna({"t_code":-1,"l_code":-1,"i_name":"その他","amount":0})    
            df = df[df["amount"]>0] 
            
            return df       
            
        except Exception: 
            logging.exception(Exception)       
            raise      
        
    
        
