# -*- coding: utf-8 -*-
"""
Created on Sat Mar  8 16:24:05 2025

@author: mkt05
"""

class Settings:
    
    def __init__(self):
        pass
    
    #集計区分のフラグ
    FLG_DAY = 1
    FLG_WEEK = 2 
    FLG_MONTH = 3
    
    DB_PATH = r"\\okisvrm1\各部署\パン部門\TestDB\SalesInfo.db"
    
    FORMAT_YMD = "%Y年%m月%d日"
    FORMAT_YM = "%Y年%m月"
    
    TBLNAME_DAY = "sales_day"
    TBLNAME_WEEK = "sales_week"
    TBLNAME_MONTH = "sales_month"
    TBLNAME_BRAND = "mst_brand"
    TBLNAME_LINE = "mst_line"
    TBLNAME_TENPO = "mst_tenpo"
    
    SELECT_LINE = 1
    SELECT_ITEM = 2
    
    SELECT_PREYEAR = 0
    SELECT_PERIOD = 1
    
    ENTRY_DISP_FORM = "yyyy年mm月dd日"
    
    CODE_WAGASHI = 9
    CODE_YOUGASHI = 5
    