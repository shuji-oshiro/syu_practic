# --- データ処理・ロジック専用 ---
# 例：タグスキャンやサムネイルフィルタなどのロジックをここに分離しても良い（将来的な拡張用）

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import functools
import json
import os
import datetime

def scan_tags(self):
    # フォルダ内の画像・動画ファイルをスキャンし、タグ情報を初期化・読み込みする
    files = [f for f in os.listdir(self.folder) if os.path.splitext(f)[1].lower() in self.VIDEO_AND_IMAGE_EXTS]
    # ファイル名をキーにして、タグ情報を初期化・読み込みする
    for fname in files:
        file_path = os.path.join(self.folder, fname)
        mtime = os.path.getmtime(file_path)
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        self.image_tag_map[fname] = {"createday":mtime_str,"tags":["タグなし"]}
    
    self.all_tags.update(["タグなし"])

    # タグマップファイルが存在する場合は読み込み、存在しない場合は新規作成
    if os.path.exists(self.PICTURE_TAGS_JSON):
        try:
            with open(self.PICTURE_TAGS_JSON, "r", encoding="utf-8") as f:
                update_map = json.load(f)
            for fname in self.image_tag_map.keys():
                self.image_tag_map[fname]["tags"] = update_map[fname]["tags"]
                self.all_tags.update(update_map[fname]["tags"])
        except Exception as e:
            print(f"{self.PICTURE_TAGS_JSON} の読み込みに失敗: {e}")
    else:
        try:
            with open(self.PICTURE_TAGS_JSON, "w", encoding="utf-8") as f:
                json.dump(self.image_tag_map, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"{self.PICTURE_TAGS_JSON} の保存に失敗: {e}")

def get_video_thumbnail(self, filepath):
    # 動画ファイルの1フレーム目をサムネイル画像（PIL.Image）として返す
    try:
        cap = cv2.VideoCapture(filepath)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img.thumbnail(self.THUMBNAIL_SIZE)
            return img
    except Exception as e:
        print(f"{filepath} の動画サムネイル生成に失敗: {e}")
    return Image.new('RGB', self.THUMBNAIL_SIZE, (128, 128, 128))


def create_tag_buttons(self):
    # タグ一覧からトグルボタン（Checkbutton）を作成し、画面上部に並べる
    for widget in self.tag_frame.winfo_children():
        widget.destroy()

    self.check_vars = {}
    col = 0
    for tag in sorted(self.all_tags):
        var = tk.BooleanVar()
        btn = ttk.Checkbutton(self.tag_frame, text=tag, variable=var, command=self.on_tag_toggle)
        btn.grid(row=0, column=col, padx=5, pady=2, sticky="w")
        self.check_vars[tag] = var
        col += 1

    # タグフレームのレイアウトを更新し、ウィジェットの配置を確定させる
    self.tag_frame.update_idletasks()

def show_thumbnails(self, selected_tags=None):
    # 選択中のタグ・日付範囲でサムネイルをフィルタし、一覧表示する
    for widget in self.image_frame.winfo_children():
        widget.destroy()
    self.thumbnails.clear()
    self.thumbnail_labels.clear()
    filtered = []

    # 選択中のタグがある場合は、そのタグを含むファイルをフィルタリング
    if selected_tags:
        for file in self.image_tag_map.keys():
            if selected_tags.issubset(self.image_tag_map[file]["tags"]):
                filtered.append(file)
    # 選択中のタグがない場合は、全てのファイルを表示
    else:
        filtered = list(self.image_tag_map.keys())

    # サムネイル表示の列数を計算    
    frame_width = self.winfo_width()

    columns = max(1, frame_width // self.min_thumb_width)
    self.current_columns = columns

    # サムネイルが選択されている状態と選択されていない状態の表示スタイル
    style = ttk.Style()
    style.configure("Selected.TLabel", background="#0066cc") # 選択中のサムネイルの背景色
    style.configure("TLabel", background="#ffffff") # 選択中でないサムネイルの背景色
    
    for idx, file in enumerate(filtered):
        try:
            # サムネイルキャッシュキーを生成
            cache_key = f"{file}_{self.THUMBNAIL_SIZE[0]}_{self.THUMBNAIL_SIZE[1]}"
            file_path = os.path.join(self.folder, file)

            # サムネイルキャッシュがない場合は、サムネイルを生成
            if cache_key not in self._thumbnail_cache:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.VIDEO_EXTS:
                    # 動画の場合は、サムネイルを生成
                    img = self.get_video_thumbnail(file_path)
                else:
                    # 画像の場合は、サムネイルを生成
                    img = Image.open(file_path)
                    img.thumbnail(self.THUMBNAIL_SIZE)
                self._thumbnail_cache[cache_key] = img

            # サムネイルキャッシュがある場合は、キャッシュからサムネイルを取得
            else:
                img = self._thumbnail_cache[cache_key]

            # サムネイルを表示
            tk_img = ImageTk.PhotoImage(img)
            thumb_frame = ttk.Frame(self.image_frame)
            thumb_frame.grid(row=idx // columns, column=idx % columns, padx=10, pady=10)

            # サムネイルが選択されている状態と選択されていない状態で表示方法を変える
            style_name = "Selected.TLabel" if file in self.selected_items else "TLabel"
            lbl = ttk.Label(thumb_frame, image=tk_img, text=os.path.basename(file), compound="top", style=style_name)
            lbl.pack()
            self.thumbnail_labels[file] = lbl

            # イベントハンドラを設定
             
            for widget in [thumb_frame, lbl]:
                # サムネイルをダブルクリックしたときに標準アプリで開く
                widget.bind("<Double-Button-1>", lambda e, path=file_path, file=file: self.open_with_default_app(e, path, file))
                # サムネイルをクリックしたときの選択・解除処理
                widget.bind("<Button-1>", functools.partial(self.on_thumbnail_click, path=file))
            self.thumbnails.append(tk_img)
        except Exception as e:
            print(f"{file} の読み込みに失敗: {e}")
    self.image_frame.bind("<Button-3>", self.on_main_frame_right_click)

def update_thumbnail_view(self):
    # サムネイル表示を更新する（タグ・日付などの条件で再描画）
    self.show_thumbnails()
