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


load_dotenv()
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER')
PICTURE_TAGS_JSON = os.getenv('PICTURE_TAGS_JSON')

THUMBNAIL_SIZE = (128, 128)
VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')

class ThumbnailApp(tk.Tk):

    def __init__(self, folder):
        super().__init__()
        self.title("画像・動画サムネイルビューア")
        self.geometry("900x700")
        self.folder = folder
        self.selected_tags = set()
        self.all_tags = set()
        self.image_tag_map = {} # 画像ファイルパス: Json対応
        self.check_vars = {}  # タグ: tk.BooleanVar
        self.thumbnails = []  # 参照保持用
        self.min_thumb_width = THUMBNAIL_SIZE[0] + 20  # サムネイル1件分の最小幅（パディング込み）
        self.max_tag_btn_width = 0  # タグボタンの最大幅
        self.current_columns = 1  # 現在のカラム数
        self._last_size = (self.winfo_width(), self.winfo_height())
        self.selected_items = set()  # 選択中のファイルパス
        self._thumbnail_cache = {}  # サムネイルキャッシュ
        self.thumbnail_labels = {}  # サムネイルラベル保持

        # タグバー（上部固定、横スクロール）
        self.tag_frame_outer = ttk.Frame(self)
        self.tag_frame_outer.pack(side="top", fill="x", padx=10, pady=5)
        self.tag_canvas = tk.Canvas(self.tag_frame_outer, height=40)
        self.tag_scrollbar = ttk.Scrollbar(self.tag_frame_outer, orient="horizontal", command=self.tag_canvas.xview)
        self.tag_frame = ttk.Frame(self.tag_canvas)
        self.tag_frame_id = self.tag_canvas.create_window((0, 0), window=self.tag_frame, anchor="nw")
        self.tag_canvas.configure(xscrollcommand=self.tag_scrollbar.set)
        self.tag_canvas.pack(side="top", fill="x", expand=True)
        self.tag_scrollbar.pack(side="bottom", fill="x")
        self.tag_frame.bind("<Configure>", self.on_tag_frame_configure)
        self.tag_canvas.bind("<Configure>", self.on_tag_canvas_configure)

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

        self.dummy_menu = None

        self.scan_tags()
        self.create_tag_buttons()
        self.after_idle(self.show_thumbnails)  # 初期表示時は遅延実行
            
        
    def scan_tags(self):

        # 画像・動画拡張子
        exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')
        # フォルダ内の全ファイル取得
        files = [f for f in os.listdir(self.folder) if os.path.splitext(f)[1].lower() in exts]

        # 初回はすべてタグなし処理を実行
        for fname in files:
            file_path = os.path.join(self.folder, fname)
            mtime = os.path.getmtime(file_path)  # UNIXタイムスタンプ
            # 日付文字列に変換（例: 2024-05-30 12:34:56）
            mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            # print(fname, mtime_str)
            self.image_tag_map[fname] = {"createday":mtime_str,"tags":["タグなし"]}
            
        self.all_tags.update(["タグなし"])

        # タグマップファイルが存在する場合は読み込む
        if os.path.exists(PICTURE_TAGS_JSON):
            try:
                with open(PICTURE_TAGS_JSON, "r", encoding="utf-8") as f:
                    update_map = json.load(f)

                # 該当するファイルのタグを取得
                for fname in self.image_tag_map.keys():
                    self.image_tag_map[fname]["tags"] = update_map[fname]["tags"]
                    self.all_tags.update(update_map[fname]["tags"])

            except Exception as e:
                print(f"{PICTURE_TAGS_JSON} の読み込みに失敗: {e}")

        # ファイルがない場合はタグマップファイルを新規作成     
        else:            
            try:
                with open(PICTURE_TAGS_JSON, "w", encoding="utf-8") as f:
                    json.dump(self.image_tag_map, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"{PICTURE_TAGS_JSON} の保存に失敗: {e}")

                

    def create_tag_buttons(self):
        # タグ一覧からトグルボタン（Checkbutton）を作成し、画面上部に並べる
        for widget in self.tag_frame.winfo_children():
            widget.destroy()
        self.check_vars = {}
        col = 0
        self.max_tag_btn_width = 0

        for tag in sorted(self.all_tags):
            var = tk.BooleanVar()
            btn = ttk.Checkbutton(self.tag_frame, text=tag, variable=var, command=self.on_tag_toggle)
            btn.grid(row=0, column=col, padx=5, pady=2, sticky="w")
            self.check_vars[tag] = var
            col += 1
            self.tag_frame.update_idletasks()
            self.max_tag_btn_width = max(self.max_tag_btn_width, btn.winfo_reqwidth())
        # サムネイルの最小幅をタグボタン最大幅とサムネイルサイズで決定
        self.min_thumb_width = max(self.max_tag_btn_width + 20, THUMBNAIL_SIZE[0] + 20)

    def on_tag_toggle(self):
        # トグルボタンのON/OFF状態から選択中のタグ集合を更新し、サムネイルを再表示する
        self.selected_tags = {tag for tag, var in self.check_vars.items() if var.get()}
        self.show_thumbnails()


    def get_video_thumbnail(self, filepath):
        # 動画ファイルの1フレーム目をサムネイル画像（PIL.Image）として返す
        try:
            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img.thumbnail(THUMBNAIL_SIZE)
                return img
        except Exception as e:
            print(f"{filepath} の動画サムネイル生成に失敗: {e}")
        # 失敗時はダミー画像
        return Image.new('RGB', THUMBNAIL_SIZE, (128, 128, 128))

    def on_window_resize(self, event):
        
        if event.widget == self:
            
            new_size = (self.winfo_width(), self.winfo_height())
            
            # サイズが本当に変わったときだけ再描画
            if new_size != self._last_size:
                print("on_window_resize_new_size_changed")
                self._last_size = new_size
                self.after_idle(self.show_thumbnails)        

    def show_thumbnails(self):
        # 選択中のタグすべてを含む画像・動画のみサムネイル表示（AND検索、タグ未選択時は全件表示）
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()
        self.thumbnail_labels.clear()  # ラベルもクリア
        filtered = []
        if self.selected_tags:
            for file in self.image_tag_map.keys():
                if self.selected_tags.issubset(self.image_tag_map[file]["tags"]):
                    filtered.append(file)
        else:
            filtered = list(self.image_tag_map.keys())
        # ウィンドウ幅からカラム数を動的に決定
        frame_width = self.winfo_width()
        if frame_width < self.min_thumb_width:
            frame_width = self.winfo_width() if self.winfo_width() > 1 else 900
        columns = max(1, frame_width // self.min_thumb_width)
        self.current_columns = columns
        # スタイル定義
        style = ttk.Style()
        style.configure("Selected.TLabel", background="#0066cc")
        style.configure("TLabel", background="#ffffff")

        for idx, file in enumerate(filtered):
            try:
                # キャッシュキーの生成
                cache_key = f"{file}_{THUMBNAIL_SIZE[0]}_{THUMBNAIL_SIZE[1]}"
                
                file_path = os.path.join(self.folder, file)
                # キャッシュから画像を取得、なければ生成
                if cache_key not in self._thumbnail_cache:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in VIDEO_EXTS:
                        img = self.get_video_thumbnail(file_path)
                    else:
                        img = Image.open(file_path)
                        img.thumbnail(THUMBNAIL_SIZE)
                    self._thumbnail_cache[cache_key] = img
                else:
                    img = self._thumbnail_cache[cache_key]
                
                tk_img = ImageTk.PhotoImage(img)
                thumb_frame = ttk.Frame(self.image_frame)
                thumb_frame.grid(row=idx // columns, column=idx % columns, padx=10, pady=10)
                
                style_name = "Selected.TLabel" if file in self.selected_items else "TLabel"
                lbl = ttk.Label(thumb_frame, image=tk_img, text=os.path.basename(file), compound="top", style=style_name)
                lbl.pack()
                self.thumbnail_labels[file] = lbl  # ラベルを保存
                
                # イベントバインディング
                for widget in [thumb_frame, lbl]:
                    widget.bind("<Double-Button-1>", lambda e, path=file_path, file=file: self.open_with_default_app(e, path, file))
                    widget.bind("<Button-1>", partial(self.on_thumbnail_click, path=file))
                self.thumbnails.append(tk_img)
            except Exception as e:
                print(f"{file} の読み込みに失敗: {e}")

        # image_frame全体で右クリック時にメニューを表示
        self.image_frame.bind("<Button-3>", self.on_main_frame_right_click)

    def on_thumb_frame_configure(self, event):
        # サムネイル一覧のFrameサイズ変更時にCanvasのスクロール領域を更新
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))

    def on_thumb_canvas_configure(self, event):
        # サムネイルCanvasのサイズ変更時にFrameの幅を合わせる
        self.thumb_canvas.itemconfig(self.frame_id, width=event.width)

    def on_tag_frame_configure(self, event):
        # タグバーのFrameサイズ変更時にCanvasのスクロール領域を更新
        self.tag_canvas.configure(scrollregion=self.tag_canvas.bbox("all"))

    def on_tag_canvas_configure(self, event):
        # タグバーCanvasのサイズ変更時にFrameの幅を合わせる
        self.tag_canvas.itemconfig(self.tag_frame_id, width=event.width)

    def on_thumbnail_click(self, event, path):
        # サムネイルをクリックしたときの選択・解除処理
        if path in self.selected_items:
            self.selected_items.remove(path)
            style_name = "TLabel"
        else:
            self.selected_items.add(path)
            style_name = "Selected.TLabel"
        # ラベルのstyleだけ変更
        if path in self.thumbnail_labels:
            self.thumbnail_labels[path].configure(style=style_name)

    def on_dummy_menu_close(self, selected_tags = None):

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
                    with open(PICTURE_TAGS_JSON, "w", encoding="utf-8") as f:
                        json.dump(self.image_tag_map, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"タグマップの保存に失敗しました: {e}")

            else:
                messagebox.showinfo(tk.messagebox.INFO, "更新はキャンセルされました")

        self.dummy_menu.destroy()
            

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

    def on_mousewheel(self, event):
        # Windows, Mac, Linux対応のマウスホイールスクロール
        if event.num == 4:  # Linux上スクロール
            self.thumb_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux下スクロール
            self.thumb_canvas.yview_scroll(1, "units")
        elif hasattr(event, 'delta'):
            if event.delta > 0:
                self.thumb_canvas.yview_scroll(-1, "units")
            else:
                self.thumb_canvas.yview_scroll(1, "units")


def main():
    app = ThumbnailApp(IMAGE_FOLDER)
    app.mainloop()

if __name__ == "__main__":
    main()
