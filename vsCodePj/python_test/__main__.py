# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:49:19 2025

@author: mkt05
"""

try:
    import os
    import tkinter as tk
    from tkinter import ttk
    import logging
    import pandas as pd
    import openpyxl as op
    from py_pk.settings import Settings
    from py_pk import analysis_data    
    from datetime import timedelta, datetime as dt
    from dateutil.relativedelta import relativedelta  
    from tkcalendar import DateEntry
    from tkinter import filedialog, messagebox as msg
    import threading
    #import calendar
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.ticker import FuncFormatter
    from adjustText import adjust_text
    from dotenv import load_dotenv

except Exception:               
    logging.exception(Exception)
    msg.showerror(msg.ERROR, "モジュールのインポートに失敗しました")
    raise  

# ログの設定
logging.basicConfig(
    filename='logfile/debug.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # エンコーディングを指定
)

USECOLS_NAME = {"amount":"売上金額","avg":"平均単価","":""}
plt.rcParams["font.family"] = "meiryo"


def set_widget_status(wg_frame, state, l):
    try:
        """
        フレーム内のウィジェットの状態を設定する

        Parameters
        ----------
        wg_frame : TYPE
            フレーム名
        state : TYPE
            ウィジェットの状態（tk.NORMAL, tk.DISABLED）
        l : TYPE
            対象ウィジェットのリスト

        Returns
        -------
        None.

        """
        for widget in wg_frame.winfo_children():  
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                set_widget_status(widget, state, l)           
            
            for target_wg in l:
                if isinstance(widget, target_wg):
                    widget.config(state=state)
                    break  
    except Exception:               
        logging.exception(Exception)
        raise  
 
      
class FrameInput(tk.LabelFrame):
    """
    .データベースパスの表示
    """    
    try:
        def __init__(self, master):
            super().__init__(master, text="データベースパス", bd=2)
            self._setup_ui()
        
        def _setup_ui(self):
            """Setup UI components"""
            self.pack(padx=10, pady=10,anchor=tk.NW)

            """Create frame for database information"""   
            
            # .env読み込み
            load_dotenv()
            db_path = os.getenv("DB_PATH")     
            tk.Label(self, text=db_path).pack()
    except Exception:               
        logging.exception(Exception)
        raise  


class FramePeriod(tk.LabelFrame):
    def __init__(self, master):
        """
        集計期間を入力するフォーム
        1.売上情報を更新するボタン
        2.売上情報を抽出する期間の設定
        3.日別、週別、月別による集計
        4.曜日選択-＞日別による集計のみ

        Parameters
        ----------
        master : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        try:
            super().__init__(master, text="集計期間：", bd=2)
            
            self.entry_from = None #抽出条件FROM
            self.entry_to = None #抽出条件TO
            self.week_flg = [] #抽出条件WEEK
            self.var_checked_comper = tk.BooleanVar() #比較分析の可否
            self.entry_from_pre = None #比較分析のFROM
            
            self.frame_row5 = tk.LabelFrame(self) #比較分析のコントロール制御用のフレーム
            self._setup_ui()  
                
        except Exception:               
            logging.exception(Exception)
            raise
        
    def _setup_ui(self):        
        """
            Setup UI components

            Returns
            -------
            None.

            """
        """Setup UI components"""
        try:
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
        except Exception:               
            logging.exception(Exception)
            raise  
    
    def on_date_selected(self, _):
        self.chang_coundkbn() 
        
    def chang_coundkbn(self):
        """
        比較ボタンチェック中に、前年、前月、前週、日付の値を変更した際に処理

        Returns
        -------
        None.

        """
        try:
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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
     
    def comper_checked(self):
        """
        比較チェックボックス選択時の処理

        Returns
        -------
        None.

        """
        try:
            if self.var_checked_comper.get():
                set_widget_status(self.frame_row5, tk.NORMAL, [tk.Radiobutton, DateEntry])
                self.chang_coundkbn()
            else:
                set_widget_status(self.frame_row5, tk.DISABLED, [tk.Radiobutton, DateEntry])
                self.chang_coundkbn()
        except Exception:
            logging.exception(Exception)
            raise
             
        
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
        try:
            _from = dt.strptime(str(self.entry_from.get_date()), "%Y-%m-%d")
            _to = dt.strptime(str(self.entry_to.get_date()), "%Y-%m-%d")
            return _from, _to
        
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise

    def get_cound_perid_datetime_pre(self):
        """
        比較分析のFROM、TOの日付を取得
        """
        try:
            _from = dt.strptime(str(self.entry_from_pre.get_date()), "%Y-%m-%d")
            f, t = self.get_cound_perid_datetime() #期間取得 
            _to = _from + relativedelta(days=(t-f).days) 
        
            return _from, _to
        
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
        
    def get_select_dayofweeks(self):
        """
        日別の売上集計期間が選択されている場合、選択されている曜日を返す処理

        Returns
        -------
        targetWeek : TYPE
            DESCRIPTION.

        """
        try:
            targetWeek = []
            # 日別の集計期間が選択されていれば曜日指定の配列を返す
            for i in range(0,7):
                if self.week_flg[i].get():
                    targetWeek.append(i)  
                
            return targetWeek
        
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
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
            logging.exception("エラーが発生しました")
        finally:
            # スレッド処理終了
            app.after(0, loading_window.destroy)
            raise
        
    def _push_inoputData(self):
        """
        [売上情報入力]ボタン押下時の処理

        Returns
        -------
        None.

        """
        
        """処理中のダイアログを表示"""
        try:       
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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise                 
        

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
        try:
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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
        
    def _setup_ui(self):
        """Setup UI components"""
        try:
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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
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
        
        try:
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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
    
    def get_selectitems(self):
        """
        一覧表示されている商品リストから選択された商品名を返す

        Returns
        -------
        select_Items : TYPE
            DESCRIPTION.

        """
        try:
            select_Items = []
            
            if self.lbox_findItems["state"] == tk.DISABLED:
                return select_Items
            
            select_index = self.lbox_findItems.curselection()
            if len(select_index) > 0:
                for index in select_index:
                    select_Items.append(self.lbox_findItems.get(index))            

            return select_Items
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
         
    def chang_coundkbn(self):
        """
        抽出条件ボタン選択時の処理
    
        Returns
        -------
        None.
    
        """
        try:
            if self.radio_jyoken.get() == Settings.SELECT_LINE:   
                set_widget_status(self.frame_line, tk.NORMAL, [ttk.Combobox])         
                set_widget_status(self.frame_item, tk.DISABLED, [tk.Entry, tk.Spinbox, tk.Listbox])  
                
                
            elif self.radio_jyoken.get() == Settings.SELECT_ITEM:
                set_widget_status(self.frame_line, tk.DISABLED, [ttk.Combobox])  
                set_widget_status(self.frame_item, tk.NORMAL, [tk.Entry, tk.Spinbox, tk.Listbox])  
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise


class treeview(ttk.Treeview):
    
    
    def __init__(self, master, df):       
        try:
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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
                       
    
    def update_data(self, df: pd.DataFrame):
        """
        DataFrame のデータを Treeview に設定する                        
        """
        try:

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
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
    def sort_by_column(self, col):
        """ヘッダークリックでソート"""
        reverse = self.sort_state[col] = not self.sort_state[col]
        df = self.df_out.sort_values(by=col, ascending=reverse)
        self.update_data(df)  # データ更新

        
    def on_select(self,event):        
        #TODO：テスト実装
        msg.showinfo("title", "message")    
                    
                
    
class MyApp(tk.Tk):
        
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
        self.var_avgCount = tk.IntVar(value=7) # 移動平均集計日数
        self.labelFrame_out = None  ## TreeView表示用フレーム
        self.labelFrame_out2 = None  ## チャート表示用フレーム
        self.tree = None

        self.var_chk_outcsv = tk.BooleanVar() # CSV出力チェックボックス
        
        self.title("売上分析システム")
        self.geometry("1500x600")  
        
        self._setup_ui() 
                

    def _setup_ui(self):
        try:
            """Setup UI components"""         
            # left side frame input data      
            frame_main1 = tk.LabelFrame(self, text="抽出条件入力", height=500)
            frame_main1.pack(anchor=tk.NW, side=tk.LEFT,padx=10, pady=10)

            self.frameInput = FrameInput(frame_main1)
            self.framePeriod = FramePeriod(frame_main1)        
            self.frameCound = FrameCound(frame_main1)  

            # midoll frame output data
            frame_main2 = tk.LabelFrame(self, text="集計処理", height=500)
            frame_main2.pack(anchor=tk.NW, side=tk.LEFT,padx=10, pady=10)
                        
            f_group1 = tk.Frame(frame_main2)
            f_group1.pack(anchor=tk.W)  
            tk.Radiobutton(f_group1, text="売上金額", variable=self.var_radio_select_vals, value="amount").pack(side=tk.LEFT)
            
            f_group2 = tk.Frame(frame_main2)
            f_group2.pack(anchor=tk.W)  

            #tk.Button(frame_row0, text="集計表出力", command=lambda:self._push_buttons(1)).pack(side=tk.LEFT)
            tk.Button(f_group2, text="時系列分析", command=lambda:self._push_buttons(1)).pack(side=tk.LEFT)       
            # tk.Button(f_group2, text="ヒストグラム分析", command=lambda:self._push_buttons(2)).pack(side=tk.LEFT)               
            tk.Button(f_group2, text="構成比グラフ", command=lambda:self._push_buttons(3)).pack(side=tk.LEFT)               
            tk.Checkbutton(f_group2, text="CSVデータ出力", variable=self.var_chk_outcsv).pack(side=tk.LEFT)    

            tk.Label(f_group2, text="移動平均集計").pack(side=tk.LEFT)
            tk.Spinbox(f_group2, width=5, from_=0, to=100, textvariable=self.var_avgCount).pack(side=tk.LEFT) 
            
            self.labelFrame_out = tk.LabelFrame(frame_main2, text="分析結果", width=500, height=450) ## TreeView表示用フレーム                
            self.labelFrame_out.pack_propagate(False) 
            self.labelFrame_out.pack(anchor=tk.NW)



            # right side frame output data
            frame_main3 = tk.LabelFrame(self, text="チャート")
            frame_main3.pack(anchor=tk.NW, side=tk.LEFT, padx=10, pady=10)

            self.labelFrame_out2 = tk.Frame(frame_main3,width=500, height=500) ## TreeView表示用フレーム                
            self.labelFrame_out2.pack_propagate(False) 
            self.labelFrame_out2.pack(anchor=tk.NW)
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise

    def _push_buttons(self, out_typ):
        try:
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
            
        
            df_out = df_out.groupby(group_key, as_index=False).sum(numeric_only=True).loc[:,group_key+["amount"]]
            df_out = df_out.rename(columns={'amount': 'base_amount'})                 
    
            
            _from2, _to2 = self.framePeriod.get_cound_perid_datetime_pre() #比較期間の取得
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

                    
            df_out2 = df_out2.groupby(group_key, as_index=False).sum(numeric_only=True).loc[:,group_key+["amount"]]
            df_out2 = df_out2.rename(columns={'amount': 'past_amount'})
            
            # df_out と df_out2 を共通キーで結合
            df_out3 = pd.merge(df_out, df_out2, on=group_key, how="outer")  # 外部結合（全データを残す）        
            # 必要なら、NaNを0に置き換え
            df_out3 = df_out3.fillna(0)
            
            #df_out3 = pd.merge(df_out, df_out2, on=group_key, how="left").fillna(0)
            df_out3["amount_par"] = df_out3["base_amount"]/df_out3["past_amount"]
            
            df_out3 = df_out3.astype({col: dtype for col, dtype in Settings.DIC_AS_TYPES.items() if col in df_out3.columns} )
            df_out3 = df_out3.fillna(0)
            
            
            
            key = ""
            key_time = "day_DateTime"
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
                
            # 選択された出力項目に基づいて列名を決定
            # 出力項目選択　金額
            base_val = f"base_{self.var_radio_select_vals.get()}"
            past_val = f"past_{self.var_radio_select_vals.get()}"
                        
            
            # keyでグループ化し、合計を計算
            df_key = df_out3.groupby(key, as_index=False).sum(numeric_only=True).loc[:,[key,base_val,past_val]]
            df_key["%percent"] = df_key[base_val] / df_key[past_val] #比較比率を算出
            df_key = df_key.sort_values(by=base_val, ascending=False) # 比率でソート
            
            # day_DateTimeでグループ化し、合計を計算
            df_time = df_out3.groupby(key_time, as_index=False).sum(numeric_only=True).loc[:,[key_time,base_val,past_val]]              

            #self._out_compar_ana(df_tree) # TreeViewにデータを表示する
            if self.var_chk_outcsv.get(): #CSV出力処理のボタン押下        
                diff = (_to - _from).days
                diff2 = (_to2 - _from2).days
                head_str = f"実績期間：{_from.strftime('%Y年%m月%d日')}～{_to.strftime('%Y年%m月%d日')}({diff})　比較期間{_from2.strftime('%Y年%m月%d日')}～{_to2.strftime('%Y年%m月%d日')}({diff2})　"

                self._out_compar_ana(df_key, l_val, l_val, head_str)  
            else:
                self._out_compar_ana(df_key)  
                

            # チャート分析を表示する処理
            if out_typ == 1:
                self._out_timeseries_chart(df_time, key_time, base_val, past_val, l_val) # 時系列分析表示する処理
                
            elif out_typ == 2: 
                self._out_histogram(df_time, base_val, past_val, l_val) # ヒストグラム分析表示する処理

            elif out_typ == 3: 
                self._out_pie(df_key, key, base_val, past_val, l_val)

            # elif out_typ == 4: 
            #     self._out_scatterplot(df_list, l_val)
            #=======================================================================
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise
        
        
    def _out_compar_ana(self, df, book_name="", sheetName="", head_str="") -> pd.DataFrame:
        """
        売上比較分析処理
 
        Returns
        -------
        str
            DESCRIPTION.
 
        """
         
        try:                                    
            if self.tree:
                self.tree.frame_treeview.destroy()             
            
            self.tree = treeview(self.labelFrame_out, df)     
            
            if not book_name == "":
                # CSVファイル出力処理
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
                        df.to_excel(writer, startrow=1, na_rep=0 ,sheet_name=sheetName, index=False) #index=Falseでインデックスを出力しない
                        # workbook = writer.book
                        worksheet = writer.sheets[sheetName]
                        # カンマ区切り（千単位）、パーセント、整数のフォーマット設定
                        excel_col = ["B","C","D"]
                        col_fm = ["#,##0", "#,##0", "0.0%"]
                        worksheet["A1"] = head_str
                        
                        for col, format_code in zip(excel_col, col_fm): 
                            for cell in worksheet[col]:                            
                                cell.number_format = format_code
                        
                    msg.showinfo(msg.INFO, "処理を正常に終了しました。")
                else:
                    msg.showwarning(msg.INFO, "処理を中断しました。")

        except Exception: 
            erMsg = "売上分析出力中にエラーが発生しました。"
            msg.showerror(msg.ERROR,erMsg)
            logging.exception(erMsg)  
 
 
    def _out_timeseries_chart(self, df, key, col1, col2, l_val): 
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
            # 既存のチャートを削除
            for widget in self.labelFrame_out2.winfo_children():
                widget.destroy()

            # プロットの準備
            fig, ax = plt.subplots(figsize=(6, 4))
            x = df[key]
            y1 = df[col1]
            y2 = df[col2]

            y_max = max(y1.max(), y2.max())  # Y軸の最大値を設定
            y_min = min(y1.min(), y2.min())  # Y軸の最小値を設定

            # 元データのプロット
            ax.plot(x, y1, linewidth=0.5, label="Base")
            ax.plot(x, y2, linewidth=0.5, label="Compare") 

            # 移動平均のプロット
            val = self.var_avgCount.get()
            if val > 0:
                y_avg = y1.rolling(val).mean()
                y2_avg = y2.rolling(val).mean()
                ax.plot(x, y_avg, linewidth=0.5, marker='^', label=f"Base({val})")
                ax.plot(x, y2_avg, linewidth=0.5, marker='^', label=f"Compare({val})")

            # X軸のラベルを自動調整
            num_labels = len(x)
            if num_labels > 20:
                font_size = 8  # データが多い場合は小さく
            elif num_labels > 10:
                font_size = 10  # 中程度の場合
            else:
                font_size = 12  # データが少ない場合は大きく

            ax.set_xticks(x[::max(1, len(x) // 10)])  # データ数に応じて間隔を調整
            ax.tick_params(axis='x', rotation=45, labelsize=font_size)  # ラベルを45度回転し、フォントサイズを調整

            # Y軸のラベルを自動調整
            num_labels_y = max(len(y1),len(y2))
            if num_labels_y > 20:
                font_size_y = 8  # データが多い場合は小さく
            elif num_labels_y > 10:
                font_size_y = 10  # 中程度の場合
            else:
                font_size_y = 12  # データが少ない場合は大きく

            ax.tick_params(axis='y', labelsize=font_size_y)  # Y軸ラベルのフォントサイズを調整

            # Y軸の最大値と最小値を設定
            ax.set_ylim(int(y_min)-(int(y_min))*0.1, int(y_max)+(int(y_max)*0.1))  # 最小値、最大値を設定（必要に応じて変更）
            #ax.set_ylim(y_min, y_max)  # 最小値、最大値を設定（必要に応じて変更）

            # Y軸のフォーマットを設定（千円単位、カンマ区切り）
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x/1000):,}"))

            # チャートの設定
            ax.set_title(f"時系列分析: {l_val}")
            ax.set_xlabel("日付")
            ax.set_ylabel("売上金額")
            ax.legend()
            ax.grid(True)

            # 余白を調整
            plt.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.2)

            # プロットをTkinterウィジェットに埋め込む
            canvas = FigureCanvasTkAgg(fig, master=self.labelFrame_out2)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            erMsg = "時系列分析チャートの表示中にエラーが発生しました。"
            msg.showerror("エラー", f"{erMsg}\n{e}")
            logging.exception(erMsg)        


    def _out_histogram(self, df, col1, col2, l_val):
        """
        「ヒストグラム分析」ボタン押下処理　

        Returns
        -------
        str
            DESCRIPTION.

        """
        # 既存のチャートを削除
        try:
            for widget in self.labelFrame_out2.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

            min_value = min(set(df[col1] + df[col2]))  # 最小値を設定
            max_value = max(set(df[col1] + df[col2])) # 最大値を設定
            
            _from, _to = self.framePeriod.get_cound_perid_datetime()
            _diff = (_to - _from).days
                
            ax.hist(df[col1], bins=30, alpha=0.5, label=f"{_from.strftime('%Y年%m月%d日')}:{_to.strftime('%Y年%m月%d日')}({_diff})", range=(min_value, max_value))
        
            _from2, _to2 = self.framePeriod.get_cound_perid_datetime_pre()
            _diff2 = (_to - _from).days
            
            ax.hist(df[col2], bins=30, alpha=0.5, label=f"{_from2.strftime('%Y年%m月%d日')}:{_to2.strftime('%Y年%m月%d日')}({_diff2})", range=(min_value, max_value)) 
            # X軸のフォーマットを設定（千円単位、カンマ区切り）
            ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, _: f"{int(x/1000):,}"))

            
            # タイトル
            ax.set_title(f'ヒストグラム分析:({l_val})')
            # x軸とy軸にラベルの追加
            ax.set_xlabel(USECOLS_NAME[self.var_radio_select_vals.get()])
            ax.set_ylabel('Frequency')
            #　データラベルの追加
            ax.legend()        
            # グリッド線の追加
            ax.grid(True)

            # 余白を調整
            plt.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.2)

            # プロットをTkinterウィジェットに埋め込む
            canvas = FigureCanvasTkAgg(fig, master=self.labelFrame_out2)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise


    def _out_pie(self, df, key, col1, col2, l_val):
        """
        横棒グラフ分析処理（円グラフを横棒グラフに置き換え）

        Parameters
        ----------
        df : pandas.DataFrame
            プロットするデータフレーム
        l_val : str
            チャートのタイトルに使用するラベル
        key : str
            グループ化に使用するキー

        Returns
        -------
        None
        """
        try:
            # 既存のチャートを削除
            for widget in self.labelFrame_out2.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(8, 6))
            # 横棒グラフのデータを集計
            labels = df[key]
            sizes = df[col1]  # 売上金額の列を指定"]
            sizes2 = df[col2]  # 売上金額の列を指定"]

            # 横棒グラフのプロット
            y_pos = range(len(labels))  # ラベルの位置
            ax.barh(y_pos, sizes, align='center', alpha=0.5,)
            ax.barh(y_pos, sizes2, align='center', alpha=0.5,)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels)
            ax.invert_yaxis()  # ラベルを上から下に表示
            ax.set_xlabel("売上金額")
            ax.set_title(f"横棒グラフ分析: {l_val}")

            # 値を各バーの右側に表示
            # for i, v in enumerate(sizes):
            #     ax.text(v, i, f"{v:,.0f}", va='center', fontsize=6)

            # 余白を調整
            plt.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)

            # プロットをTkinterウィジェットに埋め込む
            canvas = FigureCanvasTkAgg(fig, master=self.labelFrame_out2)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            logging.exception("エラーが発生しました")
            raise

def click_close():
    print("プロセスを終了しました")
    app.destroy()  # 明示的にプロセスを終了

if __name__ == "__main__":
    salesDataFrame = analysis_data.Analysis_data()
    
    app = MyApp()
    app.protocol("WM_DELETE_WINDOW", click_close) #フォームを閉じるボタン押下処理
    app.mainloop()

