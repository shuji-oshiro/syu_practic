# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:49:19 2025

@author: mkt05
"""
import os
import tkinter as tk
from tkinter import ttk, LabelFrame
import pandas as pd
import openpyxl as op
from py_pk import settings
from py_pk import analysis_data

import logging
from datetime import timedelta, datetime as dt
from dateutil.relativedelta import relativedelta  
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox as msg
import threading
import calendar
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

const = settings.Settings()        

USECOLS_NAME = {"amount":"売上金額","count":"売上数量","avg":"平均単価","":""}
plt.rcParams["font.family"] = "meiryo"

control_list =[DateEntry, tk.Checkbutton, ttk.Combobox, tk.Listbox, tk.Entry, tk.Spinbox]

def set_widget_status(wg_frame, state):                       
    for widget in wg_frame.winfo_children():  
        if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
            set_widget_status(widget, state)           
           
        for target_wg in control_list:
            if isinstance(widget, target_wg):
                widget.config(state=state)
                break    
      
class FrameInput(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="売上情報入力", bd=2)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        self.pack(padx=10, pady=10)

        """Create frame for database information"""
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        
        tk.Label(frame_row1, text="データベースパス：").pack(side=tk.LEFT)
        tk.Label(frame_row1, text=const.DB_PATH).pack(side=tk.LEFT)
        
        btn_GetInfo = tk.Button(frame_row1, text="店舗情報更新", 
                              command=self._update_mst_tenpo)
        btn_GetInfo.pack(side=tk.LEFT)
    
    def _update_mst_tenpo(self):
        
        # TODO:Update store master data
        #=======================================================================
        # """Update store master data"""
        # try:
        #     file_path = filedialog.askopenfilename(filetypes=[('', '*')]) 
        #     if file_path:
        #         df = process_db.update_mst_tenpo(file_path)
        #         salesDataFrame.df_tenpo = df
        #         msg.showinfo(msg.INFO, "店舗マスタ更新処理成功")
        # except Exception as e:
        #     msg.showinfo(msg.ERROR, "店舗マスタ更新処理失敗")
        #     logging.error(f"Store master update failed: {str(e)}" 
        #=======================================================================
        pass


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
        self._setup_ui()        
        
    def _setup_ui(self):
        """Setup UI components"""
        self.pack(anchor=tk.NW, padx=10, pady=10)

        # 2-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        btn_GetInfo = tk.Button(frame_row1, text="売上情報入力", command=self._push_inoputData)
        btn_GetInfo.pack()

        #売上情報ので使用する日付区間の設定値　-＞DataBaseName
        self.radio_kind_period = tk.StringVar(value="")               
                
        # 2-2 日別売上抽出
        self.frame_row2 = tk.LabelFrame(self)
        self.frame_row2.pack(anchor=tk.W)
        frame_1 = tk.Frame(self.frame_row2)
        frame_1.pack(anchor=tk.W)            
        tk.Radiobutton(frame_1, text="日別", variable=self.radio_kind_period, value=const.TBLNAME_DAY, command=self._choice_datekind).pack(side=tk.LEFT)
        self.entry_from = DateEntry(frame_1, date_pattern=const.ENTRY_DISP_FORM)
        self.entry_from.pack(side=tk.LEFT)
        tk.Label(frame_1, text="～").pack(side=tk.LEFT)
        #　集計終了日
        self.entry_to = DateEntry(frame_1, date_pattern=const.ENTRY_DISP_FORM)
        self.entry_to.pack(side=tk.LEFT)
        
        # 2-2 日別売上抽出 曜日指定
        frame_2 = tk.Frame(self.frame_row2)
        frame_2.pack()
                
        self.week_flg = []
        for _ in range(0,7):
            flg = tk.BooleanVar()
            flg.set(True)
            self.week_flg.append(flg)
            
        # チェックボックスの作成
        tk.Checkbutton(frame_2, text="月", variable=self.week_flg[0]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_2, text="火", variable=self.week_flg[1]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_2, text="水", variable=self.week_flg[2]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_2, text="木", variable=self.week_flg[3]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_2, text="金", variable=self.week_flg[4]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_2, text="土", variable=self.week_flg[5]).pack(side=tk.LEFT)
        tk.Checkbutton(frame_2, text="日", variable=self.week_flg[6]).pack(side=tk.LEFT)
        
        # 2-3　週別売上抽出
        self.frame_row3 = tk.LabelFrame(self)
        self.frame_row3.pack(anchor=tk.W)        
        tk.Radiobutton(self.frame_row3, text="週別", variable=self.radio_kind_period, value=const.TBLNAME_WEEK, command=self._choice_datekind).pack(side=tk.LEFT)
        
        self.var_select_week_from = tk.StringVar()
        self.comb_week_from = ttk.Combobox(self.frame_row3, state="readonly", textvariable=self.var_select_week_from)
        self.comb_week_from.pack(side=tk.LEFT)
        tk.Label(self.frame_row3, text="～").pack(side=tk.LEFT)
        self.var_select_week_to = tk.StringVar()
        self.comb_week_to = ttk.Combobox(self.frame_row3, state="readonly", textvariable=self.var_select_week_to)
        self.comb_week_to.pack(side=tk.LEFT)
        
        #2-4　月別売上抽出
        self.frame_row4 = tk.LabelFrame(self)
        self.frame_row4.pack(anchor=tk.W)      
        tk.Radiobutton(self.frame_row4, text="月別", variable=self.radio_kind_period, value=const.TBLNAME_MONTH, command=self._choice_datekind).pack(side=tk.LEFT)
        
        self.var_select_mont_from = tk.StringVar()
        self.comb_mont_from = ttk.Combobox(self.frame_row4, state="readonly", textvariable=self.var_select_mont_from)
        self.comb_mont_from.pack(side=tk.LEFT)
        tk.Label(self.frame_row4, text="～").pack(side=tk.LEFT)
        self.var_select_mont_to = tk.StringVar()
        self.comb_mont_to = ttk.Combobox(self.frame_row4, state="readonly", textvariable=self.var_select_mont_to)
        self.comb_mont_to.pack(side=tk.LEFT)
        
        
    def get_cound_perid_formaｎdto(self) -> (dt, dt):
        """
        抽出条件の日、週、月のFORM・TOの日付をDatetime型で取得

        Returns
        -------
        _from : TYPE
            DESCRIPTION.
        _to : TYPE
            DESCRIPTION.

        """
        _from,_to = None,None
        if self.radio_kind_period.get() == const.TBLNAME_DAY:
            _from = dt.combine(self.entry_from.get_date() ,dt.min.time())  # @UndefinedVariable
            _to = dt.combine(self.entry_to.get_date(), dt.min.time())  # @UndefinedVariable
            
            
        elif self.radio_kind_period.get() == const.TBLNAME_WEEK:
            _from = dt.strptime(self.var_select_week_from.get(), const.FORMAT_YMD)
            _to = dt.strptime(self.var_select_week_to.get(), const.FORMAT_YMD)
            
            
        elif self.radio_kind_period.get() == const.TBLNAME_MONTH:
            _from = dt.strptime(self.var_select_mont_from.get(), const.FORMAT_YM)
            _to = dt.strptime(self.var_select_mont_to.get(), const.FORMAT_YM)
            _to = _to.replace(day=calendar.monthrange(_to.year, _to.month)[1]) # TODO：月末取得処理
            
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
        if self.radio_kind_period.get() == const.TBLNAME_DAY:
            for i in range(0,7):
                if self.week_flg[i].get():
                    targetWeek.append(i)  
                
        return targetWeek
        
        
    def _update_database(self, fle): #売上情報を更新する処理
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
            if salesDataFrame.update_salesData(fle):
                msg.showinfo(msg.INFO,"売上情報の更新処理に成功しました")
                
            else:
                msg.showerror(msg.ERROR, "売上情報の更新処理に失敗しました")
                    
        except Exception: 
            msg.showerror(msg.ERROR, "売上情報の更新処理に失敗しました")            
        
        finally:
            # スレッド処理終了
            app.after(0, loading_window.destroy)
            return "break" 
        
        
    def _push_inoputData(self):
        """
        [売上情報入力]ボタン押下時の処理

        Returns
        -------
        None.

        """
        
        """処理中のダイアログを表示"""
        
        df = salesDataFrame.get_currentData()
        if df.empty:
            msg.showwarning(msg.WARNING, "読み込む売上情報の集計期間を選択してください")
            return "break"
        
        typ = [('CSVファイル', '*.csv')]            
        fle = filedialog.askopenfilenames(filetypes = typ)  
        if len(fle) > 0:    
            fle = sorted(fle)    
        else:
            return "break"
        
        global loading_window
        loading_window = tk.Toplevel(app)  # 新しいウィンドウ
        loading_window.title("処理中")
        loading_window.geometry("300x100")
        loading_window.resizable(False, False)
        
        ttk.Label(loading_window, text="データ更新中...\nしばらくお待ちください", font=("Arial", 12)).pack(pady=20)
        loading_window.grab_set()  # ダイアログを最前面に固定
        
        # 別スレッドでデータベース更新処理を実行
        threading.Thread(target=lambda:self._update_database(fle), daemon=True).start()


    def _get_salesdata(self):
        """
        選択した売上集計区分の売上情報を取得する処理-＞マルチスレッド

        Returns
        -------
        None.

        """
        
                
        try:                       
            
            df = salesDataFrame.get_currentData()
            if df.empty:                
                df = salesDataFrame.get_salesData()
                                                               
            if self.radio_kind_period.get() == const.TBLNAME_DAY:  
                self.entry_to.set_date(salesDataFrame.get_maxdate())
                self.entry_from.set_date(salesDataFrame.get_mindate())
 
            elif self.radio_kind_period.get() == const.TBLNAME_WEEK:                     
                # 集計期間の日付を更新する            
                u_day = df["day"].unique().tolist().sorted()
                self.comb_week_from["values"] = u_day
                self.comb_week_to["values"] = u_day
                self.var_select_week_from.set(min(u_day))               
                self.var_select_week_to.set(max(u_day)) 
                  
                 
            elif self.radio_kind_period.get() == const.TBLNAME_MONTH:  
                u_day = df["day"].unique().tolist()
                u_day = sorted(u_day)
                self.comb_mont_from["values"] = u_day
                self.comb_mont_to["values"] = u_day
                self.var_select_mont_from.set(min(u_day))               
                self.var_select_mont_to.set(max(u_day))                         

            # TODO：後日機能追加
            # # 集計期間の選択によって曜日選択の有効無効を設定する
            # if not self.radio_kind_period.get() == FLG_DAY:
            #     for widget in self.frame_row3.winfo_children():       
            #         widget.config(state=tk.DISABLED)
            # else:
            #     for widget in self.frame_row3.winfo_children():       
            #         widget.config(state=tk.NORMAL)
                                    
        except Exception: 
            msg.showerror(msg.ERROR, Exception)
        
        finally:        
            # スレッド処理終了
            app.after(0, loading_window.destroy)
                    

    def _choice_datekind(self):
        """
        売上集計期間を選択した時に発生するイベント

        Returns
        -------
        None.

        """
        
        """処理中のダイアログを表示"""
        
        salesDataFrame.current_df_type = self.radio_kind_period.get()
        
        global loading_window
        loading_window = tk.Toplevel(app)  # 新しいウィンドウ
        loading_window.title("処理中")
        loading_window.geometry("300x100")
        loading_window.resizable(False, False)
    
        ttk.Label(loading_window, text="データ取得中...\nしばらくお待ちください", font=("Arial", 12)).pack(pady=20)
        loading_window.grab_set()  # ダイアログを最前面に固定
    
        #  別スレッドでデータベース更新処理を実行
        threading.Thread(target=self._get_salesdata, daemon=True).start()
                        
        if self.radio_kind_period.get() == const.TBLNAME_DAY: 
            set_widget_status(self.frame_row2, tk.NORMAL)
            set_widget_status(self.frame_row3, tk.DISABLED)
            set_widget_status(self.frame_row4, tk.DISABLED)                                 
            #===================================================================
            # for widget in self.frame_row2.winfo_children():  
            #     if isinstance(widget, tk.Frame):
            #         continue           
            #     if not isinstance(widget, tk.Radiobutton):
            #         widget.config(state=tk.DISABLED)
            #===================================================================
                    
        elif self.radio_kind_period.get() == const.TBLNAME_WEEK:
            set_widget_status(self.frame_row2, tk.DISABLED)
            set_widget_status(self.frame_row3, tk.NORMAL)
            set_widget_status(self.frame_row4, tk.DISABLED)  
        
        elif self.radio_kind_period.get() == const.TBLNAME_MONTH:
            set_widget_status(self.frame_row2, tk.DISABLED)
            set_widget_status(self.frame_row3, tk.DISABLED)
            set_widget_status(self.frame_row4, tk.NORMAL)  
                              

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
        self._setup_ui()
        
        
    def _setup_ui(self):
        """Setup UI components"""
        self.pack(anchor=tk.NW, padx=10,pady=5)                           
        
        # 3-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        
        var_brand = salesDataFrame.dataframes[const.TBLNAME_BRAND]["t_name"].unique().tolist()
        var_brand.insert(0,"全取引先")
        var_brand.append("その他取引先")
        
        self.select_brand_var = tk.StringVar()
        cp_comb = ttk.Combobox(frame_row1, values=var_brand ,state="readonly", textvariable=self.select_brand_var)
        cp_comb.current(0)
        cp_comb.pack(side=tk.LEFT)
        
        self.var_checked_without = tk.BooleanVar()
        tk.Checkbutton(frame_row1, text="和洋菓子課除外", variable=self.var_checked_without).pack(side=tk.LEFT)
        
        self.radio_jyoken = tk.IntVar(value=1)
        # 3-2
        self.frame_row2 = tk.LabelFrame(self)
        self.frame_row2.pack(anchor=tk.W)
        
        tk.Radiobutton(self.frame_row2, text="ライン別", variable=self.radio_jyoken, value=const.SELECT_LINE, command=self.chang_coundkbn).pack(side=tk.LEFT)
        
        var_line = salesDataFrame.dataframes[const.TBLNAME_LINE]["l_name"].tolist()
        var_line.insert(0,"全ライン")
        
        self.select_line_var = tk.StringVar()
        
        line_comb = ttk.Combobox(self.frame_row2, values=var_line ,state="readonly", textvariable=self.select_line_var)
        line_comb.current(0)
        line_comb.pack(side=tk.LEFT)
        
        # 3-3
        self.frame_row3 = tk.LabelFrame(self)
        self.frame_row3.pack(anchor=tk.W)
        
        tk.Radiobutton(self.frame_row3, text="商品別", variable=self.radio_jyoken, value=const.SELECT_ITEM, command=self.chang_coundkbn).pack(side=tk.LEFT)

        # 商品コードを入力するフォーム
        self.var_icode = tk.IntVar(value=0)
        entry_icode = tk.Spinbox(self.frame_row3, width=5, from_=0, to=9999, textvariable=self.var_icode)
        entry_icode.bind("<Return>", lambda event: self._setfindItems())
        entry_icode.pack(side=tk.LEFT) 
        
        
        # 商品名のキーワードを入力するフォーム
        self.var_tname = tk.StringVar()
        entry_name = tk.Entry(self.frame_row3, textvariable=self.var_tname)
        entry_name.bind("<Return>", lambda event: self._setfindItems(True))
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
        self.lbox_findItems.bind("<Double-Button-1>", self._setfindItems)
        self.lbox_findItems.config(state=tk.DISABLED)
        
        
    def _setfindItems(self, flg=False):
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
        
        # TODO:リストから商品情報を取得する処理　未検証処理
        df = salesDataFrame.get_currentData()
        if df.empty:        
            msg.showwarning(msg.WARNING, "売上情報が存在しません")
        
        
        if flg:
            # 商品名による抽出
            df = df[df["i_name"].str.contains(self.var_tname.get())]
        else:
            # 商品コードによる抽出
            df = df[df["i_code"]==self.var_icode.get()]
                    
        ls = df['i_code'].astype(str).str.cat(df['i_name'], sep=',')
        ls = ls.unique().tolist()

        if len(ls) > 0:
            self.var_foudlist.set(ls) 
        else:
            msg.showwarning(msg.WARNING, "検索条件に合致する商品情報がありません。")
                        
        return "break"
    
    
    def get_selectitems(self):
        """
        一覧表示されている商品リストから選択された商品名を返す

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
        
         
    def chang_coundkbn(self):
        """
        抽出条件ボタン選択時の処理
    
        Returns
        -------
        None.
    
        """
        if self.radio_jyoken.get() == const.SELECT_LINE:            
            set_widget_status(self.frame_row2, tk.NORMAL)
            set_widget_status(self.frame_row3, tk.DISABLED)
            set_widget_status(self.frame_row4, tk.DISABLED)
            
            #===================================================================
            # for widget in self.frame_row2.winfo_children():
            #     if not isinstance(widget, tk.Radiobutton):
            #         widget.config(state=tk.NORMAL)
            # 
            # for widget in self.frame_row3.winfo_children():
            #     if not isinstance(widget, tk.Radiobutton):         
            #         widget.config(state=tk.DISABLED)
            # 
            # for widget in self.frame_row4.winfo_children():
            #     if not isinstance(widget, tk.Radiobutton):
            #         widget.config(state=tk.DISABLED)
            #===================================================================
            
        elif self.radio_jyoken.get() == const.SELECT_ITEM:
            set_widget_status(self.frame_row2, tk.DISABLED)
            set_widget_status(self.frame_row3, tk.NORMAL)
            set_widget_status(self.frame_row4, tk.NORMAL)
                   

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
        self.cls_period = cls_period_instance
        self.cls_cound = cls_cound_instance   
        self._setup_ui()
              
        self.labelFrame_out = LabelFrame(self, text="分析結果", width = 900, height = 600)    
        self.labelFrame_out.pack(anchor=tk.NW)    
                
        
    def _setup_ui(self):
        """Setup UI components"""
                
        frame_row0 = tk.LabelFrame(self)
        frame_row0.pack(anchor=tk.W)
        self.var_radio_select_vals = tk.StringVar(value="amount")    
        tk.Radiobutton(frame_row0, text="売上金額", variable=self.var_radio_select_vals, value="amount").pack(side=tk.LEFT)
        tk.Radiobutton(frame_row0, text="売上数量", variable=self.var_radio_select_vals, value="count").pack(side=tk.LEFT)
        tk.Button(frame_row0, text="CSVデータ出力", bg="white", command=lambda:self._push_buttons(0)).pack(side=tk.LEFT)
        
        
        # 3-1        
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        tk.Button(frame_row1, text="集計表出力", command=lambda:self._push_buttons(1)).pack(side=tk.LEFT)
        tk.Button(frame_row1, text="時系列分析", command=lambda:self._push_buttons(2)).pack(side=tk.LEFT)       
        tk.Button(frame_row1, text="ヒストグラム分析", command=lambda:self._push_buttons(3)).pack(side=tk.LEFT)               
        tk.Button(frame_row1, text="散布図分析", command=lambda:self._push_buttons(4)).pack(side=tk.LEFT)  
        
        frame_avg = tk.Frame(frame_row1)
        frame_avg.pack(side=tk.LEFT, padx=10)
        tk.Label(frame_avg, text="移動平均集計").pack(side=tk.LEFT)
        self.var_avgCount = tk.IntVar(value=0)
        tk.Spinbox(frame_avg, width=5, from_=0, to=100, textvariable=self.var_avgCount).pack(side=tk.LEFT) 
        
        # TODO：前年、期間指定
        frame_comper = tk.Frame(frame_row1)
        frame_comper.pack(side=tk.LEFT, padx=10)
        
        # TODO: 日付操作処理の検証必要
        self.var_checked_comper = tk.BooleanVar()
        tk.Checkbutton(frame_comper, text="比較", variable=self.var_checked_comper).pack(side=tk.LEFT)
        self.var_select_compar = tk.IntVar(value=0)
        tk.Radiobutton(frame_comper, text="前年", variable=self.var_select_compar, value=0, command=self.chang_coundkbn).pack(side=tk.LEFT)
        tk.Radiobutton(frame_comper, text="前月", variable=self.var_select_compar, value=1, command=self.chang_coundkbn).pack(side=tk.LEFT)
        tk.Radiobutton(frame_comper, text="前週", variable=self.var_select_compar, value=2, command=self.chang_coundkbn).pack(side=tk.LEFT)
        self.entry_from_pre = DateEntry(frame_comper, date_pattern=const.ENTRY_DISP_FORM)
        self.entry_from_pre.pack(side=tk.LEFT)
    
    def chang_coundkbn(self):
        """
        抽出条件ボタン選択時の処理

        Returns
        -------
        None.

        """
        _from, _ = self.cls_period.get_cound_perid_formaｎdto()
        
        if not _from:
            msg.showwarning(msg.WARNING, "集計期間を選択してください")
            return "break"
        
        if self.var_select_compar.get() == 0: #前年          
            _from_pre = _from - relativedelta(years=1)
            
        elif self.var_select_compar.get() == 1: #前月
            _from_pre = _from - relativedelta(months=1)
          
            
        elif self.var_select_compar.get() == 2: #前週
            _from_pre = _from - relativedelta(weeks=1)
            delta_days = (_from_pre.weekday() - 0) % 7
            _from_pre = _from_pre - timedelta(days=delta_days)
        
        self.entry_from_pre.set_date(_from_pre)               
       

    def _show_plotData(self, fig=None, df=pd.DataFrame):
        """
        フレームに分析データを表示する処理

        Returns
        -------
        None.

        """
                       
        for widget in self.labelFrame_out.winfo_children():  # フレーム内の全ウィジェットを削除
            widget.destroy()
        
        if not df.empty :
            
            # スタイルの設定
            style = ttk.Style()
            # TreeViewの全部に対して、フォントサイズの変更
            style.configure("Treeview",font=("",11))
            # TreeViewのHeading部分に対して、フォントサイズの変更と太字の設定
            # style.configure("Treeview.Heading",font=("",14,"bold"))
            
            tree_col = ["_".join(col) for col in df.columns.to_flat_index()]
            tree_col.insert(0, "keyval")
                        
            tree = ttk.Treeview(self.labelFrame_out, columns=tree_col, show="headings", height=25)
            # ヘッダーの設定
            for col in tree_col:
                tree.heading(col, text=col)  # ヘッダーのラベル
                tree.column(col, anchor="center", width=100)  # カラム幅
            
            def format_values(row):                
                return (row[0],
                         f"{round(row[1]):,}", f"{round(row[2]):,}",f"{round(row[3]):,}",
                         f"{round(row[4]):,}", round(row[5],1), round(row[6],1),
                         f"{row[7]:.1%}", f"{row[8]:.1%}", f"{row[9]:.1%}")
             
            # DataFrame のデータを一括設定
            for row in df.itertuples(index=True):
                tree.insert("", "end", values=format_values(row))
                
            # スクロールバーを追加
            scroll_y = ttk.Scrollbar(self.labelFrame_out, orient=tk.VERTICAL, command=tree.yview)
            scroll_x = ttk.Scrollbar(self.labelFrame_out, orient=tk.HORIZONTAL, command=tree.xview)

            tree.configure(yscrollcommand=scroll_y.set)
            tree.configure(xscrollcommand=scroll_x.set)
            
            # レイアウト配置（grid を使用）
            tree.grid(row=0, column=0, sticky="nsew")
            scroll_y.grid(row=0, column=1, sticky="ns")
            scroll_x.grid(row=1, column=0, sticky="ew")
            
            # `frame` の中で `Treeview` が自動拡張するように設定
            self.labelFrame_out.grid_rowconfigure(0, weight=1)
            self.labelFrame_out.grid_columnconfigure(0, weight=1)
            
                        
            #===================================================================
            # scroll_y.pack(side="right", fill="y")    
            # scroll_x.pack(side="bottom", fill="x")  
            # 
            # tree.pack(expand=True, fill="both")  
            #===================================================================
            
        else:                                  
            canvas = FigureCanvasTkAgg(fig, master=self.labelFrame_out)  # Tkinter フレームに埋め込む
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack()
        
            
    def _push_buttons(self, out_typ):
        # 商品名抽出        
        _brand = self.cls_cound.select_brand_var.get()
        _line = self.cls_cound.select_line_var.get()
        _items = self.cls_cound.get_selectitems()
        _from, _to = self.cls_period.get_cound_perid_formaｎdto()
        _weeks = self.cls_period.get_select_dayofweeks()
        _without = self.cls_cound.var_checked_without.get()
                                
        # 商品名抽出
        if self.cls_cound.radio_jyoken.get()==const.SELECT_ITEM:
            if not _items:
                msg.showwarning(msg.WARNING,"抽出する商品名を選択してください。")
                return "break"  
            l_val = "{}_{}".format(_brand, ",".join(_items))
        else:
            l_val = "{}_{}".format(_brand, _line)
                    
        df_out = salesDataFrame.get_datacondition(None if _brand == "全取引先" else _brand,
                                                   None if _line == "全ライン" else _line,
                                                    _items,
                                                     _from,
                                                      _to,
                                                       _weeks,
                                                       _without)
        # 売上情報の存在チェック
        if df_out.empty:
            msg.showwarning(msg.WARNING,"入力された期間の売上情報が存在しません")
            return "break"
                      
        diff_day = (_to -_from).days #期間取得               
        
        _from2 = dt.strptime(self.entry_from_pre.get(), const.FORMAT_YMD)                
        _to2 = _from2 + relativedelta(days=diff_day) 
                 
        df_out2 = salesDataFrame.get_datacondition(None if _brand == "全取引先" else _brand,
                                                   None if _line == "全ライン" else _line,
                                                    _items,
                                                     _from2,
                                                      _to2,
                                                       _weeks,
                                                       _without)
        
        #diff_day2 = (_to2 -_from2).days #期間取得    
            
        df_list = {"now":[df_out,_from,_to, len(df_out["day"].unique())]}  
        if out_typ == 0 or out_typ == 1 or self.var_checked_comper.get():
            df_list["past"]=[df_out2, _from2, _to2, len(df_out2["day"].unique())]        
             
        
        if out_typ == 0:
            self._out_compar_ana(df_list, l_val, _line, _items, _brand, True)
        
        elif out_typ == 1:
            self._out_compar_ana(df_list, l_val, _line, _items, _brand)
             
        elif out_typ == 2: 
            self._out_timeseries_chart(df_list, l_val)
         
        elif out_typ == 3: 
            self._out_histogram(df_list, l_val)
              
        elif out_typ == 4: 
            self._out_scatterplot(df_list, l_val)
    
    
    def _out_compar_ana(self, df_list, l_val, _line, _items, _brand, csv_flg=False):
        """
        売上比較分析処理

        Returns
        -------
        str
            DESCRIPTION.

        """
        
        try:
            
            key_val = None                       
                        
            sheetName=""                        
            if self.cls_cound.select_brand_var.get() == "全取引先":               
                key_val = "t_name"
                if self.cls_cound.radio_jyoken.get()==const.SELECT_LINE:
                    sheetName = _line
                else:                  
                    sheetName = "_".join(_items)                       
            else:
                if self.cls_cound.radio_jyoken.get()==const.SELECT_LINE:                    
                    if self.cls_cound.select_line_var.get() == "全ライン":
                        sheetName = _brand    
                        key_val = "l_name"                   
                    else:
                        sheetName = _line  
                        key_val = "i_name"                      
                else:
                    key_val = "i_name"  
                    sheetName = _brand
                      
            df_out, _from, _to, diff_day = df_list["now"] 
            df_out2, _from2, _to2, diff_day2 = df_list["past"] 
                                      
            df = df_out.groupby([key_val], as_index=False).sum(numeric_only=True)
            df["unit"] = df["amount"]/df["count"]
            df["year"] = "実績"
                        
            if not df_out2.empty:
                df2 = df_out2.groupby([key_val], as_index=False).sum(numeric_only=True)
                df2["unit"] = df2["amount"]/df2["count"]
                df2["year"] = "比較"   
                df3 = pd.concat([df,df2])    
            pivo_df = pd.pivot_table(df3, index=[key_val], columns="year", values=["amount","count","unit"])
            pivo_df["amount","増減率"] = pivo_df["amount","実績"] / pivo_df["amount","比較"]
            pivo_df["count","増減率"] = pivo_df["count","実績"] / pivo_df["count","比較"]
            pivo_df["unit","増減率"] = pivo_df["unit","実績"] / pivo_df["unit","比較"]
            
            pivo_df = pivo_df.fillna(0)

            head_str = f"実績期間：{_from.strftime('%Y年%m月%d日')}～{_to.strftime('%Y年%m月%d日')}({diff_day})　比較期間{_from2.strftime('%Y年%m月%d日')}～{_to2.strftime('%Y年%m月%d日')}({diff_day2})　"
                
            self._show_plotData(df=pivo_df)  
             
            if csv_flg:
                self._out_excel(pivo_df, l_val, sheetName, head_str)                
                
        except Exception: 
            erMsg = "売上分析出力中にエラーが発生しました。"
            msg.showerror(msg.ERROR,erMsg)
            logging.exception(erMsg)  
            
       
    def _out_excel(self, pivo_df, book_name, sheetName, head_str) -> bool:
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
                    pivo_df.to_excel(writer, startrow=1, na_rep=0 ,sheet_name=sheetName) 
                    # workbook = writer.book
                    worksheet = writer.sheets[sheetName]
                    # カンマ区切り（千単位）、パーセント、整数のフォーマット設定
                    excel_col = ["B","C","D","E","F","G","H","I","J"]
                    col_fm = ["#,##0", "#,##0", "#,##0", "#,##0", "0.0", "0.0", "0.0%", "0.0%", "0.0%"]
                    worksheet["A1"] = head_str
                    
                    for col, format_code in zip(excel_col, col_fm): 
                        for cell in worksheet[col]:                            
                            cell.number_format = format_code
                     
                msg.showinfo(msg.INFO, "処理を正常に終了しました。")
            else:
                msg.showwarning(msg.INFO, "処理を中断しました。")
            
        except Exception: 
            erMsg = "Excelファイル出力中にエラーが発生しました。"
            logging.exception(erMsg)  
            raise  


    def _out_timeseries_chart(self, df_list, l_val): 
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
                                                                                                           
            use_col = self.var_radio_select_vals.get()  
                  
            fig, ax = plt.subplots(figsize=(8, 6)) 
            x = []            
            for key in df_list.keys():              
                df_out, _from, _to, _dff = df_list[key]
                
                # 時系列分析図出力処理-----
                df_out = df_out[["day",use_col]].groupby(["day"], as_index=False).sum(numeric_only=True)         
                
                if len(x)==0: # X軸をそろえる為
                    x = df_out["day"]
                    
                y = df_out[use_col]
                
                #比較分析時、X軸の件数が異なる場合エラーとなるで処理を中断
                if (len(x)-len(y)) != 0:
                    msg.showerror(msg.ERROR,"比較対象となる期間が存在しない為、集計期間を短くてください")
                    return "break"
                 
                
                ax.plot(x, y,linewidth=0.5,label=f"{_from.strftime('%Y年%m月%d日')}～{_to.strftime('%Y年%m月%d日')}({_dff})")          
                #ax.xmargin = 5.0             
                # 移動平均算出用処理
                val = self.var_avgCount.get() 
                if val > 0:                    
                    y = y.rolling(val).mean()  
                    ax.plot(x, y, linewidth=0.5, marker='^', label=f"{key}:移動平均({val})")           
                             
            #ax.scatter(x, y)            
            ax.set_title(f"時系列分析:{l_val}")
            ax.set_xlabel("日付")
            #ax.set_xlim(0,100) # X軸の幅指定　件数
            #ax.set_ylim(0,100) # X軸の幅指定　件数     
                          
            #等間隔の数を設定する処理
            step_idx = np.arange(0, len(x), step=np.ceil(len(x)/6)) #等間隔の数を決める
            step_xval = x.loc[step_idx] #等間隔に沿った文字列データを取得
            ax.set_xticks(step_idx,step_xval) #ラベルに設定する
            
            ax.minorticks_on() #補助目盛を追加
            
            ax.set_ylabel(USECOLS_NAME[use_col])
            #　データラベルの追加
            ax.legend()        
            # グリッド線の追加
            ax.grid(True)                             
            
            self._show_plotData(fig=fig)
            salesDataFrame.pre_charts["timeseries"] = [x, y, l_val]

        except Exception: 
            erMsg = "売上分析出力中にエラーが発生しました。"
            msg.showerror(msg.ERROR,erMsg)
            logging.exception(erMsg)  
            
    
    def _out_histogram(self, df_list, l_val):
        """
        「ヒストグラム分析」ボタン押下処理　

        Returns
        -------
        str
            DESCRIPTION.

        """
        
        use_col = self.var_radio_select_vals.get()
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        for key in df_list.keys():
            df_out, _from, _to, _dff = df_list[key]
            
            temp = df_out.groupby(["day"]).mean(numeric_only=True)
            ax.hist(temp[use_col], bins=30, alpha=0.5, label=f"{_from.strftime('%Y年%m月%d日')}:{_to.strftime('%Y年%m月%d日')}({_dff})")
            
        
        #不要処理
        #=======================================================================
        # # 移動平均算出用処理
        # val = self.var_avgCount.get() 
        # if val > 0:     
        #     temp["temp2"] = temp[use_col].rolling(val).mean()              
        #     ax.hist(temp["temp2"], bins=30, alpha=0.5, label=f"移動平均({val})")
        #=======================================================================
            
        # タイトル
        ax.set_title(f'ヒストグラム分析:({l_val})')
        
        # x軸とy軸にラベルの追加
        ax.set_xlabel(USECOLS_NAME[use_col])
        ax.set_ylabel('Frequency')
        
        #　データラベルの追加
        ax.legend()        
        # グリッド線の追加
        ax.grid(True)
    
        self._show_plotData(fig=fig)        
        salesDataFrame.pre_charts["histogram"] = [temp[use_col], l_val]
        
            
    def _out_scatterplot(self, df_list, l_val):
        """
        
        「回帰分析」ボタン押下処理　
        Returns
        -------
        str
            DESCRIPTION.

        """        
              
        use_col = self.var_radio_select_vals.get()
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        for key in df_list.keys():
            
            df_out, _from, _to, _dff = df_list[key]
              
            temp = df_out[["day","count","amount"]].groupby(["day"]).mean(numeric_only=True) 
            
            # 平均単価算出
            temp["avg"] = temp["amount"]/temp["count"]        
        
            x = temp["avg"]
            y = temp[use_col]
                
            ax.scatter(x, y, alpha=0.5, label=f"{_from.strftime('%Y年%m月%d日')}:{_to.strftime('%Y年%m月%d日')}({_dff})")
        
        # 不要？？
        # 移動平均算出用処理
        #=======================================================================
        # val = self.var_avgCount.get()
        # if val > 0:     
        #     y = y.rolling(val).mean()              
        #     ax.scatter(x, y, label=f"移動平均({val})")
        #=======================================================================
        
        ax.set_title(f"回帰分析：{l_val}")
        ax.set_xlabel(USECOLS_NAME["avg"])
        ax.set_ylabel(USECOLS_NAME[use_col])
        #　データラベルの追加
        ax.legend()        
        # グリッド線の追加
        ax.grid(True)
                
        self._show_plotData(fig=fig)
        salesDataFrame.pre_charts["scatterplot"] = [x,y,l_val]        
        
    
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
        self.geometry("1400x700")  
        
        # left side frame input data      
        frame_main1 = tk.Frame(self)
        frame_main1.pack(anchor=tk.NW, side=tk.LEFT,padx=10, pady=10)
              
        self.frame2 = FrameInput(frame_main1)
        self.frame3 = FramePeriod(frame_main1)        
        self.frame4 = FrameCound(frame_main1)        
        
        # right side frame output data
        frame_main2 = tk.Frame(self)
        frame_main2.pack(anchor=tk.NW, side=tk.LEFT,  padx=10, pady=10)
        
        self.frame5 = FrameOutput(frame_main2, self.frame3, self.frame4)    
                
        
salesDataFrame = analysis_data.Analysis_data()
#salesDataFrame = SalesDataFrame()
app = MyApp()
app.mainloop()


