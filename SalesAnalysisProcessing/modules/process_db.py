# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:55:47 2025
共通データベースより売上情報の取得や更新を行う処理
@author: mkt05
"""

import pandas as pd
import sqlite3
import logging
from tkinter import messagebox as msg

SUCCESS = 1
ERROR = -1
CANCEL = 0 

TBLNAME_DAY = "sales_day"
TBLNAME_WEEK = "sales_week"
TBLNAME_MONTH = "sales_month"
TBLNAME_BRAND = "mst_brand"
TBLNAME_LINE = "mst_line"
TBLNAME_TENPO = "mst_tenpo"


USECOLS_WEEK = ["得意先コード", "店舗コード", "ラインコード", "商品コード", "商品名", "当年純売金額", "当年純売数量"]
USECOLS_MONTH = ["得意先コード","ラインコード","商品コード","商品名","当年純売金額","当年純売数量"]

COL_CSVTODB_DAY = {'得意先コード': 't_code',"ラインコード":"l_code","商品コード":"i_code","商品名":"i_name"}
COL_CSVTODB_WEEK = {'得意先コード':'t_code',"店舗コード":"ten_code", "ラインコード":"l_code", "商品コード":"i_code", "商品名":"i_name", "当年純売金額":"amount", "当年純売数量":"count"}
COL_CSVTODB_MONTH = {'得意先コード':'t_code', "ラインコード":"l_code", "商品コード":"i_code", "商品名":"i_name", "当年純売金額":"amount", "当年純売数量":"count"}


class Process_db():
    
    def __init__(self):
        
        self.DB_PATH = r"\\okisvrm1\各部署\パン部門\TestDB\SalesInfo.db"
        
        try:  
            # データベース接続
            with sqlite3.connect(self.DB_PATH) as conn:
                self.df_db_day = pd.read_sql(f"SELECT * FROM {TBLNAME_DAY}", conn)
                self.df_db_week = pd.read_sql(f"SELECT * FROM {TBLNAME_WEEK}", conn)
                self.df_db_month = pd.read_sql(f"SELECT * FROM {TBLNAME_MONTH}", conn)                
                self.df_brand = pd.read_sql(f"SELECT * FROM {TBLNAME_BRAND}", conn)
                self.df_line = pd.read_sql(f"SELECT * FROM {TBLNAME_LINE}", conn)
                self.df_tenpo = pd.read_sql(f"SELECT * FROM {TBLNAME_TENPO}", conn)

            if len(self.df_db_day["day"]) > 0:
                self.from_day = self.df_db_day["day"].min()
                self.to_day = self.df_db_day["day"].max()           
            else:
                self.from_day = None
                self.to_day = None                  
            
        except Exception:               
            erMsg = "初期処理実行中にエラーが発生しました。"
            logging.exception(erMsg)

    
    def __update_salesinfo(self, df_a, df_b, tblName)->bool:
                
        try:
            
            # 同日付の売上情報が含まれている場合
            a = df_a["day"].tolist()
            b = df_b["day"].tolist()
            
            c = set(a) & set(b)
            
            if len(c) > 0:                  
                msgVal = sorted(c)                        
                message_text = "\n".join([msgVal[0],"～",msgVal[-1]])
                
                flg_answer = msg.askyesnocancel(msg.INFO,f"同日付の売上情報が含まれています。更新しますか？\n{message_text}")
                
                if flg_answer is None:
                    msg.showinfo(msg.INFO, "売上情報の更新処理を中断しました。")
                    return CANCEL
                
                elif flg_answer:
                    df_b = df_b[~df_b["day"].isin(c)]      
                    
                else:
                    df_a = df_a[~df_a["day"].isin(c)] 
                    
            df_c = pd.concat([df_a, df_b])            
            
            with  sqlite3.connect(self.DB_PATH) as conn :      
                    df_c.to_sql(tblName,conn,if_exists="replace",index=None)
                    conn.commit()
            
            return SUCCESS
            
        except Exception:               
            erMsg = "売上情報更新中にエラーが発生しました"
            logging.exception(erMsg)            
            return ERROR


    def read_salesinfo_week(cls, fle:tuple):
        try:                        
            df_in = pd.DataFrame()
            
            for f in fle:
                # １行目の年月情報の文字列を取得しDate型の情報に変換する
                temp = pd.read_csv(f,encoding="CP932",header=None,nrows=1)                
                time_val = temp[0][0].split("　")[0].split(":")[1].split("～")            
                dt_year_and_mont = time_val[0][:8]
                                        
                temp = pd.read_csv(f ,encoding="CP932", header=1 ,usecols=USECOLS_WEEK) 
                temp["day"] = dt_year_and_mont
                                
                df_in = pd.concat([df_in, temp]) 
                                
            df_in = df_in.rename(columns = COL_CSVTODB_WEEK)
        
            #　欠損値を更新            
            df_in = df_in.fillna({"t_code":-1,"l_code":-1,"i_name":"その他","amount":0})    
            
            return cls.__update_salesinfo(df_in, cls.df_db_week, TBLNAME_WEEK)
                            
            
        except Exception: 
            erMsg = "売上情報読み込み中にエラーが発生しました"
            logging.exception(erMsg) 
            return ERROR
        

    def read_salesinfo_month(cls, fle:tuple):
        try:                        
            df_in = pd.DataFrame()
            
            for f in fle:
                # １行目の年月情報の文字列を取得しDate型の情報に変換する
                temp = pd.read_csv(f,encoding="CP932",header=None,nrows=1)                
                time_val = temp[0][0].split("　")[0].split(":")[1].split("～")            
                dt_year_and_mont = time_val[0][:8]
                                        
                temp = pd.read_csv(f ,encoding="CP932", header=1 , usecols=USECOLS_MONTH)
                temp["day"] = dt_year_and_mont
                                
                df_in = pd.concat([df_in, temp]) 
                                
            df_in = df_in.rename(columns = COL_CSVTODB_MONTH)
        
            #　欠損値を更新            
            df_in = df_in.fillna({"t_code":-1,"l_code":-1,"i_name":"その他","amount":0})    
            
            return cls.__update_salesinfo(df_in, cls.df_db_month, TBLNAME_MONTH)
                            
            
        except Exception: 
            erMsg = "売上情報読み込み中にエラーが発生しました"
            logging.exception(erMsg) 
            return ERROR
    
    
    def read_salesinfo_day(cls, fle:tuple):
    
        try:                        
            df_in = pd.DataFrame()
            
            for f in fle:
                # １行目の年月情報の文字列を取得しDate型の情報に変換する
                temp = pd.read_csv(f,encoding="CP932",header=None,nrows=1)                
                time_val = temp[0][0].split("　")[0].split(":")[1].split("～")            
                dt_year = time_val[0][:5]
                                        
                temp = pd.read_csv(f ,encoding="CP932", header=1) 
                    
                head_data = temp[["得意先コード","ラインコード","商品コード","商品名"]]
                head_data = head_data.rename(columns = COL_CSVTODB_DAY)
                
                sales_data = temp.filter(like=f"納品金額{dt_year}", axis=1)   
                henpin_data = temp.filter(like=f"返品金額{dt_year}", axis=1)  
                
                index = 0
                for col in sales_data.columns:
                                     
                    head_data["day"] = col[4:15]
                    
                    head_data2 = head_data.copy()
                    
                    head_data["kind"] = "売上"
                    head_data2["kind"] = "返品"
                    
                    head_data["amount"] = sales_data.iloc[:,index]
                    head_data2["amount"] = henpin_data.iloc[:,index]
                                    
                    df_in = pd.concat([df_in,head_data.query("amount>0"),head_data2.query("amount>0")]) 
                    
                    index += 1
                            
            #　欠損値を更新            
            df_in = df_in.fillna({"t_code":-1,"l_code":-1,"i_name":"その他","amount":0})    
            
            return cls.__update_salesinfo(df_in, cls.df_db_day, TBLNAME_DAY)
            
        except Exception: 
            erMsg = "売上情報読み込み中にエラーが発生しました"
            logging.exception(erMsg)   
            return ERROR
        
        
        
    def update_mst_tenpo(self, f):
        
        try:
            mst_data = pd.read_csv(f,encoding="utf-8",header=1) 
            with  sqlite3.connect(self.DB_PATH) as conn :      
                    mst_data.to_sql(TBLNAME_TENPO, conn,if_exists="replace",index=None)
                    conn.commit()
                    self.df_tenpo = pd.read_sql(f"SELECT * FROM {TBLNAME_TENPO}", conn)
            return SUCCESS
        except Exception: 
            erMsg = "マスタ情報更新中にエラーが発生しました"
            logging.exception(erMsg)   
            return ERROR
        
        
    
        
