'''
Created on 2025/03/19

@author: mkt05
'''

import pandas as pd
from py_pk.settings import Settings
from py_pk.process_db import Process_db
import logging
from datetime import datetime as dt

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
            Settings.TBLNAME_BRAND: pd.DataFrame(),
            Settings.TBLNAME_LINE: pd.DataFrame(),
            Settings.TBLNAME_TENPO: pd.DataFrame()
        }
        
        self.current_df_type = ""  # 選択されているデータフレーム
        
        self.pre_charts = {
            'timeseries': [],
            'histogram': [],
            'scatterplot': []
        }                
        self.set_mastData() # マスタデータの読み込み
    
    
    def get_currentData(self):
            return self.dataframes[self.current_df_type]
       
    
    def set_mastData(self):
        self.dataframes[Settings.TBLNAME_BRAND], self.dataframes[Settings.TBLNAME_LINE], self.dataframes[Settings.TBLNAME_TENPO] = Process_db.Get_master()
            
    
    def set_salesData(self) -> bool:
        try:        
            df = Process_db.Get_salesData(self.current_df_type)
            df = df.merge(self.dataframes[Settings.TBLNAME_BRAND],on='t_code', how='left').fillna("その他取引先")
            df = df.merge(self.dataframes[Settings.TBLNAME_LINE],on='l_code', how='left').fillna("その他ライン")
            
            # 日付文字列データをDateTimeに変換
            if self.current_df_type == Settings.TBLNAME_DAY:
                df["day_DateTime"] = pd.to_datetime(df["day"], format=Settings.FORMAT_YMD)
                
            elif self.current_df_type == Settings.TBLNAME_WEEK:
                df["day_DateTime"] = pd.to_datetime(df["day"], format=Settings.FORMAT_YMD)
                
            elif self.current_df_type == Settings.TBLNAME_MONTH:
                df["day_DateTime"] = pd.to_datetime(df["day"], format=Settings.FORMAT_YM)
                        
            self.dataframes[self.current_df_type] = df            
            return True
        
        except Exception:
            logging.exception(Exception)
            return False        
                          
                
    def get_maxdate(self):
        df = self.dataframes[self.current_df_type]     
        return df['day'].max()
        
    def get_mindate(self):
        df = self.dataframes[self.current_df_type] 
        return df['day'].min()        
           
            
    def get_datacondition(self, brand=None, line=None, items=None, from_date=None, to_date=None, target_week=None) -> pd.DataFrame:
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
            
            if df_out.empty:
                return df_out
    
            # Apply filters
            if brand:
                df_out = df_out[df_out["t_name"] == brand]
            
            if line:
                df_out = df_out[df_out["l_name"] == line]
            
            if items:
                df_out = df_out[df_out["i_name"].isin(items)]
        
            
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
        self.dataframes[self.current_df_type] = Process_db.Update_salesinfo(fle, self.dataframes[self.current_df_type], self.current_df_type)
        
        return True
    