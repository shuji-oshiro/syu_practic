import os
import glob
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from dotenv import load_dotenv
import cv2  # 動画サムネイル用
import numpy as np
import functools
from functools import partial


load_dotenv()
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER')
TAGS_JSON = os.getenv('TAGS_JSON')
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
        self.image_tag_map = {}  # 画像ファイルパス: set(タグ)
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

        self.bind("<Configure>", self.on_window_resize)

        self.scan_tags()
        self.create_tag_buttons()
        self.after_idle(self.show_thumbnails)  # 初期表示時は遅延実行

    def scan_tags(self):
        # 指定フォルダ内の画像・動画ファイルを全て取得し、tags.jsonからタグを取得（なければ空集合）
        self.image_tag_map = {}
        self.all_tags = set()
        # 画像・動画拡張子
        exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')
        # フォルダ内の全ファイル取得
        files = [f for f in os.listdir(self.folder) if os.path.splitext(f)[1].lower() in exts]
        # tags.json読み込み
        tag_dict = {}
        if os.path.exists(TAGS_JSON):
            try:
                with open(TAGS_JSON, "r", encoding="utf-8") as f:
                    tag_dict = json.load(f)
            except Exception as e:
                print(f"{TAGS_JSON} の読み込みに失敗: {e}")
        # 各ファイルについてタグを取得
        for fname in files:
            path = os.path.join(self.folder, fname)
            tags = set(tag_dict.get(fname, []))
            self.image_tag_map[path] = tags
            self.all_tags.update(tags)
        # タグなしファイルがある場合は「タグなし」もall_tagsに追加
        if any(len(tags) == 0 for tags in self.image_tag_map.values()):
            self.all_tags.add('タグなし')
        # タグなしファイルには仮想的に「タグなし」タグを付与
        for path, tags in self.image_tag_map.items():
            if not tags:
                self.image_tag_map[path] = {'タグなし'}

    def create_tag_buttons(self):
        # タグ一覧からトグルボタン（Checkbutton）を作成し、画面上部に並べる
        for widget in self.tag_frame.winfo_children():
            widget.destroy()
        self.check_vars = {}
        col = 0
        self.max_tag_btn_width = 0
        if not self.all_tags:
            lbl = ttk.Label(self.tag_frame, text="タグなし")
            lbl.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            self.max_tag_btn_width = lbl.winfo_reqwidth()
        else:
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
        

    def show_thumbnails(self):
        # 選択中のタグすべてを含む画像・動画のみサムネイル表示（AND検索、タグ未選択時は全件表示）
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()
        self.thumbnail_labels.clear()  # ラベルもクリア
        filtered = []
        if self.selected_tags:
            for file, tags in self.image_tag_map.items():
                if self.selected_tags.issubset(tags):
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
                
                # キャッシュから画像を取得、なければ生成
                if cache_key not in self._thumbnail_cache:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in VIDEO_EXTS:
                        img = self.get_video_thumbnail(file)
                    else:
                        img = Image.open(file)
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
                    widget.bind("<Double-Button-1>", lambda e, path=file: self.open_with_default_app(path))
                    widget.bind("<Button-1>", partial(self.on_thumbnail_click, path=file))
                
                self.thumbnails.append(tk_img)
            except Exception as e:
                print(f"{file} の読み込みに失敗: {e}")

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

    def open_with_default_app(self, path):
        # 画像・動画をWindows標準アプリで開く
        try:
            os.startfile(path)
        except Exception as e:
            print(f"{path} のオープンに失敗: {e}")

def main():
    app = ThumbnailApp(IMAGE_FOLDER)
    app.mainloop()

if __name__ == "__main__":
    main()
