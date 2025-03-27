'''
Created on 2025/03/19

@author: mkt05
'''

import pandas as pd
from py_pk.settings import Settings
from py_pk.process_db import Process_db
import logging
from datetime import datetime as dt
from tkinter import messagebox as msg

logging.basicConfig(filename='logfile/logger.log', level=logging.ERROR)

class Analysis_data:
    '''
    classdocs
    '''
    def __init__(self):
        self.dataframes = {
            Settings.TBLNAME_DAY: pd.DataFrame(),
            Settings.TBLNAME_WEEK: pd.DataFrame(),
            Settings.TBLNAME_MONTH: pd.DataFrame(),
            Settings.TBLNAME_BRAND: Process_db.Get_master(Settings.TBLNAME_BRAND),
            Settings.TBLNAME_LINE: Process_db.Get_master(Settings.TBLNAME_LINE),
            Settings.TBLNAME_TENPO: Process_db.Get_master(Settings.TBLNAME_TENPO)
        }
        
        self.current_df_type = Settings.TBLNAME_MONTH # 選択されているデータフレーム
        
        self.pre_charts = {
            'timeseries': [],
            'histogram': [],
            'scatterplot': []
        }                

    
    def get_currentData(self):
            return self.dataframes[self.current_df_type]
            
    
    def get_salesData(self):
        try:                
            df = Process_db.Get_salesData(self.current_df_type)                                    
            self.dataframes[self.current_df_type] = df 
            return df
        except Exception:
            logging.exception(Exception)
            raise         
                          
    def get_maxdate(self):
        df = self.dataframes[self.current_df_type]     
        return df['day'].max()
        
    def get_mindate(self):
        df = self.dataframes[self.current_df_type] 
        return df['day'].min()        
           
            
    def get_datacondition(self, brand=None, line=None, items=None, from_date=None, to_date=None, target_week=None):
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
            
            df_out = self.dataframes[self.current_df_type] 
            df_out = df_out.merge(self.dataframes[Settings.TBLNAME_BRAND],on='t_code', how='left').fillna("その他取引先")
            df_out = df_out.merge(self.dataframes[Settings.TBLNAME_LINE],on='l_code', how='left').fillna("その他ライン")
         
            if df_out.empty:
                return df_out
    
            # Apply filters
            if brand:
                df_out = df_out[df_out["t_name"] == brand]
            
            if line:
                df_out = df_out[df_out["l_name"] == line]
            
            if items:
                df_out = df_out[df_out["i_name"].isin(items)]
                       

            # 日付文字列データをDateTimeに変換
            if self.current_df_type == Settings.TBLNAME_MONTH:
                df_out["day_DateTime"] = pd.to_datetime(df_out["day"], format=Settings.FORMAT_YM)
                
            else:
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
            return False  
            
    def update_salesData(self, fle) -> bool:
        
        try:
            df_base = self.get_currentData()
            if self.current_df_type == Settings.TBLNAME_DAY:
                df = Process_db._read_salesinfo_day(fle)
                
            elif self.current_df_type == Settings.TBLNAME_WEEK:
                df = Process_db._read_salesinfo_week(fle)
                
            elif self.current_df_type == Settings.TBLNAME_MONTH:
                df = Process_db._read_salesinfo_month(fle)
    
            # 同日付の売上情報が含まれている場合
            a = df["day"].tolist()
            b = df_base["day"].tolist()
            c = set(a) & set(b)
                        
            if len(c) > 0:                  
                msgVal = sorted(c)                        
                message_text = "\n".join([msgVal[0],"～",msgVal[-1]])
                
                flg_answer = msg.askyesnocancel(msg.INFO,f"同日付の売上情報が含まれています。更新しますか？\n{message_text}")
                
                if flg_answer is None:
                    msg.showinfo(msg.INFO, "売上情報の更新処理を中断しました。")
                    return pd.DataFrame()
                
                elif flg_answer:
                    df_base = df_base[~df_base["day"].isin(c)]     
                else:
                    df = df[~df["day"].isin(c)] 
                    
            use_cools = [""]
            df_new = pd.concat([df, df_base]).loc[:,use_cools]
            
            
            
            self.dataframes[self.current_df_type] = Process_db.Update_db(df_new, self.current_df_type)
                        
            return True
        
        except Exception:
            logging.exception(Exception)
            
            raise  
        
        
    