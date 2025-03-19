'''
Created on 2025/03/19

@author: mkt05
'''

import pandas as pd
from py_pk.settings import Settings as const

class Analysis_data:
    '''
    classdocs
    '''
    def __init__(self):
        self.dataframes = {
            'day': pd.DataFrame(),
            'week': pd.DataFrame(),
            'month': pd.DataFrame(),
            'brand': pd.DataFrame(),
            'line': pd.DataFrame(),
            'tenpo': pd.DataFrame()
        }
        
        self.current_df  = pd.DataFrame() # 選択されているデータフレーム
        
        self.pre_charts = {
            'timeseries': [],
            'histogram': [],
            'scatterplot': []
        }
        
    def setDataframe(self, df_name="", df=pd.DataFrame):
        
        # Merge with reference data
        for merge_df, key, fill_value in [
            (self.dataframes['brand'], 't_code', "その他取引先"),
            (self.dataframes['line'], 'l_code', "その他ライン")
        ]:
            df = pd.merge(df, merge_df, on=key, how='left').fillna(fill_value)
        
        # Convert date format
        date_format = const.FLG_MONTH if df_name == "month" else const.FORMAT_YMD
        df[df_name] = pd.to_datetime(df[df_name], format=date_format)
        
        self.dataframes[df_name] = df
        
        
    def set_select_df(self, df_name):
        self.current_df = self.dataframes[df_name]
        
            
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
        if self.current_df.empty:
            return self.current_df
        
        df_out = self.current_df

        # Apply filters
        if brand:
            df_out = df_out[df_out["t_name"] == brand]
        
        if line:
            df_out = df_out[df_out["l_name"] == line]
        
        if items:
            df_out = df_out[df_out["i_name"].isin(items)]
    
        
        # Date range filter
        df_out = df_out[(df_out["day"] >= from_date) & (df_out["day"] <= to_date)]
    
        # Week filter
        if target_week:
            df_out = df_out.set_index("day")
            df_out = df_out[df_out.index.weekday.isin(target_week)]
            df_out = df_out.reset_index(drop=False)
    
        return df_out
        
    
    
    