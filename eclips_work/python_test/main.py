# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:49:19 2025

@author: mkt05
"""
 
import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import openpyxl as op
from py_pk.settings import Settings
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

     

USECOLS_NAME = {"amount":"売上金額","count":"売上数量","avg":"平均単価","":""}
plt.rcParams["font.family"] = "meiryo"


def set_widget_status(wg_frame, state, l):
    for widget in wg_frame.winfo_children():  
        if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
            set_widget_status(widget, state, l)           
        
        for target_wg in l:
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
        tk.Label(frame_row1, text=Settings.DB_PATH).pack(side=tk.LEFT)


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
        
        self.entry_from = None #抽出条件FROM
        self.entry_to = None #抽出条件TO
        self.week_flg = [] #抽出条件WEEK
        self.var_checked_comper = tk.BooleanVar() #比較分析の可否
        self.entry_from_pre = None #比較分析のFROM
        
        self.frame_row5 = tk.LabelFrame(self) #比較分析のコントロール制御用のフレーム
        self._setup_ui()        
        
    def _setup_ui(self):
        """Setup UI components"""
        self.pack(anchor=tk.NW, padx=10, pady=10)

        # 2-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        btn_GetInfo = tk.Button(frame_row1, text="売上情報入力", command=self._push_inoputData)
        btn_GetInfo.pack()
                
        # 2-2 日別売上抽出
        frame_row2 = tk.LabelFrame(self)
        frame_row2.pack(anchor=tk.W)
        frame_1 = tk.Frame(frame_row2)
        frame_1.pack(anchor=tk.W)            
        
        _from, _to = salesDataFrame.get_from_and_to()
        
        self.entry_from = DateEntry(frame_1, date_pattern=Settings.ENTRY_DISP_FORM)
        self.entry_from.bind("<<DateEntrySelected>>", self.on_date_selected)        
        self.entry_from.set_date(_from)
        
        self.entry_from.pack(side=tk.LEFT)
        tk.Label(frame_1, text="～").pack(side=tk.LEFT)
        #　集計終了日
        self.entry_to = DateEntry(frame_1, date_pattern=Settings.ENTRY_DISP_FORM)
        self.entry_to.pack(side=tk.LEFT)        
        self.entry_to.set_date(_to)
        # 2-2 日別売上抽出 曜日指定
        frame_2 = tk.Frame(frame_row2)
        frame_2.pack()
                
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
                
        #2-5　比較分析
        self.frame_row5.pack(anchor=tk.W)   
        tk.Checkbutton(self.frame_row5, text="比較", variable=self.var_checked_comper, command=self.comper_checked).pack(side=tk.LEFT)
        self.var_select_compar = tk.IntVar(value=0)
        tk.Radiobutton(self.frame_row5, text="前年", variable=self.var_select_compar, value=0, command=self.chang_coundkbn).pack(side=tk.LEFT)
        tk.Radiobutton(self.frame_row5, text="前月", variable=self.var_select_compar, value=1, command=self.chang_coundkbn).pack(side=tk.LEFT)
        tk.Radiobutton(self.frame_row5, text="前週", variable=self.var_select_compar, value=2, command=self.chang_coundkbn).pack(side=tk.LEFT)
        self.entry_from_pre = DateEntry(self.frame_row5, date_pattern=Settings.ENTRY_DISP_FORM)
        self.entry_from_pre.pack(side=tk.LEFT)        
        set_widget_status(self.frame_row5, tk.DISABLED, [tk.Radiobutton, DateEntry])
    
    def on_date_selected(self, _):
        self.chang_coundkbn() 
        
    def chang_coundkbn(self):
        """
        比較ボタンチェック中に、前年、前月、前週、日付の値を変更した際に処理

        Returns
        -------
        None.

        """
        _from, _ = self.get_cound_perid_datetime()
        
        
        if self.var_select_compar.get() == 0: #前年          
            _from_pre = _from - relativedelta(years=1)
            
        elif self.var_select_compar.get() == 1: #前月
            _from_pre = _from - relativedelta(months=1)
            
        elif self.var_select_compar.get() == 2: #前週
            _from_pre = _from - relativedelta(weeks=1)
            delta_days = (_from_pre.weekday() - 0) % 7
            _from_pre = _from_pre - timedelta(days=delta_days)
        
        self.entry_from_pre.set_date(_from_pre)  

     
    def comper_checked(self):
        """
        比較チェックボックス選択時の処理

        Returns
        -------
        None.

        """
        if self.var_checked_comper.get():
            set_widget_status(self.frame_row5, tk.NORMAL, [tk.Radiobutton, DateEntry])
            self.chang_coundkbn()
        else:
            set_widget_status(self.frame_row5, tk.DISABLED, [tk.Radiobutton, DateEntry])
            self.chang_coundkbn()
             
        
    def get_cound_perid_datetime(self):
        """
        抽出条件となる日、週、月のFORM・TOの日付をDatetime型で取得

        Returns
        -------
        _from : TYPE
            DESCRIPTION.
        _to : TYPE
            DESCRIPTION.

        """
                
        _from = dt.strptime(str(self.entry_from.get_date()), "%Y-%m-%d")
        _to = dt.strptime(str(self.entry_to.get_date()), "%Y-%m-%d")
        return _from, _to
    
    def get_cound_perid_datetime_pre(self):
        _from = dt.strptime(str(self.entry_from_pre.get_date()), "%Y-%m-%d")
        f, t = self.get_cound_perid_datetime() #期間取得 
        _to = _from + relativedelta(days=(t-f).days) 
        
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
            salesDataFrame.update_salesData(fle)
            msg.showinfo(msg.INFO,"売上情報の更新処理に成功しました")
            
            _from, _to = salesDataFrame.get_from_and_to()
            self.entry_from.set_date(_from)
            self.entry_to.set_date(_to)
                    
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
        
        #=======================================================================
        # df = salesDataFrame.get_currentData()
        # if df.empty:
        #     msg.showwarning(msg.WARNING, "読み込む売上情報の集計期間を選択してください")
        #     return "break"
        #=======================================================================
        
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
        
        self.select_brand_var = tk.StringVar() #取引先抽出条件
        self.var_checked_without = tk.BooleanVar() #特定区分を除くかの判断区分
        self.radio_jyoken = tk.IntVar(value=1) #ライン別、商品別で抽出するかの判断区分       
        self.select_line_var = tk.StringVar() #ライン別抽出条件
        
        self.frame_line = tk.LabelFrame(self) #ライン別のコントールを制御するフレーム
        self.frame_item = tk.LabelFrame(self) #商品別のコントールを制御するフレーム
        
        self.var_icode = tk.IntVar(value=0)#商品コードを入力する変数
        self.var_tname = tk.StringVar()#商品名を入力する変数
        
        self.var_foudlist = tk.StringVar()#リストに含まれている商品名を保持している変数
        self.lbox_findItems = None
        
        self._setup_ui()
        
        
    def _setup_ui(self):
        """Setup UI components"""
        self.pack(anchor=tk.NW, padx=10,pady=5)                           
        
        # 3-1
        frame_row1 = tk.LabelFrame(self)
        frame_row1.pack(anchor=tk.W)
        
        var_brand = salesDataFrame.df_brand["t_name"].unique().tolist()
        var_brand.insert(0,"全取引先")
        var_brand.append("その他取引先")
                
        cp_comb = ttk.Combobox(frame_row1, values=var_brand ,state="readonly", textvariable=self.select_brand_var)
        cp_comb.current(0)
        cp_comb.pack(side=tk.LEFT)
        
        tk.Checkbutton(frame_row1, text="和洋菓子課除外", variable=self.var_checked_without).pack(side=tk.LEFT)
                
        # 3-2
        self.frame_line.pack(anchor=tk.W)
        tk.Radiobutton(self.frame_line, text="ライン別", variable=self.radio_jyoken, value=Settings.SELECT_LINE, command=self.chang_coundkbn).pack(side=tk.LEFT)
        
        var_line = salesDataFrame.df_line["l_name"].tolist()
        var_line.insert(0,"全ライン")
        
        line_comb = ttk.Combobox(self.frame_line, values=var_line ,state="readonly", textvariable=self.select_line_var)
        line_comb.current(0)
        line_comb.pack(side=tk.LEFT)
        
        # 3-3
        self.frame_item.pack(anchor=tk.W)
        frame = tk.Frame(self.frame_item)
        frame.pack(anchor=tk.W)
        tk.Radiobutton(frame, text="商品別", variable=self.radio_jyoken, value=Settings.SELECT_ITEM, command=self.chang_coundkbn).pack(side=tk.LEFT)

        # 商品コードを入力するフォーム
        entry_icode = tk.Spinbox(frame, width=5, from_=0, to=9999, textvariable=self.var_icode)
        entry_icode.bind("<Return>", lambda event: self._setfindItems())
        entry_icode.pack(side=tk.LEFT) 
        
        
        # 商品名のキーワードを入力するフォーム
        entry_name = tk.Entry(frame, textvariable=self.var_tname)
        entry_name.bind("<Return>", lambda event: self._setfindItems(True))
        entry_name.pack(side=tk.LEFT)
                        
        #=======================================================================
        # self.frame_row4 = tk.LabelFrame(self.frame_item)
        # self.frame_row4.pack()
        #=======================================================================
        frame2 = tk.Frame(self.frame_item)
        frame2.pack(anchor=tk.W)         
        # キーワードで抽出された商品名を表示するリスト
        self.lbox_findItems = tk.Listbox(frame2, listvariable=self.var_foudlist, width=25, height=12, selectmode=tk.MULTIPLE)
        self.lbox_findItems.pack(side=tk.LEFT)
        self.lbox_findItems.bind("<Double-Button-1>", self._setfindItems)
        
        #　一部コントロールの無効化処理
        set_widget_status(self.frame_item, tk.DISABLED, [tk.Entry, tk.Spinbox, tk.Listbox])
        
        
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
        
        df = salesDataFrame.df
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
        if self.radio_jyoken.get() == Settings.SELECT_LINE:   
            set_widget_status(self.frame_line, tk.NORMAL, [ttk.Combobox])         
            set_widget_status(self.frame_item, tk.DISABLED, [tk.Entry, tk.Spinbox, tk.Listbox])  
            
            
        elif self.radio_jyoken.get() == Settings.SELECT_ITEM:
            set_widget_status(self.frame_line, tk.DISABLED, [ttk.Combobox])  
            set_widget_status(self.frame_item, tk.NORMAL, [tk.Entry, tk.Spinbox, tk.Listbox])  

                  
#===============================================================================
# class FrameOutput(tk.LabelFrame):
#            
#      
#     def _show_plotData(self, fig=None, df=pd.DataFrame):
#             """
#             フレームに分析データを表示する処理
#      
#             Returns
#             -------
#             None.
#      
#             """
#             for item in self.tree.get_children():
#                 self.tree.delete(item)            
#             #===================================================================
#             # for widget in self.labelFrame_out.winfo_children():  # フレーム内の全ウィジェットを削除
#             #     widget.destroy()
#             #===================================================================
#              
#                           
#             canvas = FigureCanvasTkAgg(fig, master=self.labelFrame_out)  # Tkinter フレームに埋め込む
#             canvas_widget = canvas.get_tk_widget()
#             canvas_widget.pack()
#      
#  
#     def _out_timeseries_chart(self, df_list, l_val): 
#         """
#         2024.07.31
#         「時系列分析」ボタン押下処理　、エクセルへ出力する処理
#      
#         Parameters
#         ----------
#         event : TYPE
#             DESCRIPTION.
#      
#         Returns
#         -------
#         str
#             DESCRIPTION.
#      
#         """       
#              
#         try:              
#                                                                                                             
#             use_col = self.var_radio_select_vals.get()  
#                    
#             fig, ax = plt.subplots(figsize=(8, 6)) 
#             x = []            
#             for key in df_list.keys():              
#                 df_out, _from, _to, _dff = df_list[key]
#                  
#                 # 時系列分析図出力処理-----
#                 df_out = df_out[["day",use_col]].groupby(["day"], as_index=False).sum(numeric_only=True)         
#                  
#                 if len(x)==0: # X軸をそろえる為
#                     x = df_out["day"]
#                      
#                 y = df_out[use_col]
#                  
#                 #比較分析時、X軸の件数が異なる場合エラーとなるで処理を中断
#                 if (len(x)-len(y)) != 0:
#                     msg.showerror(msg.ERROR,"比較対象となる期間が存在しない為、集計期間を短くてください")
#                     return "break"
#                   
#                  
#                 ax.plot(x, y,linewidth=0.5,label=f"{_from.strftime('%Y年%m月%d日')}～{_to.strftime('%Y年%m月%d日')}({_dff})")          
#                 #ax.xmargin = 5.0             
#                 # 移動平均算出用処理
#                 val = self.var_avgCount.get() 
#                 if val > 0:                    
#                     y = y.rolling(val).mean()  
#                     ax.plot(x, y, linewidth=0.5, marker='^', label=f"{key}:移動平均({val})")           
#                               
#             #ax.scatter(x, y)            
#             ax.set_title(f"時系列分析:{l_val}")
#             ax.set_xlabel("日付")
#             #ax.set_xlim(0,100) # X軸の幅指定　件数
#             #ax.set_ylim(0,100) # X軸の幅指定　件数     
#                            
#             #等間隔の数を設定する処理
#             step_idx = np.arange(0, len(x), step=np.ceil(len(x)/6)) #等間隔の数を決める
#             step_xval = x.loc[step_idx] #等間隔に沿った文字列データを取得
#             ax.set_xticks(step_idx,step_xval) #ラベルに設定する
#              
#             ax.minorticks_on() #補助目盛を追加
#              
#             ax.set_ylabel(USECOLS_NAME[use_col])
#             #　データラベルの追加
#             ax.legend()        
#             # グリッド線の追加
#             ax.grid(True)                             
#              
#             self._show_plotData(fig=fig)
#             salesDataFrame.pre_charts["timeseries"] = [x, y, l_val]
#  
#         except Exception: 
#             erMsg = "売上分析出力中にエラーが発生しました。"
#             msg.showerror(msg.ERROR,erMsg)
#             logging.exception(erMsg)  
#              
#      
#     def _out_histogram(self, df_list, l_val):
#         """
#         「ヒストグラム分析」ボタン押下処理　
#  
#         Returns
#         -------
#         str
#             DESCRIPTION.
#  
#         """
#          
#         use_col = self.var_radio_select_vals.get()
#         fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
#          
#         for key in df_list.keys():
#             df_out, _from, _to, _dff = df_list[key]
#              
#             temp = df_out.groupby(["day"]).mean(numeric_only=True)
#             ax.hist(temp[use_col], bins=30, alpha=0.5, label=f"{_from.strftime('%Y年%m月%d日')}:{_to.strftime('%Y年%m月%d日')}({_dff})")
#              
#          
#         #不要処理
#         #=======================================================================
#         # # 移動平均算出用処理
#         # val = self.var_avgCount.get() 
#         # if val > 0:     
#         #     temp["temp2"] = temp[use_col].rolling(val).mean()              
#         #     ax.hist(temp["temp2"], bins=30, alpha=0.5, label=f"移動平均({val})")
#         #=======================================================================
#              
#         # タイトル
#         ax.set_title(f'ヒストグラム分析:({l_val})')
#          
#         # x軸とy軸にラベルの追加
#         ax.set_xlabel(USECOLS_NAME[use_col])
#         ax.set_ylabel('Frequency')
#          
#         #　データラベルの追加
#         ax.legend()        
#         # グリッド線の追加
#         ax.grid(True)
#      
#         self._show_plotData(fig=fig)        
#         salesDataFrame.pre_charts["histogram"] = [temp[use_col], l_val]
#          
#              
#     def _out_scatterplot(self, df_list, l_val):
#         """
#          
#         「回帰分析」ボタン押下処理　
#         Returns
#         -------
#         str
#             DESCRIPTION.
#  
#         """        
#                
#         use_col = self.var_radio_select_vals.get()
#         fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
#          
#         for key in df_list.keys():
#              
#             df_out, _from, _to, _dff = df_list[key]
#                
#             temp = df_out[["day","count","amount"]].groupby(["day"]).mean(numeric_only=True) 
#              
#             # 平均単価算出
#             temp["avg"] = temp["amount"]/temp["count"]        
#          
#             x = temp["avg"]
#             y = temp[use_col]
#                  
#             ax.scatter(x, y, alpha=0.5, label=f"{_from.strftime('%Y年%m月%d日')}:{_to.strftime('%Y年%m月%d日')}({_dff})")
#          
#         # 不要？？
#         # 移動平均算出用処理
#         #=======================================================================
#         # val = self.var_avgCount.get()
#         # if val > 0:     
#         #     y = y.rolling(val).mean()              
#         #     ax.scatter(x, y, label=f"移動平均({val})")
#         #=======================================================================
#          
#         ax.set_title(f"回帰分析：{l_val}")
#         ax.set_xlabel(USECOLS_NAME["avg"])
#         ax.set_ylabel(USECOLS_NAME[use_col])
#         #　データラベルの追加
#         ax.legend()        
#         # グリッド線の追加
#         ax.grid(True)
#                  
#         self._show_plotData(fig=fig)
#         salesDataFrame.pre_charts["scatterplot"] = [x,y,l_val]        
#===============================================================================

class treeview(ttk.Treeview):
    
    try:
        def __init__(self, master, df):       
            
            self.df_out = df #TreeView表示用DB 並び替えでも使用         
                        
            self.frame_treeview = tk.Frame(master) #TreeViewガジェット制御用フレーム
            self.frame_treeview.pack(fill="both", expand=True)
            
            tree_scroll_y = tk.Scrollbar(self.frame_treeview, orient=tk.VERTICAL)
            tree_scroll_x = tk.Scrollbar(self.frame_treeview, orient=tk.HORIZONTAL)
            
            use_columns = list(self.df_out.columns)   
            # 🟢 Treeview のカラム設定
            super().__init__(self.frame_treeview, columns=use_columns, show="headings", height=20, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
                        
            for col in use_columns:
                self.heading(col, text=col, command=lambda c=col: self.sort_by_column(c), anchor="center")
                self.column(col, width=max(self.df_out[col].astype(str).map(len).max() * 10, 100), anchor="center") 
            
            
            self.sort_state = {col: False for col in use_columns} # 降順昇順を管理
            tree_scroll_y.config(command=self.yview)
            tree_scroll_x.config(command=self.xview) 
            
            # 🟢 データを Treeview に追加
            self.update_data(self.df_out)
            
            # 🟢 配置
            tree_scroll_y.pack(side="right", fill="y")
            tree_scroll_x.pack(side="bottom", fill="x")
            self.pack(expand=True, fill="both")     
                       
    
        def update_data(self, df: pd.DataFrame):
                        
            """Treeview に `DataFrame` のデータを設定"""
            self.delete(*self.get_children())  # 既存データ削除
            for _, row in df.iterrows():
                formatted_row = []
                for col in df.columns:
                    value = row[col]
            
                    # データ型ごとの表示フォーマット
                    if pd.api.types.is_integer_dtype(df[col]):
                        formatted_value = f"{value:,}"  # 整数はカンマ区切り
                    elif pd.api.types.is_float_dtype(df[col]):
                        formatted_value = f"{value:,.1%}"  # 小数はカンマ区切り＆2桁
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        formatted_value = value.strftime("%Y年%m月%d日") if pd.notna(value) else ""  # 日付フォーマット
                    else:
                        formatted_value = value  # それ以外はそのまま
                        
                    formatted_row.append(formatted_value)
                
                self.insert("", "end", values=formatted_row)  
    
        def sort_by_column(self, col):
            """ヘッダークリックでソート"""
            reverse = self.sort_state[col] = not self.sort_state[col]
            df = self.df_out.sort_values(by=col, ascending=reverse)
            self.update_data(df)  # データ更新
                
        
        def on_select(self,event):        
            #TODO：テスト実装
            msg.showinfo("title", "message")    
        
    except Exception: 
        erMsg = "treeviewの初期化中にエラーが発生しました。"
        msg.showerror(msg.ERROR, erMsg)
        logging.exception(erMsg)  
                
                
    
class MyApp(tk.Tk):
        
    def _setup_ui(self):
        """Setup UI components"""         
        
        # right side frame output data
        frame_main2 = tk.Frame(self)
        frame_main2.pack(anchor=tk.NW, side=tk.LEFT,  padx=10, pady=10)
        
        label_f = tk.LabelFrame(frame_main2,text="集計処理")
        label_f.pack(anchor=tk.NW, padx=10,pady=10)
                     
        frame_row0 = tk.LabelFrame(label_f)
        frame_row0.pack(anchor=tk.W)  
        tk.Radiobutton(frame_row0, text="売上金額", variable=self.var_radio_select_vals, value="amount").pack(side=tk.LEFT)
        tk.Radiobutton(frame_row0, text="売上数量", variable=self.var_radio_select_vals, value="count").pack(side=tk.LEFT)
        tk.Button(frame_row0, text="CSVデータ出力", bg="white", command=lambda:self._push_buttons(0)).pack(side=tk.LEFT)
                        
        frame_row1 = tk.LabelFrame(label_f)
        frame_row1.pack(anchor=tk.W)
        tk.Button(frame_row1, text="集計表出力", command=lambda:self._push_buttons(1)).pack(side=tk.LEFT)
        tk.Button(frame_row1, text="時系列分析", command=lambda:self._push_buttons(2)).pack(side=tk.LEFT)       
        tk.Button(frame_row1, text="ヒストグラム分析", command=lambda:self._push_buttons(3)).pack(side=tk.LEFT)               
        tk.Button(frame_row1, text="散布図分析", command=lambda:self._push_buttons(4)).pack(side=tk.LEFT)  
         
        frame_avg = tk.Frame(frame_row1)
        frame_avg.pack(side=tk.LEFT, padx=10)
        tk.Label(frame_avg, text="移動平均集計").pack(side=tk.LEFT)
        tk.Spinbox(frame_avg, width=5, from_=0, to=100, textvariable=self.var_avgCount).pack(side=tk.LEFT) 
        self.labelFrame_out = tk.LabelFrame(label_f, text="分析結果", width=500, height=400)
        self.labelFrame_out.pack_propagate(False) 
        self.labelFrame_out.pack(anchor=tk.NW)
            
            
    def _push_buttons(self, out_typ):
        #商品名抽出        
        _brand = self.frameCound.select_brand_var.get()
        _line = self.frameCound.select_line_var.get()
        _items = self.frameCound.get_selectitems()
        _from, _to = self.framePeriod.get_cound_perid_datetime()
        _weeks = self.framePeriod.get_select_dayofweeks()
        _without = self.frameCound.var_checked_without.get()
                   
        group_key = ["t_name","l_name","i_name","day_DateTime"]     
                             
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
         
     
        df_out = df_out.groupby(group_key, as_index=False).sum(numeric_only=True).loc[:,group_key+["amount","count"]]
        df_out = df_out.rename(columns={'amount': 'base_amount', 'count': 'base_count'})                 
 
         
        _from2, _to2 = self.framePeriod.get_cound_perid_datetime_pre()
        df_out2 = salesDataFrame.get_datacondition(None if _brand == "全取引先" else _brand,
                                                   None if _line == "全ライン" else _line,
                                                    _items,
                                                     _from2,
                                                      _to2,
                                                       _weeks,
                                                       _without)           
        
        if self.framePeriod.var_checked_comper.get():
            dif_day_pre = (_from-_from2).days #　ベースとなる売上情報にマッチする為に日付を加算
            df_out2["day_DateTime"] = df_out2["day_DateTime"] + pd.Timedelta(days=dif_day_pre)  
        else:
            df_out2 = df_out2.iloc[0:0]

                 
        df_out2 = df_out2.groupby(group_key, as_index=False).sum(numeric_only=True).loc[:,group_key+["amount","count"]]
        df_out2 = df_out2.rename(columns={'amount': 'past_amount', 'count': 'past_count'})
        
        # df_out と df_out2 を共通キーで結合
        df_out3 = pd.merge(df_out, df_out2, on=group_key, how="outer")  # 外部結合（全データを残す）        
        # 必要なら、NaNを0に置き換え
        df_out3 = df_out3.fillna(0)
        
        #df_out3 = pd.merge(df_out, df_out2, on=group_key, how="left").fillna(0)
        df_out3["amount_par"] = df_out3["base_amount"]/df_out3["past_amount"]
        df_out3["count_par"] = df_out3["base_count"]/df_out3["past_count"] 
        
        df_out3 = df_out3.astype({col: dtype for col, dtype in Settings.DIC_AS_TYPES.items() if col in df_out3.columns} )
        df_out3 = df_out3.fillna(0)
        
        
        
        key = ""
        key_plot = "day_DateTime"
        if self.frameCound.radio_jyoken.get()==Settings.SELECT_ITEM:#商品名で抽出する条件
            l_val = "{}_{}".format(_brand, ",".join(_items))
            
            key = "i_name"
            
        else:#ライン名で抽出する条件
            l_val = "{}_{}".format(_brand, _line)
            
            if (self.frameCound.select_brand_var.get() == "全取引先" and self.frameCound.select_line_var.get() == "全ライン"):
                key = "t_name"#全取引先ごとに集計
                
            elif (self.frameCound.select_brand_var.get() != "全取引先" and self.frameCound.select_line_var.get() == "全ライン"):
                key = "l_name"#取引先単位でライン別
                
            else: 
                key = "i_name"
            
        
        base_val = f"base_{self.var_radio_select_vals.get()}"
        past_val = f"past_{self.var_radio_select_vals.get()}"
                      
        
        df_tree = df_out3.groupby(key, as_index=False).sum(numeric_only=True).loc[:,[key,base_val,past_val]]
        df_tree["比率"] = df_tree[base_val] / df_tree[past_val] #比較比率を算出
        
        df_out_plot = df_out3.groupby(key_plot, as_index=False).sum(numeric_only=True).loc[:,[key_plot,base_val,past_val]]           
            

        self._out_compar_ana(df_out3)
        if out_typ == 0:
            self._out_compar_ana(df_out3, True)
         
        elif out_typ == 1:
            self._out_compar_ana(df_out3)
              
        elif out_typ == 2:
            self._out_timeseries_chart(df_out_plot, l_val)
              
        #=======================================================================
        # elif out_typ == 3: 
        #     self._out_histogram(df_list, l_val)
        #       
        # elif out_typ == 4: 
        #     self._out_scatterplot(df_list, l_val)
        #=======================================================================
        
    def _out_compar_ana(self, df, csv_flg=False):
        """
        売上比較分析処理
 
        Returns
        -------
        str
            DESCRIPTION.
 
        """
         
        try:                        
            key =[]
            use_columns =[]
            
            # 商品名抽出       
            if self.frameCound.radio_jyoken.get()==Settings.SELECT_ITEM:  
                key = "i_name"
                
                #l_val = "{}_{}".format(_brand, ",".join(_items))
            else:                
                if (self.frameCound.select_brand_var.get() == "全取引先" and self.frameCound.select_line_var.get() == "全ライン"):
                    key = "t_name"
                    
                elif (self.frameCound.select_brand_var.get() != "全取引先" and self.frameCound.select_line_var.get() == "全ライン"):
                    key = "l_name"
                    
                else: 
                    key = "i_name"
                    
                    
                #l_val = "{}_{}".format(_brand, _line)

            if self.var_radio_select_vals.get() == "amount":#出力項目選択　金額
                use_columns = [f"{key}","base_amount","past_amount"]            
                df_out = df.groupby(key, as_index=False).sum(numeric_only=True)[use_columns]
                df_out["比率"] = df_out["base_amount"] / df_out["past_amount"] #比較比率を産出
                
            else:#出力項目選択　数量
                use_columns = [f"{key}","base_count","past_count"]            
                df_out = df.groupby(key, as_index=False).sum(numeric_only=True)[use_columns]
                df_out["比率"] = df_out["base_count"] / df_out["past_count"] #比較比率を産出
            
            if self.tree:
                self.tree.frame_treeview.destroy() 
                #self.tree.destroy()             
            
            self.tree = treeview(self.labelFrame_out, df_out) 
            
            _from, _to = self.framePeriod.get_cound_perid_datetime()
            _from2, _to2 = self.framePeriod.get_cound_perid_datetime_pre()
         
            diff = (_to-_from).days
            diff2 = (_to2-_from2).days
                                      
            if csv_flg:
                sheetName=f"{self.cls_cound.select_brand_var.get()}:{self.cls_cound.select_line_var.get()}"
                head_str = f"実績期間：{_from.strftime('%Y年%m月%d日')}～{_to.strftime('%Y年%m月%d日')}({diff})　比較期間{_from2.strftime('%Y年%m月%d日')}～{_to2.strftime('%Y年%m月%d日')}({diff2})　"
                self._out_excel(df, sheetName, sheetName, head_str)                
                
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
 
 
    def _out_timeseries_chart(self, df, l_val): 
        """
        時系列分析チャートを表示する処理

        Parameters
        ----------
        df : pandas.DataFrame
            プロットするデータフレーム
        l_val : str
            チャートのタイトルに使用するラベル

        Returns
        -------
        None
        """
        try:
            # 別画面が存在する場合は削除
            if hasattr(self, "chart_window") and self.chart_window.winfo_exists():
                self.chart_window.destroy()

            # 別画面を作成
            self.chart_window = tk.Toplevel(self)
            self.chart_window.title("時系列分析チャート")
            self.chart_window.geometry("800x600")

            # プロットの準備
            fig, ax = plt.subplots(figsize=(8, 6))
            x = df["day_DateTime"]
            y = df["base_amount"]

            # 元データのプロット
            ax.plot(x, y, linewidth=0.5, label="元データ")

            # 移動平均のプロット
            val = self.var_avgCount.get()
            if val > 0:
                y_avg = y.rolling(val).mean()
                ax.plot(x, y_avg, linewidth=0.5, marker='^', label=f"移動平均({val})")

            # Y軸のフォーマットを設定（千円単位、カンマ区切り）
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

            # チャートの設定
            ax.set_title(f"時系列分析: {l_val}")
            ax.set_xlabel("日付")
            ax.set_ylabel("売上金額")
            ax.legend()
            ax.grid(True)

            # プロットをTkinterウィジェットに埋め込む
            canvas = FigureCanvasTkAgg(fig, master=self.chart_window)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            erMsg = "時系列分析チャートの表示中にエラーが発生しました。"
            msg.showerror("エラー", f"{erMsg}\n{e}")
            logging.exception(erMsg)        




        # try:                                                                                                         
            
            
        #     use_col = self.var_radio_select_vals.get()  
                   
        #     fig, ax = plt.subplots(figsize=(8, 6))                
            
        #     _from, _to = self.framePeriod.get_cound_perid_datetime()
        #     _diff = (_to-_from).days
            
        #     x = df["day_DateTime"]
        #     y = df["base_amount"]
            
        #     ax.plot(x, y,linewidth=0.5,label=f"{_from.strftime('%Y年%m月%d日')}～{_to.strftime('%Y年%m月%d日')}({_diff})") 

        #     key = self.frameCound.select_brand_var.get()

        #     #ax.xmargin = 5.0             
        #     # 移動平均算出用処理
        #     val = self.var_avgCount.get() 
        #     if val > 0:                    
        #         y = y.rolling(val).mean()  
        #         ax.plot(x, y, linewidth=0.5, marker='^', label=f"{key}:移動平均({val})")           
                              
        #     #ax.scatter(x, y)            
        #     ax.set_title(f"時系列分析:{l_val}")
        #     ax.set_xlabel("日付")
        #     #ax.set_xlim(0,100) # X軸の幅指定　件数
        #     #ax.set_ylim(0,100) # X軸の幅指定　件数     
                           
        #     #等間隔の数を設定する処理
        #     step_idx = np.arange(0, len(x), step=np.ceil(len(x)/6)) #等間隔の数を決める
        #     step_xval = x.loc[step_idx] #等間隔に沿った文字列データを取得
        #     ax.set_xticks(step_idx,step_xval) #ラベルに設定する
             
        #     ax.minorticks_on() #補助目盛を追加
            
        #     ax.set_ylabel(use_col)
        #     #　データラベルの追加
        #     ax.legend()        
        #     # グリッド線の追加
        #     ax.grid(True)                             
            
        #     new_root = tk.Tk()

        #     canvas = FigureCanvasTkAgg(fig, master=new_root)  # Tkinter フレームに埋め込む
        #     canvas_widget = canvas.get_tk_widget()
        #     canvas_widget.pack()
        #     #salesDataFrame.pre_charts["timeseries"] = [x, y, l_val] 

  
        # except Exception: 
        #     erMsg = "売上分析出力中にエラーが発生しました。"
        #     msg.showerror(msg.ERROR,erMsg)
        #     logging.exception(erMsg)  
    

    def __init__(self):
        """
        システムのメイン処理

        Returns
        -------
        None.
        """
        super().__init__()
        
        self.frameInput = None
        self.framePeriod = None        
        self.frameCound = None  
        self.var_radio_select_vals = tk.StringVar(value="amount") 
        self.var_avgCount = tk.IntVar(value=0)
        self.labelFrame_out = None  
        
        self.tree = None
        
        self.title("売上分析システム")
        self.geometry("1000x600")  
        
        # left side frame input data      
        frame_main1 = tk.Frame(self)
        frame_main1.pack(anchor=tk.NW, side=tk.LEFT,padx=10, pady=10)
        self.frameInput = FrameInput(frame_main1)
        self.framePeriod = FramePeriod(frame_main1)        
        self.frameCound = FrameCound(frame_main1)  
        
        self._setup_ui() 
                
        #self.frame5 = FrameOutput(frame_main2, self.frame3, self.frame4)   
         
        
salesDataFrame = analysis_data.Analysis_data()
app = MyApp()
app.mainloop()




