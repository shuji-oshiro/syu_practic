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
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER')
        


class ThumbnailApp(tk.Tk):

    def __init__(self, folder):
        super().__init__()        
        self.PICTURE_TAGS_JSON = os.getenv('PICTURE_TAGS_JSON')
        self.THUMBNAIL_SIZE = (128, 128)
        self.VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')
        self.VIDEO_AND_IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')

        self.title("画像・動画サムネイルビューア")
        self.geometry("900x700")
        self.folder = folder
        self.all_tags = set()
        self.image_tag_map = {} # 画像ファイルパス: Json対応
        self.check_vars = {}  # タグ: tk.BooleanVar
        self.thumbnails = []  # 参照保持用
        self.min_thumb_width = self.THUMBNAIL_SIZE[0] + 20  # サムネイル1件分の最小幅（パディング込み）
        self.current_columns = 1  # 現在のカラム数
        self._last_size = (self.winfo_width(), self.winfo_height())
        self.selected_items = set()  # 選択中のファイルパス
        self._thumbnail_cache = {}  # サムネイルキャッシュ
        self.thumbnail_labels = {}  # サムネイルラベル保持

        # --- 横スクロール可能な tag_frame を作成 ---
        canvas = tk.Canvas(self, height=30)
        canvas.pack(side="top", fill="x", padx=10, pady=5)
        h_scroll = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        h_scroll.pack(side="top", fill="x", padx=10)
        canvas.configure(xscrollcommand=h_scroll.set)
        # スクロール対象のフレームを Canvas に埋め込む
        self.tag_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.tag_frame, anchor="nw")
        self.tag_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))



        # 日付入力コントロール
        self.date_frame = ttk.Frame(self)
        self.date_frame.pack(side="top", fill="x", padx=10, pady=2)
        ttk.Label(self.date_frame, text="FROM").pack(side="left")
        self.from_date_entry = DateEntry(self.date_frame, width=12, date_pattern='yyyy-mm-dd')
        self.from_date_entry.pack(side="left", padx=(0, 10))
        self.from_date_entry.bind("<<DateEntrySelected>>", self.on_date_change)
        ttk.Label(self.date_frame, text="TO").pack(side="left")
        self.to_date_entry = DateEntry(self.date_frame, width=12, date_pattern='yyyy-mm-dd')
        self.to_date_entry.pack(side="left")
        self.to_date_entry.bind("<<DateEntrySelected>>", self.on_date_change)

        # サムネイル一覧（下部、縦スクロール）
        self.thumb_frame_outer = ttk.Frame(self)
        self.thumb_frame_outer.pack(side="top", fill="both", expand=True)
        self.thumb_canvas = tk.Canvas(self.thumb_frame_outer, bg="white")
        self.thumb_scrollbar = ttk.Scrollbar(self.thumb_frame_outer, orient="vertical", command=self.thumb_canvas.yview)
        self.image_frame = ttk.Frame(self.thumb_canvas)
        self.frame_id = self.thumb_canvas.create_window((0, 0), window=self.image_frame, anchor="nw")
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_canvas.pack(side="left", fill="both", expand=True)
        self.thumb_scrollbar.pack(side="right", fill="y")
        self.image_frame.bind("<Configure>", self.on_thumb_frame_configure)
        self.thumb_canvas.bind("<Configure>", self.on_thumb_canvas_configure)

        # マウスホイールスクロール対応
        self.thumb_canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows
        self.thumb_canvas.bind_all("<Button-4>", self.on_mousewheel)    # Linux
        self.thumb_canvas.bind_all("<Button-5>", self.on_mousewheel)    # Linux

        self.bind("<Configure>", self.on_window_resize)

        self.scan_tags = types.MethodType(logic.scan_tags, self)
        self.get_video_thumbnail = types.MethodType(logic.get_video_thumbnail, self)
        self.create_tag_buttons = types.MethodType(logic.create_tag_buttons, self)
        self.show_thumbnails = types.MethodType(logic.show_thumbnails, self)
        self.dummy_menu = None

        self.scan_tags()
        self.create_tag_buttons()        
        self.after_idle(self.show_thumbnails)  # 初期表示時は遅延実行

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
        self.show_thumbnails()

    def on_tag_toggle(self):
        # トグルボタンのON/OFF状態から選択中のタグ集合を更新し、サムネイルを再表示する
        selected_tags = {tag for tag, var in self.check_vars.items() if var.get()}
        self.show_thumbnails(selected_tags)

    def on_window_resize(self, event):
        if event.widget == self:
            new_size = (self.winfo_width(), self.winfo_height())
            if new_size != self._last_size:
                self._last_size = new_size
                self.after_idle(self.show_thumbnails)

    def on_thumb_frame_configure(self, event):
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))

    def on_thumb_canvas_configure(self, event):
        self.thumb_canvas.itemconfig(self.frame_id, width=event.width)

    def on_tag_frame_configure(self, event):
        self.tag_canvas.configure(scrollregion=self.tag_canvas.bbox("all"))

    def on_tag_canvas_configure(self, event):
        self.tag_canvas.itemconfig(self.tag_frame_id, width=event.width)

    def on_mousewheel(self, event):
        if event.num == 4:
            self.thumb_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.thumb_canvas.yview_scroll(1, "units")
        elif hasattr(event, 'delta'):
            if event.delta > 0:
                self.thumb_canvas.yview_scroll(-1, "units")
            else:
                self.thumb_canvas.yview_scroll(1, "units")

    def on_thumbnail_click(self, event, path):
        if path in self.selected_items:
            self.selected_items.remove(path)
            style_name = "TLabel"
        else:
            self.selected_items.add(path)
            style_name = "Selected.TLabel"
        if path in self.thumbnail_labels:
            self.thumbnail_labels[path].configure(style=style_name)

    def on_dummy_menu_close(self, selected_tags=None):
        if selected_tags:
            if messagebox.askyesno(tk.messagebox.YESNO, f"{selected_tags}のタグで\n{len(self.selected_items)}件の選択した写真を更新しますか？"):

                for fname in self.selected_items:
                    self.image_tag_map[fname]["tags"] = selected_tags
                
                for tag in selected_tags:
                    self.all_tags.add(tag)

                self.selected_items.clear()

                self.create_tag_buttons()

                self.show_thumbnails()

                self.thumb_canvas.yview_moveto(0)

                try:
                    with open(self.PICTURE_TAGS_JSON, "w", encoding="utf-8") as f:
                        json.dump(self.image_tag_map, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"タグマップの保存に失敗しました: {e}")

            else:
                messagebox.showinfo(tk.messagebox.INFO, "更新はキャンセルされました")
        self.dummy_menu.destroy()
            

    def open_with_default_app(self, event, path, file):
        # 画像・動画をWindows標準アプリで開く
        try:
            os.startfile(path)

            # ダブルクリック時はサムネイルを選択解除
            self.selected_items.remove(file)
            style_name = "TLabel"
            if file in self.thumbnail_labels:
                self.thumbnail_labels[file].configure(style=style_name)
            
        except Exception as e:
            print(f"{path} のオープンに失敗: {e}")


    def on_main_frame_right_click(self, event):
        if not self.selected_items:
            messagebox.showinfo(tk.messagebox.INFO, "選択されているファイルがありません")
            return

        self.dummy_menu = DummyMenu(self, event.x_root, event.y_root, self.all_tags, self.on_dummy_menu_close)
        self.dummy_menu.transient(self)  # selfはメインウィンドウ
        self.dummy_menu.grab_set()  # サブメニュー表示中はメイン画面操作不可
        self.dummy_menu.focus_set()  # サブメニューにフォーカスを設定
        
        # サブメニューが閉じたときのイベントを設定
        self.dummy_menu.protocol("WM_DELETE_WINDOW", self.on_dummy_menu_close)
        

def main():
    app = ThumbnailApp(IMAGE_FOLDER)
    app.mainloop()

if __name__ == "__main__":
    main()
