import os
import glob
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from dotenv import load_dotenv
import cv2  # 動画サムネイル用
import numpy as np
import functools
from functools import partial
from dummyMenu import DummyMenu
import datetime
from tkcalendar import DateEntry  # 追加
import types
import logic


load_dotenv()

class ThumbnailApp(tk.Tk):

    def __init__(self):
        super().__init__()        
        self.PICTURE_TAGS_JSON = os.getenv('PICTURE_TAGS_JSON')
        self.THUMBNAIL_SIZE = (128, 128)
        self.VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')
        self.VIDEO_AND_IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')
        self.title("画像・動画サムネイルビューア")
        self.geometry("900x700")
        
        self.folder = os.getenv('IMAGE_FOLDER')
        # self.df_image_tag_map = pd.DataFrame()
        self.all_tags = set()
        self.image_tag_map = {} # 画像ファイルパス: Json対応
        self.check_vars = {}  # タグ: tk.BooleanVar
        self.thumbnails = []  # 参照保持用
        self.min_thumb_width = self.THUMBNAIL_SIZE[0] + 20  # サムネイル1件分の最小幅（パディング込み）
        self.current_columns = 1  # 画面に表示されるカラム数　特に使用はしていない　
        self._last_size = (self.winfo_width(), self.winfo_height())
        self.selected_items = set()  # 選択中のファイル
        self.selected_tags = []  # 選択中のタグ
        self._thumbnail_cache = {}  # サムネイルキャッシュ
        self.thumbnail_labels = {}  # サムネイルラベル保持


        # --- 横スクロール可能な tag_frame を作成 ---
        canvas_tags = tk.Canvas(self, height=30)
        canvas_tags.pack(side="top", fill="x", padx=10, pady=5)
        x_scroll_tags = ttk.Scrollbar(self, orient="horizontal", command=canvas_tags.xview)
        # h_scroll.pack(side="top", fill="x", padx=10)
        canvas_tags.configure(xscrollcommand=x_scroll_tags.set)
        # スクロール対象のフレームを Canvas に埋め込む
        self.tag_frame = tk.Frame(canvas_tags)
        
        canvas_tags.create_window((0, 0), window=self.tag_frame, anchor="nw")

        def on_frame_configure(event):
        # tag_frameのサイズ
            frame_width = self.tag_frame.winfo_reqwidth()
            # canvasの表示幅
            canvas_width = canvas_tags.winfo_width()

            # スクロールが必要か判定
            if frame_width > canvas_width:
                x_scroll_tags.pack(side="top", fill="x", padx=10)  # スクロールバーを表示
            else:
                x_scroll_tags.pack_forget()  # スクロールバーを非表示

            # スクロール範囲を更新
            canvas_tags.configure(scrollregion=canvas_tags.bbox("all"))

        self.tag_frame.bind("<Configure>",on_frame_configure)


        # 日付入力コントロール
        self.date_frame = ttk.Frame(self)
        self.date_frame.pack(side="top", fill="x", padx=10, pady=2)
        ttk.Label(self.date_frame, text="FROM").pack(side="left")
        self.from_date_entry = DateEntry(self.date_frame, width=12, date_pattern='yyyy-mm-dd')
        self.from_date_entry.pack(side="left", padx=(0, 10))
        
        self.from_date_entry.bind("<<DateEntrySelected>>", self.on_date_change)
        self.from_date_entry.bind("<FocusOut>", self.on_date_change)
        ttk.Label(self.date_frame, text="TO").pack(side="left")
        self.to_date_entry = DateEntry(self.date_frame, width=12, date_pattern='yyyy-mm-dd')
        self.to_date_entry.pack(side="left")
        self.to_date_entry.bind("<<DateEntrySelected>>", self.on_date_change)
        self.to_date_entry.bind("<FocusOut>", self.on_date_change)

        # サムネイル一覧（下部、縦スクロール）
        # 1. ラッパー用のフレームを作成
        thumb_area = tk.Frame(self)
        thumb_area.pack(side="top", fill="both", expand=True)


        self.canvas_thumb = tk.Canvas(thumb_area)
        self.canvas_thumb.pack(side="left", fill="both", expand=True)
        h_scroll_thumb = ttk.Scrollbar(thumb_area, orient="vertical", command=self.canvas_thumb.yview)
        h_scroll_thumb.pack(side="right", fill="y")
        self.canvas_thumb.configure(yscrollcommand=h_scroll_thumb.set)

        
        self.image_frame = tk.Frame(self.canvas_thumb)
        self.canvas_thumb.create_window((0, 0), window=self.image_frame, anchor="nw")

        def on_image_frame_configure(event):
            # tag_frameのサイズ
            frame_height = self.image_frame.winfo_reqheight()
            # canvasの表示幅
            canvas_height = self.canvas_thumb.winfo_height()

            # スクロールが必要か判定
            if frame_height > canvas_height:
                h_scroll_thumb.pack(side="right", fill="y", padx=10)  # スクロールバーを表示
            else:
                h_scroll_thumb.pack_forget()  # スクロールバーを非表示

            # スクロール範囲を更新
            self.canvas_thumb.configure(scrollregion=self.canvas_thumb.bbox("all"))

        self.image_frame.bind("<Configure>",on_image_frame_configure)


        # マウスホイールスクロール対応
        self.canvas_thumb.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas_thumb.bind_all("<Button-4>", self.on_mousewheel)    # Linux
        self.canvas_thumb.bind_all("<Button-5>", self.on_mousewheel)    # Linux

        self.bind("<Configure>", self.on_window_resize)

        self.scan_tags = types.MethodType(logic.scan_tags, self)
        self.get_video_thumbnail = types.MethodType(logic.get_video_thumbnail, self)
        self.create_tag_buttons = types.MethodType(logic.create_tag_buttons, self)
        self.show_thumbnails = types.MethodType(logic.show_thumbnails, self)
        self.dummy_menu = None

        self.scan_tags()
        self.create_tag_buttons()  

        # サイズ変更時に同様の処理が発生しているため、初期表示時は遅延実行しない
        # print("__init__","show_thumbnails")
        # self.after_idle(self.show_thumbnails)  # 初期表示時は遅延実行

        # サムネイルのcreatedayから最小・最大日付を取得
        createday_list = [
            datetime.datetime.strptime(self.image_tag_map[f]["createday"], "%Y-%m-%d %H:%M:%S")
            for f in self.image_tag_map
            if "createday" in self.image_tag_map[f]
        ]
        if createday_list:
            min_date = min(createday_list).date()
            max_date = max(createday_list).date()
        else:
            today = datetime.date.today()
            min_date = today
            max_date = today
        self.from_date_entry.set_date(min_date)
        self.to_date_entry.set_date(max_date)

    def on_date_change(self, event=None):
        """
        日付が変更された時の処理
        選択された日付範囲に基づいてサムネイルを再表示
        """

        if self.from_date_entry.get_date() > self.to_date_entry.get_date():
            self.to_date_entry.set_date(self.from_date_entry.get_date())
            messagebox.showinfo(tk.messagebox.INFO, "FROMの日付がTOの日付より新しい日付を選択してください")
            return

        print("on_date_change","show_thumbnails")
        self.show_thumbnails()

    def on_tag_toggle(self, tag):
        """
        タグの選択状態が変更された時の処理
        - タグなしと他のタグは排他的に動作
        - タグなしが選択された場合、他のタグを全て解除
        - 他のタグが選択された場合、タグなしを解除
        - 選択状態に基づいてサムネイルを再表示
        """

        if tag == "タグなし":
            flg = self.check_vars[tag].get()
            for _tag in self.check_vars.keys():
                self.check_vars[_tag].set(False)
            if flg:                               
                self.check_vars[tag].set(True)
        else:
            self.check_vars["タグなし"].set(False)

        self.selected_tags = [tag for tag, var in self.check_vars.items() if var.get()]
        self.selected_items.clear()
        print("on_tag_toggle","show_thumbnails")
        self.show_thumbnails()
 

    def on_window_resize(self, event):
        """
        ウィンドウサイズが変更された時の処理
        - 新しいサイズを記録
        - サイズが変更された場合、サムネイルを再配置
        """
        if event.widget == self:
            new_size = (self.winfo_width(), self.winfo_height())
            if new_size != self._last_size:
                self._last_size = new_size

                print("on_window_resize","show_thumbnails")
                self.after_idle(self.show_thumbnails)


    def on_mousewheel(self, event):
        if event.num == 4:
            self.canvas_thumb.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas_thumb.yview_scroll(1, "units")
        elif hasattr(event, 'delta'):
            if event.delta > 0:
                self.canvas_thumb.yview_scroll(-1, "units")
            else:
                self.canvas_thumb.yview_scroll(1, "units")

    # サムネイルクリック時の処理
    def on_thumbnail_click(self, event, path):
        """
        サムネイルがクリックされた時の処理
        - 選択状態を切り替え（選択/非選択）
        - 選択状態に応じてスタイルを変更
        - 選択状態は self.selected_items で管理
        """
        if path in self.selected_items:
            self.selected_items.remove(path)
            style_name = "TLabel"
        else:
            self.selected_items.add(path)
            style_name = "Selected.TLabel"
        if path in self.thumbnail_labels:
            self.thumbnail_labels[path].configure(style=style_name)

    # サブメニューが閉じたときの処理
    def on_dummy_menu_close(self, update_tags=None):
        """
        タグ編集メニューが閉じられた時の処理
        - タグの更新が選択された場合：
          - 選択されたファイルのタグを更新
          - タグ一覧を再読み込み
          - サムネイルを再表示
        - 更新がキャンセルされた場合：
          - メニューを閉じる
        """
        if update_tags:
            if messagebox.askyesno(tk.messagebox.YESNO, f"{update_tags}のタグで\n{len(self.selected_items)}件の選択した写真を更新しますか？"):
                for fname in self.selected_items:
                    self.image_tag_map[fname]["tags"] = update_tags
                
                try:
                    with open(self.PICTURE_TAGS_JSON, "w", encoding="utf-8") as f:
                        json.dump(self.image_tag_map, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"タグマップの保存に失敗しました: {e}")
                    return
                
                self.selected_items.clear()
                self.scan_tags()
                self.create_tag_buttons()

                for tag in update_tags:
                    self.check_vars[tag].set(True)
                    self.selected_tags.append(tag)

                print("on_dummy_menu_close","show_thumbnails")
                self.show_thumbnails()
                self.canvas_thumb.yview_moveto(0)
            else:
                messagebox.showinfo(tk.messagebox.INFO, "更新はキャンセルされました")
        self.dummy_menu.destroy()


    # 画像・動画をWindows標準アプリで開く
    def open_with_default_app(self, event, path, file):
        """
        ファイルをデフォルトアプリケーションで開く処理
        - 指定されたパスのファイルを開く
        - ダブルクリック時はサムネイルの選択を解除
        - エラー発生時はエラーメッセージを表示
        """
        try:
            os.startfile(path)
            self.selected_items.remove(file)
            style_name = "TLabel"
            if file in self.thumbnail_labels:
                self.thumbnail_labels[file].configure(style=style_name)
        except Exception as e:
            print(f"{path} のオープンに失敗: {e}")


    def on_main_frame_right_click(self, event):
        """
        メインフレームで右クリックされた時の処理
        - 選択されたファイルがある場合：
          - タグ編集メニューを表示
          - メニューをモーダルとして表示
        - 選択されたファイルがない場合：
          - ファイルを選択するよう促すメッセージを表示
        """
        if not self.selected_items:
            messagebox.showinfo(tk.messagebox.INFO, "選択されているファイルがありません")
            return

        self.dummy_menu = DummyMenu(self, event.x_root, event.y_root, self.all_tags, self.on_dummy_menu_close)
        self.dummy_menu.transient(self)
        self.dummy_menu.grab_set()
        self.dummy_menu.focus_set()
        self.dummy_menu.protocol("WM_DELETE_WINDOW", self.on_dummy_menu_close)
        

def main():
    app = ThumbnailApp()
    app.mainloop()

if __name__ == "__main__":
    main()
