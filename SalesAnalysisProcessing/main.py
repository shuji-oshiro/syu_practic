# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:49:19 2025

@author: mkt05
"""

import os
import tkinter as tk

import tkinter.ttk as ttk
import pandas as pd
import openpyxl as op
import process_db
import process_analysis
import settings
import logging
from datetime import timedelta, datetime as dt
from dateutil.relativedelta import relativedelta  
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox as msg
import matplotlib.pyplot as plt
import threading

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

const = settings.Settings()        

process_db = process_db.Process_db()
pro_anasys = process_analysis.ProcessAnalysis()

USECOLS_NAME = {"amount":"売上金額","count":"売上数量","avg":"平均単価","":""}

plt.rcParams["font.family"] = "meiryo"



class SalesDataFrame:
    def __init__(self):
        self.df_day = pd.DataFrame()
        self.df_week = pd.DataFrame()
        self.df_month = pd.DataFrame()
        self.df_brand = pd.DataFrame()
        self.df_line = pd.DataFrame()
        self.df_tenpo = pd.DataFrame()
        self.current_date = None
        
        self.pre_timeserieschart = []
        self.pre_histogram = []
        self.pre_scatterplot = []
                
        
    def get_maxdate(self):
        val = None
        
        if self.current_date == const.FLG_DAY:
            if len(self.df_day["day"]) > 0:
                val = self.df_day["day"].max()   
                
        elif self.current_date == const.FLG_WEEK:
            if len(self.df_week["day"]) > 0:
                val = self.df_week["day"].max()   
                
        elif self.current_date == const.FLG_MONTH:
            if len(self.df_month["day"]) > 0:
                val = self.df_month["day"].max()                
        return val    
    
    def get_mindate(self):
        val = None
        
        if self.current_date == const.FLG_DAY:
            if len(self.df_day["day"]) > 0:
                val = self.df_day["day"].min()   
                
        elif self.current_date == const.FLG_WEEK:
            if len(self.df_week["day"]) > 0:
                val = self.df_week["day"].min()   
                
        elif self.current_date == const.FLG_MONTH:
            if len(self.df_month["day"]) > 0:
                val = self.df_month["day"].min()               
                
        return val     
    
    
    def get_selectkind_df(self):
        """
        現在選択されている集計区分のデータフレームを返す

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        if self.current_date == const.FLG_DAY:
            return self.df_day
        
        elif self.current_date == const.FLG_WEEK:
            return self.df_week
        
        else:
            return self.df_month
        
            
    def get_cound_df(self, _brand=None, _line=None, _items=None, _from=None, _to=None, targetWeek=None):
        
        df_out = self.get_selectkind_df()
        from_day = _from     
        to_day = _to
        if df_out.empty:
            return df_out
        
            
        # コードと名称の紐づけ処理            
        df_out = pd.merge(df_out, self.df_brand, on='t_code', how='left').fillna("その他取引先")
        df_out = pd.merge(df_out, self.df_line, on='l_code', how='left').fillna("その他ライン")
        
        # 取引先で抽出   
        if not _brand == "全取引先":
            df_out = df_out[df_out["t_name"]==_brand]           
        # ライン名抽出
        if not _line == "全ライン":
            df_out = df_out[df_out["l_name"]==_line]
                     
        # 商品名抽出            
        if _items:
            df_out = df_out[df_out["i_name"].isin(_items)]
                            
           
        # 文字列日付⇒日付データ
        if self.current_date == const.FLG_MONTH:
            df_out["day"] = pd.to_datetime(df_out["day"], format=const.FORMAT_YM)
        else:                          
            df_out["day"] = pd.to_datetime(df_out["day"], format=const.FORMAT_YMD)
        
            
        # FROM <= 抽出期間 <= TO               
        df_out = df_out[(df_out["day"]>=from_day) & (df_out["day"]<=to_day)]  
                    
        #　集計期間==日別 -> WEEK
        if targetWeek: 
            df_out = df_out.set_index("day")
            df_out = df_out[df_out.index.weekday.isin(targetWeek)]                
            df_out = df_out.reset_index(drop=False)
        
        return df_out        
    
salesDataFrame = SalesDataFrame()
        
    
class FrameInput(tk.LabelFrame):    
    def __init__(self, master):
        """
        売上情報ファイルからＤＢに取り込む際に使用するフォーム

        Parameters
        ----------
        master : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(master, text="売上情報入力", bd=2)
        self.pack(anchor=tk.NW, padx=10,pady=10)  
        
        # 1-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        tk.Label(frame_row1, text="データベースパス：").pack(side=tk.LEFT)
        tk.Label(frame_row1, text=const.DB_PATH).pack(side=tk.LEFT)
    
    
        btn_GetInfo = tk.Button(frame_row1, text="店舗情報更新")
        btn_GetInfo.pack(side=tk.LEFT)
        
        
        def update_mst_tenpo(self):
                                   
            try:
                fle = ()        
                typ = [('', '*')]            
                fle = filedialog.askopenfilename(filetypes = typ)                             
                
                #ファイルが読み込まれていない場合処理を中断
                if len(fle) > 0:   
                    df = process_db.update_mst_tenpo(fle)
                    msg.showinfo(msg.INFO,"店舗マスタ更新処理成功")
                    salesDataFrame.df_tenpo = df             
            except Exception: 
                msg.showinfo(msg.ERROR,"店舗マスタ更新処理失敗")   


class FramePeriod(tk.LabelFrame):
    def __init__(self, master):
        """
        集計期間を入力するフォーム
        1.売上情報を抽出する期間の設定
        2.日別、週別、月別による集計
        3.曜日選択-＞日別による集計のみ

        Parameters
        ----------
        master : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(master, text="集計期間：", bd=2)
        self.pack(anchor=tk.NW, padx=10,pady=5)  
        
        # 2-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        btn_GetInfo = tk.Button(frame_row1, text="売上情報入力", command=self.push_inoputData)
        btn_GetInfo.pack()

        #売上情報のDB更新で使用する期間判別
        self.radio_kind_period = tk.IntVar(value=None)
        
                
                
        # 2-2 日別売上抽出
        frame_row2 = tk.LabelFrame(self)
        frame_row2.pack(anchor=tk.W)
            
        tk.Radiobutton(frame_row2, text="日別", variable=self.radio_kind_period, value=const.FLG_DAY, command=self.choice_datekind).pack(side=tk.LEFT)
        self.entry_from = DateEntry(frame_row2, date_pattern="yyyy年mm月dd日")
        self.entry_from.pack(side=tk.LEFT)
        tk.Label(frame_row2, text="～").pack(side=tk.LEFT)
        #　集計終了日
        self.entry_to = DateEntry(frame_row2, date_pattern="yyyy年mm月dd日")
        self.entry_to.pack(side=tk.LEFT)
        
        # 2-2 日別売上抽出 曜日指定
        frame_row2_week = tk.LabelFrame(self)
        frame_row2_week.pack(anchor=tk.W)
                
        self.week_flg = []
        for i in range(0,7):
            flg = tk.BooleanVar()
            flg.set(True)
            self.week_flg.append(flg)
            
        # チェックボックスの作成
        tk.Checkbutton(frame_row2_week, text="月", variable=self.week_flg[0]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_row2_week, text="火", variable=self.week_flg[1]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_row2_week, text="水", variable=self.week_flg[2]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_row2_week, text="木", variable=self.week_flg[3]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_row2_week, text="金", variable=self.week_flg[4]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_row2_week, text="土", variable=self.week_flg[5]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_row2_week, text="日", variable=self.week_flg[6]).pack(side=tk.LEFT)
        
        # 2-3　週別売上抽出
        frame_row3 = tk.LabelFrame(self)
        frame_row3.pack(anchor=tk.W)        
        tk.Radiobutton(frame_row3, text="週別", variable=self.radio_kind_period, value=const.FLG_WEEK, command=self.choice_datekind).pack(side=tk.LEFT)
        
        self.var_select_week_from = tk.StringVar()
        self.comb_week_from = ttk.Combobox(frame_row3, state="readonly", textvariable=self.var_select_week_from)
        self.comb_week_from.pack(side=tk.LEFT)
        tk.Label(frame_row3, text="～").pack(side=tk.LEFT)
        self.var_select_week_to = tk.StringVar()
        self.comb_week_to = ttk.Combobox(frame_row3, state="readonly", textvariable=self.var_select_week_to)
        self.comb_week_to.pack(side=tk.LEFT)
        
        #2-4　月別売上抽出
        frame_row4 = tk.LabelFrame(self)
        frame_row4.pack(anchor=tk.W)      
        tk.Radiobutton(frame_row4, text="月別", variable=self.radio_kind_period, value=const.FLG_MONTH, command=self.choice_datekind).pack(side=tk.LEFT)
        
        self.var_select_mont_from = tk.StringVar()
        self.comb_mont_from = ttk.Combobox(frame_row4, state="readonly", textvariable=self.var_select_mont_from)
        self.comb_mont_from.pack(side=tk.LEFT)
        tk.Label(frame_row4, text="～").pack(side=tk.LEFT)
        self.var_select_mont_to = tk.StringVar()
        self.comb_mont_to = ttk.Combobox(frame_row4, state="readonly", textvariable=self.var_select_mont_to)
        self.comb_mont_to.pack(side=tk.LEFT)
        
        
    def get_cound_perid_formaｎdto(self):
        """
        抽出条件の日、週、月のFORM・TOの日付を取得

        Returns
        -------
        _from : TYPE
            DESCRIPTION.
        _to : TYPE
            DESCRIPTION.

        """
        _from,_to = None,None
        if self.radio_kind_period.get() == const.FLG_DAY:
            _from = dt.combine(self.entry_from.get_date(), dt.min.time())
            _to = dt.combine(self.entry_to.get_date(), dt.min.time())
            
            
        elif self.radio_kind_period.get() == const.FLG_WEEK:
            _from = dt.strptime(self.var_select_week_from.get(), const.FORMAT_YMD)
            _to = dt.strptime(self.var_select_week_to.get(), const.FORMAT_YMD)
            
            
        elif self.radio_kind_period.get() == const.FLG_MONTH:
            _from = dt.strptime(self.var_select_mont_from.get(), const.FORMAT_YM)
            _to = dt.strptime(self.var_select_mont_to.get(), const.FORMAT_YM)
            
            # _to = _to.replace(day=calendar.monthrange(_to.year, _to.month)[1])
            
        return _from, _to
    
    
        
    def get_select_dayofweeks(self):
        """
        日別の売上集計期間が選択されている場合、選択されている曜日を返す処理

        Returns
        -------
        targetWeek : TYPE
            DESCRIPTION.

        """
        
        targetWeek = []
        
        # 日別の集計期間が選択されていれば曜日指定の配列を返す
        if self.radio_kind_period.get() == const.FLG_DAY:
            for i in range(0,7):
                if self.week_flg[i].get():
                    targetWeek.append(i)  
                
        return targetWeek
        

    def update_database(self, fle):          
        """
        売上情報を更新する処理-＞マルチスレッド
        
    
        Parameters
        ----------
        event : TYPE
            DESCRIPTION.
    
        Returns
        -------
        str
            DESCRIPTION.
    
        """    
        try:                    
            
            #ファイルが読み込まれていない場合処理を中断
            if len(fle) > 0:               
                
                fle = sorted(fle)            
                
                if self.radio_kind_period.get() == const.FLG_DAY: 

                    df_update = process_db.read_salesinfo_day(fle, salesDataFrame.df_day)
                    if not df_update.empty:
                        salesDataFrame.df_day = df_update
                        msg.showinfo(msg.INFO,"売上情報の更新処理に成功しました")
            
                elif self.radio_kind_period.get() == const.FLG_WEEK:
                        
                    df_update = process_db.read_salesinfo_week(fle, salesDataFrame.df_week)
                    if not df_update.empty:
                        salesDataFrame.df_week = df_update
                        msg.showinfo(msg.INFO,"売上情報の更新処理に成功しました")
                        
                elif self.radio_kind_period.get() == const.FLG_MONTH:                    
                        
                    df_update = process_db.read_salesinfo_month(fle, salesDataFrame.df_month)
                    if not df_update.empty:
                        salesDataFrame.df_month = df_update
                        msg.showinfo(msg.INFO,"売上情報の更新処理に成功しました")
                
                
        except Exception: 
            msg.showerror(msg.ERROR, "売上情報の更新処理に失敗しました")            
        
        finally:
            # スレッド処理終了
            app.after(0, loading_window.destroy)
            return "break" 
              
        
    def push_inoputData(self):
        """
        [売上情報入力]ボタン押下時の処理

        Returns
        -------
        None.

        """
        
        """処理中のダイアログを表示"""
        
                    
        if not self.radio_kind_period.get():
            msg.showwarning(msg.WARNING, "読み込む売上情報の集計期間を選択してください")
            return "break"
        
        fle = ()        
        typ = [('CSVファイル', '*.csv')]            
        fle = filedialog.askopenfilenames(filetypes = typ)    
        
        # TODO 検証用処理　スレッド停止
        # self.update_database(fle)
        
        global loading_window
        loading_window = tk.Toplevel(app)  # 新しいウィンドウ
        loading_window.title("処理中")
        loading_window.geometry("300x100")
        loading_window.resizable(False, False)
        
        ttk.Label(loading_window, text="データ更新中...\nしばらくお待ちください", font=("Arial", 12)).pack(pady=20)
        loading_window.grab_set()  # ダイアログを最前面に固定
        
        # 別スレッドでデータベース更新処理を実行
        threading.Thread(target=lambda:self.update_database(fle), daemon=True).start()


    def get_salesdata(self):     
        """
        選択した売上集計区分の売上情報を取得する処理-＞マルチスレッド

        Returns
        -------
        None.

        """
        
        try:
            if self.radio_kind_period.get() == const.FLG_DAY:                
                if salesDataFrame.df_day.empty:
                    salesDataFrame.df_day = process_db.get_sales_day()   
                    
                salesDataFrame.current_date=const.FLG_DAY
                # 集計期間の日付を更新する
                self.entry_from.set_date(salesDataFrame.get_mindate())
                self.entry_to.set_date(salesDataFrame.get_maxdate())
                
                
            elif self.radio_kind_period.get() == const.FLG_WEEK:
                if salesDataFrame.df_week.empty: 
                    salesDataFrame.df_week = process_db.get_sales_week() 
                
                salesDataFrame.current_date=const.FLG_WEEK
                
                df = salesDataFrame.df_week.sort_values("day")
                
                # 集計期間の日付を更新する            
                self.comb_week_from["values"] = df["day"].unique().tolist()
                self.comb_week_to["values"] = df["day"].unique().tolist()
                self.var_select_week_from.set(salesDataFrame.get_mindate())               
                self.var_select_week_to.set(salesDataFrame.get_maxdate()) 
                

                
            elif self.radio_kind_period.get() == const.FLG_MONTH:
                
                if salesDataFrame.df_month.empty:
                    salesDataFrame.df_month = process_db.get_sales_month()
                
                salesDataFrame.current_date=const.FLG_MONTH
                
                df = salesDataFrame.df_month.sort_values("day")
                
                self.comb_mont_from.configure(values=df["day"].unique().tolist())
                self.comb_mont_to.configure(values=df["day"].unique().tolist())
                self.var_select_mont_from.set(salesDataFrame.get_mindate())               
                self.var_select_mont_to.set(salesDataFrame.get_maxdate())                         
              
            
            # TODO：後日機能追加
            # # 集計期間の選択によって曜日選択の有効無効を設定する
            # if not self.radio_kind_period.get() == FLG_DAY:
            #     for widget in self.frame_row3.winfo_children():       
            #         widget.config(state=tk.DISABLED)
            # else:
            #     for widget in self.frame_row3.winfo_children():       
            #         widget.config(state=tk.NORMAL)
                                    
        except Exception: 
            msg.showerror(msg.ERROR,"売上情報読み込み中にエラーが発生しました。")
        
        finally:        
            # スレッド処理終了
            app.after(0, loading_window.destroy)
                    

    def choice_datekind(self):
        """
        売上集計期間を選択した時に発生するイベント

        Returns
        -------
        None.

        """
        
        """処理中のダイアログを表示"""
        
        global loading_window
        loading_window = tk.Toplevel(app)  # 新しいウィンドウ
        loading_window.title("処理中")
        loading_window.geometry("300x100")
        loading_window.resizable(False, False)
    
        ttk.Label(loading_window, text="データ取得中...\nしばらくお待ちください", font=("Arial", 12)).pack(pady=20)
        loading_window.grab_set()  # ダイアログを最前面に固定
    
        #  別スレッドでデータベース更新処理を実行
        threading.Thread(target=self.get_salesdata, daemon=True).start()

              
    def get_period_day_count(self):
        """
        集計期間の日数を返す処理        

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # TODO： 日、週、月単位での処理追加                
        from_day = dt.strptime(self.entry_from.get(), const.FORMAT_YMD)        
        to_day = dt.strptime(self.entry_to.get(), const.FORMAT_YMD)
        
        return (to_day-from_day).days 
    
                

class FrameCound(tk.LabelFrame):    
    def __init__(self, master):
        """
        売上情報を得意先名、ライン名、商品名などで集計する為のフォーム
        
        Parameters
        ----------
        master : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(master, text="抽出条件", bd=2)
        self.pack(anchor=tk.NW, padx=10,pady=5) 
                
        salesDataFrame.df_brand, salesDataFrame.df_line, salesDataFrame.df_tenpo = process_db.get_master()
        
        # 3-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        
        var_brand = salesDataFrame.df_brand["t_name"].unique().tolist()
        var_brand.insert(0,"全取引先")
        var_brand.append("その他取引先")
        
        self.select_brand_var = tk.StringVar()
        
        cp_comb = ttk.Combobox(frame_row1, values=var_brand ,state="readonly", textvariable=self.select_brand_var)
        cp_comb.current(0)
        cp_comb.pack(side=tk.LEFT)
        
        
        self.radio_jyoken = tk.IntVar(value=1)
        # 3-2
        self.frame_row2 = tk.LabelFrame(self)
        self.frame_row2.pack(anchor=tk.W)
        
        tk.Radiobutton(self.frame_row2, text="ライン別", variable=self.radio_jyoken, value="1", command=self.chang_coundkbn).pack(side=tk.LEFT)
        
        var_line = salesDataFrame.df_line["l_name"].tolist()
        var_line.insert(0,"全ライン")
        
        self.select_line_var = tk.StringVar()
        
        line_comb = ttk.Combobox(self.frame_row2, values=var_line ,state="readonly", textvariable=self.select_line_var)
        line_comb.current(0)
        line_comb.pack(side=tk.LEFT)
        
        # 3-3
        self.frame_row3 = tk.LabelFrame(self)
        self.frame_row3.pack(anchor=tk.W)
        
        tk.Radiobutton(self.frame_row3, text="商品別", variable=self.radio_jyoken, value="2",command=self.chang_coundkbn).pack(side=tk.LEFT)

        # 商品コードを入力するフォーム
        self.var_icode = tk.IntVar(value=0)
        entry_icode = tk.Spinbox(self.frame_row3, width=5, from_=0, to=9999, textvariable=self.var_icode)
        entry_icode.bind("<Return>", self.press_key)
        entry_icode.pack(side=tk.LEFT) 
        
        
        # 商品名のキーワードを入力するフォーム
        self.var_tname = tk.StringVar()
        entry_name = tk.Entry(self.frame_row3, textvariable=self.var_tname)
        entry_name.bind("<Return>", self.setfindItems)
        entry_name.pack(side=tk.LEFT)
        
                
        #　一部コントロールの無効化処理
        for widget in self.frame_row3.winfo_children():
            if not isinstance(widget, tk.Radiobutton):
                widget.config(state=tk.DISABLED)
                
        self.frame_row4 = tk.LabelFrame(self)
        self.frame_row4.pack(anchor=tk.W)
                
        # キーワードで抽出された商品名を表示するリスト
        self.var_foudlist = tk.StringVar()
        self.lbox_findItems = tk.Listbox(self.frame_row4, listvariable=self.var_foudlist, width=25, height=12, selectmode=tk.MULTIPLE)
        self.lbox_findItems.pack(side=tk.LEFT)
        self.lbox_findItems.bind("<Double-Button-1>",self.set_listItems)
        self.lbox_findItems.config(state=tk.DISABLED)
        
    
    def press_key(self, event):
        """
        商品コードを入力した後エンターキーを押下した時の処理

        Parameters
        ----------
        event : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        target_df = salesDataFrame.get_selectkind_df()
  
        try:
            if target_df.empty: 
                msg.showwarning(msg.WARNING, "売上情報が存在しません")               
                    
            else:       
                itemNames = target_df[target_df["i_code"]==self.var_icode.get()]["i_name"].unique().tolist()
                
                if len(itemNames) > 0:
                    self.var_foudlist.set(itemNames) 
                else:
                    msg.showwarning(msg.WARNING, "検索条件に合致する商品情報がありません。")
        
        except Exception: 
            pass
        
    
    
    def get_finditems(self):
        """
        売上情報の集計を商品単位で行う際に、選択された商品名を返す処理

        Returns
        -------
        select_Items : TYPE
            DESCRIPTION.

        """
        select_Items = []
        
        if self.lbox_findItems["state"] == tk.DISABLED:
            return select_Items
        
        select_index = self.lbox_findItems.curselection()
        if len(select_index) > 0:
            for index in select_index:
                select_Items.append(self.lbox_findItems.get(index))            

        return select_Items
        
    
    def set_listItems(self,event):
        """
        抽出条件の商品名を表示するリストをダブルクリックした時の処理

        Parameters
        ----------
        event : TYPE
            DESCRIPTION.

        Returns
        -------
        str
            DESCRIPTION.

        """
        
        try:
            
            if event.widget["state"] == tk.DISABLED:
                return "break"
                
            fle = ()        
            typ = [('CSVファイル', '*.csv')]     
            iDir = os.path.abspath(os.path.dirname(__file__))       
            fle = filedialog.askopenfilename(filetypes = typ, initialdir=iDir)                             
            
            #ファイルが読み込まれていない場合処理を中断
            if len(fle)>0 :          
                
                temp = pd.read_csv(fle ,encoding="CP932",header=None)                 
                a = temp[0].tolist()     
                
                target_df = salesDataFrame.get_selectkind_df()
                
                if target_df.empty:
                    msg.showwarning("売上情報が存在しません")
                    return "break"
                
                
                b =target_df[target_df["i_code"].isin(a)]
                c = b["i_name"].unique().tolist()
                
                self.var_foudlist.set(c)
                
                for i in range(0,event.widget.size()):
                    event.widget.select_set(i)        
                
                return "break"
            
        except Exception: 
            msg.showerror(msg.ERROR,"データ取得中にエラーが発生しました。")
            return "break"
        
        
    def chang_coundkbn(self):
        """
        抽出条件ボタン選択時の処理
    
        Returns
        -------
        None.
    
        """
             
        if self.radio_jyoken.get() == 1:
            
            for widget in self.frame_row2.winfo_children():
                if not isinstance(widget, tk.Radiobutton):
                    widget.config(state=tk.NORMAL)
            
            for widget in self.frame_row3.winfo_children():
                if not isinstance(widget, tk.Radiobutton):         
                    widget.config(state=tk.DISABLED)
            
            for widget in self.frame_row4.winfo_children():
                if not isinstance(widget, tk.Radiobutton):
                    widget.config(state=tk.DISABLED)
            
        else:
            for widget in self.frame_row2.winfo_children():
                if not isinstance(widget, tk.Radiobutton):
                    widget.config(state=tk.DISABLED)
            
            for widget in self.frame_row3.winfo_children():
                if not isinstance(widget, tk.Radiobutton):
                    widget.config(state=tk.NORMAL)
            
            for widget in self.frame_row4.winfo_children():
                if not isinstance(widget, tk.Radiobutton):
                    widget.config(state=tk.NORMAL)
            
    
    def setfindItems(self, event):
        """
        # 商品名で検索するエントリーフォームでエンターした時の処理　-＞条件に合致する商品名をリストに表示

        Parameters
        ----------
        event : TYPE
            DESCRIPTION.

        Returns
        -------
        str
            DESCRIPTION.

        """
        target_df = salesDataFrame.get_selectkind_df()
        if not target_df.empty:        
            itemNames = target_df[target_df["i_name"].str.contains(self.var_tname.get(),na=False)]["i_name"].unique().tolist()
            
            if len(itemNames) > 0:
                self.var_foudlist.set(itemNames) 
            else:
                msg.showwarning(msg.WARNING, "検索条件に合致する商品情報がありません。")
                
        else:       
            msg.showwarning(msg.WARNING, "売上情報が存在しません")
                            
        return "break"
        

class FrameOutput(tk.LabelFrame):
    def __init__(self, master, cls_period_instance, cls_cound_instance):
        """
        抽出条件をベースに売上分析を行うフォーム

        Parameters
        ----------
        master : TYPE
            DESCRIPTION.
        cls_period_instance : TYPE
            DESCRIPTION.
        cls_cound_instance : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(master, text="集計処理")
        self.pack(anchor=tk.NW, padx=10,pady=10) 
        
        frame_row0 = tk.LabelFrame(self)
        frame_row0.pack(anchor=tk.W)
        self.var_radio_select_vals = tk.StringVar(value="amount")    
        tk.Radiobutton(frame_row0, text="売上金額", variable=self.var_radio_select_vals, value="amount").pack(side=tk.LEFT)
        tk.Radiobutton(frame_row0, text="売上数量", variable=self.var_radio_select_vals, value="count").pack(side=tk.LEFT)
        
        # TODO 合計、平均で選択 ただし平均の意味を確認して使用する予定
        self.var_select_cal = tk.IntVar(value=0)
        tk.Radiobutton(frame_row0, text="合計", variable=self.var_select_cal, value=0).pack(side=tk.LEFT)
        # tk.Radiobutton(frame_row0, text="平均", variable=self.var_select_cal, value=1).pack(side=tk.LEFT)   
        
        
        # 3-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        
        comit_btn = tk.Button(frame_row1, text="時系列分析", command=self.out_timeseries_chart)
        comit_btn.pack(side=tk.LEFT)
        
        e_lab = tk.Label(frame_row1, text="移動平均集計件数")
        e_lab.pack(side=tk.LEFT,padx=10)
        
        self.var_avgCount = tk.IntVar(value=0)
        entry_avgCount = tk.Spinbox(frame_row1, width=5, from_=0, to=100, textvariable=self.var_avgCount)
        entry_avgCount.pack(side=tk.LEFT) 
        
        frame_row2 = tk.LabelFrame(self)
        frame_row2.pack(anchor=tk.W)
        
        comit_btn = tk.Button(frame_row2, text="前年比較分析", command=self.out_compar_ana)
        comit_btn.pack()    
        
        comit_btn = tk.Button(frame_row2, text="ヒストグラム分析", command=self.out_histogram)
        comit_btn.pack()               

        comit_btn = tk.Button(frame_row2, text="散布図分析", command=self.out_scatterplot)
        comit_btn.pack()  

        
        self.cls_period = cls_period_instance
        self.cls_cound = cls_cound_instance
       
        
    
    def out_compar_ana(self):
        """
        売上比較分析処理

        Returns
        -------
        str
            DESCRIPTION.

        """
        
        try:
            # 商品名抽出        
            _brand = self.cls_cound.select_brand_var.get()
            _line = self.cls_cound.select_line_var.get()
            _items = self.cls_cound.get_finditems()
            _from, _to = self.cls_period.get_cound_perid_formaｎdto()
            _weeks = self.cls_period.get_select_dayofweeks()
                                    
            # 商品名抽出
            if self.cls_cound.radio_jyoken.get()==2:
                if not _items:
                    msg.showwarning(msg.WARNING,"抽出する商品名を選択してください。")
                    return "break"  
                l_val = "{}_{}".format(_brand, ",".join(_items))
            else:
                l_val = "{}_{}".format(_brand, _line)
                        
            df_out = salesDataFrame.get_cound_df(_brand, _line, _items, _from, _to, _weeks)
            
            #TODO:現在エラー発生、 比較分析をどこまでやるか確認する必要あり
            
            if self.cls_period.get() == const.FLG_MONTH:
                _from2 = _from - relativedelta(years=1)
                _to2 = _to - relativedelta(years=1)
                df_out2 = salesDataFrame.get_cound_df(_brand, _line, _items, _from2, _to2, _weeks)
            
            # 売上情報の存在チェック
            if df_out.empty:
                msg.showwarning(msg.WARNING,"入力された期間の売上情報が存在しません")
                return "break"  
            
            key_val = None
            
            if self.cls_cound.radio_jyoken.get()==1:
                if self.cls_cound.select_brand_var.get() == "全取引先":
                    key_val = "t_name"
                else:                
                    if self.cls_cound.select_line_var.get() == "全ライン":
                        key_val = "l_name"
                    else:
                        key_val = "i_name"
            else:
                key_val = "i_name"
            
            
            df = df_out.groupby([f"{key_val}","day"], as_index=False).sum(numeric_only=True) 
            df2 = df_out2.groupby([f"{key_val}","day"], as_index=False).sum(numeric_only=True)  
                        
            df["year"]="1.当年"
            df2["year"]="2.前年"
                    
            # 結合するために前年の日付を同年に戻す
            df2["day"] = df2["day"].apply(lambda x: x + relativedelta(years=1))
            
            df_temp = df2.rename(columns={'count':'p_count','amount': 'p_amount'})
                        
            df3 = pd.merge(df, df_temp[[f"{key_val}","day","p_count","p_amount"]], on=[f"{key_val}","day"], how="outer")
            df3["amount"] = df3["amount"] / df3["p_amount"]
            df3["count"] = df3["count"] / df3["p_count"]
            df3["year"] = "3.前年比"
                 
            df4 = pd.concat([df, df2, df3])
            pivo1 = pd.pivot_table(df4, index=[f"{key_val}","year"], columns=["day"], values=["amount"])
            l = {}
            l["売上金額"]= pivo1
            l["売上数量"]= pd.pivot_table(df4, index=[f"{key_val}","year"], columns=["day"], values=["count"])
            
            self.out_excel(l, l_val)
        except Exception: 
            erMsg = "売上分析出力中にエラーが発生しました。"
            msg.showerror(msg.ERROR,erMsg)
            logging.exception(erMsg)  
            
       
    def out_excel(self, l_out_df, book_name) -> bool:
        """
        Excelファイルを出力する処理

        Parameters
        ----------
        out_df : TYPE
            DESCRIPTION.
        book_name : TYPE
            DESCRIPTION.
        sheet_name : TYPE
            DESCRIPTION.

        Raises
        ------
        
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        try:
            fileNmae = f"{book_name}_売上分析"
            iDir = os.path.abspath(os.path.dirname(__file__))       
            file_path = filedialog.asksaveasfilename(initialfile=fileNmae, initialdir=iDir, defaultextension="xlsx")
            
            if file_path:                
                # ファイルが存在しない場合、新規作成する
                if not os.path.isfile(file_path):
                    create_file = op.Workbook()
                    create_file.save(file_path)      
                                       
                           
                #　エクセルファイルを書き込みする処理
                with pd.ExcelWriter(file_path) as writer:
                    
                    for key in l_out_df.keys():
                    
                        l_out_df[key].to_excel(writer, startrow=0, na_rep=0, sheet_name=f"{key}") 
                     
                msg.showinfo(msg.INFO, "処理を正常に終了しました。")
            else:
                msg.showwarning(msg.INFO, "処理を中断しました。")
            
        except Exception: 
            erMsg = "Excelファイル出力中にエラーが発生しました。"
            logging.exception(erMsg)  
            raise  
                       

    def out_timeseries_chart(self): 
        """
        2024.07.31
        「時系列分析」ボタン押下処理　、エクセルへ出力する処理
    
        Parameters
        ----------
        event : TYPE
            DESCRIPTION.
    
        Returns
        -------
        str
            DESCRIPTION.
    
        """       
            
        try:              
            
            global p_x
            global p_y
            global p_label
                        
            _brand = self.cls_cound.select_brand_var.get()
            _line = self.cls_cound.select_line_var.get()
            _items = self.cls_cound.get_finditems()
            _from, _to = self.cls_period.get_cound_perid_formaｎdto()
                        
            _weeks = self.cls_period.get_select_dayofweeks()
                                    
            # 商品名抽出
            if self.cls_cound.radio_jyoken.get()==2:
                if not _items:
                    msg.showwarning(msg.WARNING,"抽出する商品名を選択してください。")
                    return "break"  
                l_val = "{}:{}".format(_brand, ",".join(_items))
            else:
                l_val = "{}:{}".format(_brand, _line)
                        
            df_out = salesDataFrame.get_cound_df(_brand, _line, _items, _from, _to, _weeks)
            
            # 売上情報の存在チェック
            if df_out.empty:
                msg.showwarning(msg.WARNING,"入力された期間の売上情報が存在しません")
                return "break"  
                                                                                               
            use_col = self.var_radio_select_vals.get()
                    
            # 時系列分析図出力処理-----
            df_out = df_out[["day",use_col]].groupby(["day"], as_index=False).sum(numeric_only=True)
            
            fig, ax = plt.subplots(figsize=(10, 8), dpi=100)            
            x = df_out["day"]
            y = df_out[use_col]
            
            # 移動平均算出用処理
            val = self.var_avgCount.get() 
            if val > 0:                    
                y = y.rolling(val).mean()
            
            ax.plot(x, y, linewidth=0.5, label=l_val)
                         
            # 前回表示したプロットデータが存在する場合
            if salesDataFrame.pre_timeserieschart:
                ax.plot(salesDataFrame.pre_timeserieschart[0], salesDataFrame.pre_timeserieschart[1], linewidth=0.5, label=salesDataFrame.pre_timeserieschart[2])
                
            #_from _toを文字列に変換する
            str_from = dt.strftime(_from, const.FORMAT_YMD)
            str_to = dt.strftime(_to, const.FORMAT_YMD)
            ax.scatter(x, y)
            ax.set_title(f"時系列分析{str_from}～{str_to}")
            ax.set_xlabel("日付")
            ax.set_ylabel(USECOLS_NAME[use_col])
            #　データラベルの追加
            ax.legend()        
            # グリッド線の追加
            ax.grid(True)     
                        
            
            plot_app = tk.Tk()
            # plot_app.geometry("600x750")         
            canvas = FigureCanvasTkAgg(fig, master=plot_app)  # Tkinter ウィンドウに埋め込む
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack()
            
            # 
            salesDataFrame.pre_timeserieschart = [x, y, l_val]
                            

        except Exception: 
            erMsg = "売上分析出力中にエラーが発生しました。"
            msg.showerror(msg.ERROR,erMsg)
            logging.exception(erMsg)  
            
    
    def out_histogram(self):
        """
        「ヒストグラム分析」ボタン押下処理　

        Returns
        -------
        str
            DESCRIPTION.

        """
        global pre_val
        global pre_key
                
        _brand = self.cls_cound.select_brand_var.get()
        _line = self.cls_cound.select_line_var.get()
        _items = self.cls_cound.get_finditems()
        _from, _to = self.cls_period.get_cound_perid_formaｎdto()
        _weeks = self.cls_period.get_select_dayofweeks()
                                
        # 商品名抽出
        if self.cls_cound.radio_jyoken.get()==2:
            if not _items:
                msg.showwarning(msg.WARNING,"抽出する商品名を選択してください。")
                return "break"  
            l_val = "{}:{}".format(_brand, ",".join(_items))
        else:
            l_val = "{}:{}".format(_brand, _line)
                    
        df_out = salesDataFrame.get_cound_df(_brand, _line, _items, _from, _to, _weeks)
        
        # 売上情報の存在チェック
        if df_out.empty:
            msg.showwarning(msg.WARNING,"入力された期間の売上情報が存在しません")
            return "break"   

        if self.var_select_cal.get() == 0:
            temp = df_out.groupby(["day"]).sum(numeric_only=True)    
        else:
            temp = df_out.groupby(["day"]).mean(numeric_only=True)            
                
        # color = plt.cm.tab10(0)
        
        use_col = self.var_radio_select_vals.get()
            
        detal = self.cls_period.get_period_day_count()
        
        fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
        ax.hist(temp[use_col], bins=30, alpha=0.5, label=l_val)
        
        
        if salesDataFrame.pre_histogram:
            ax.hist(salesDataFrame.pre_histogram[0], bins=30, alpha=0.5, label=salesDataFrame.pre_histogram[1])
            
        # タイトル
        ax.set_title(f'ヒストグラム分析:({detal})')
        
        # x軸とy軸にラベルの追加
        ax.set_xlabel(USECOLS_NAME[use_col])
        ax.set_ylabel('Frequency')
        
        #　データラベルの追加
        ax.legend()        
        # グリッド線の追加
        ax.grid(True)
        

        plot_app = tk.Tk()
        # plot_app.geometry("600x750")         
        canvas = FigureCanvasTkAgg(fig, master=plot_app)  # Tkinter ウィンドウに埋め込む
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        
        salesDataFrame.pre_histogram = [temp[use_col], l_val]
        
            
    def out_scatterplot(self):
        """
        
        「回帰分析」ボタン押下処理　
        Returns
        -------
        str
            DESCRIPTION.

        """        
        if self.cls_period.radio_kind_period.get() == const.FLG_DAY:
            msg.showwarning(msg.WARNING,"「日別」の集計処理では散布図分析はできません。")
            return "break"  
        
        _brand = self.cls_cound.select_brand_var.get()
        _line = self.cls_cound.select_line_var.get()
        _items = self.cls_cound.get_finditems()
        _from, _to = self.cls_period.get_cound_perid_formaｎdto()
        _weeks = self.cls_period.get_select_dayofweeks()
                                
        # 商品名抽出
        if self.cls_cound.radio_jyoken.get()==2:
            if not _items:
                msg.showwarning(msg.WARNING,"抽出する商品名を選択してください。")
                return "break"  
            l_val = "{}:{}".format(_brand, ",".join(_items))
        else:
            l_val = "{}:{}".format(_brand, _line)
                    
        df_out = salesDataFrame.get_cound_df(_brand, _line, _items, _from, _to, _weeks)
        
        # 売上情報の存在チェック
        if df_out.empty:
            msg.showwarning(msg.WARNING,"入力された期間の売上情報が存在しません")
            return "break"   
                
        if self.var_select_cal.get() == 0:
            temp = df_out[["day","count","amount"]].groupby(["day"]).sum(numeric_only=True)
        else:
            temp = df_out[["day","count","amount"]].groupby(["day"]).mean(numeric_only=True) 
            
        # 平均単価算出
        temp["avg"] = temp["amount"]/temp["count"]
        
        col_name = self.var_radio_select_vals.get()
        
        x = temp["avg"]
        y = temp[col_name]
        
        
        fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
        
        ax.scatter(x, y, label=l_val)
        if salesDataFrame.pre_scatterplot:
            ax.scatter(salesDataFrame.pre_scatterplot[0], salesDataFrame.pre_scatterplot[1], label=salesDataFrame.pre_scatterplot[2])
        
        #_from _toを文字列に変換する
        str_from = dt.strftime(_from, const.FORMAT_YMD)
        str_to = dt.strftime(_to, const.FORMAT_YMD)
        ax.set_title(f"回帰分析：{str_from}～{str_to}")
        ax.set_xlabel(USECOLS_NAME["avg"])
        ax.set_ylabel(USECOLS_NAME[col_name])
        #　データラベルの追加
        ax.legend()        
        # グリッド線の追加
        ax.grid(True)
                
        plot_app = tk.Tk()
        # plot_app.geometry("600x750")         
        canvas = FigureCanvasTkAgg(fig, master=plot_app)  # Tkinter ウィンドウに埋め込む
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        
        salesDataFrame.pre_scatterplot = [x,y,l_val]        
        
    
class MyApp(tk.Tk):    
    def __init__(self):
        """
        システムのメイン処理

        Returns
        -------
        None.

        """
        super().__init__()

        self.title("売上分析システム")
        self.geometry("600x750")                
        self.frame2 = FrameInput(self)
        self.frame3 = FramePeriod(self)        
        self.frame4 = FrameCound(self)
        self.frame5 = FrameOutput(self, self.frame3, self.frame4)    
        
app = MyApp()
app.mainloop()


