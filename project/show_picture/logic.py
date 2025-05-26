# --- データ処理・ロジック専用 ---
# 例：タグスキャンやサムネイルフィルタなどのロジックをここに分離しても良い（将来的な拡張用）

import os
import cv2
import json
import datetime
import functools
import pandas as pd
import tkinter as tk
import collections
from tkinter import ttk
from PIL import Image, ImageTk

def scan_tags(self):
    # フォルダ内の画像・動画ファイルをスキャンし、タグ情報を初期化・読み込みする
    files = [f for f in os.listdir(self.folder) if os.path.splitext(f)[1].lower() in self.VIDEO_AND_IMAGE_EXTS]
    # ファイル名をキーにして、タグ情報を初期化・読み込みする
    for fname in files:
        file_path = os.path.join(self.folder, fname)
        mtime = os.path.getmtime(file_path)
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        self.image_tag_map[fname] = {"createday":mtime_str,"tags":[]}
    
    self.all_tags.clear()
    self.selected_tags.clear()
    # タグマップファイルが存在する場合は読み込み、存在しない場合は新規作成
    if os.path.exists(self.PICTURE_TAGS_JSON):
        try:
            with open(self.PICTURE_TAGS_JSON, "r", encoding="utf-8") as f:
                update_map = json.load(f)
                
            temp =[]
            self.none_tag_cnt = 0 #タグなしカウント
            for fname in self.image_tag_map.keys():
                self.image_tag_map[fname]["tags"] = update_map[fname]["tags"]
                temp.extend(self.image_tag_map[fname]["tags"])

                if not self.image_tag_map[fname]["tags"]:
                    self.none_tag_cnt += 1

            self.all_tags = collections.Counter(temp)

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

    # タグなしボタン
    none_tag = "タグなし"
    var = tk.BooleanVar()
    btn = ttk.Checkbutton(self.tag_frame, text=f"{none_tag} ({self.none_tag_cnt})", variable=var, command=lambda tag=none_tag: self.on_tag_toggle(none_tag))
    self.check_vars[none_tag] = var
    btn.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
    col = 1
    for tag,cnt in self.all_tags.items():
        var = tk.BooleanVar()
        btn = ttk.Checkbutton(self.tag_frame, text=f"{tag} ({cnt})", variable=var,command=lambda tag=tag: self.on_tag_toggle(tag))
        btn.grid(row=0, column=col, padx=5, pady=2, sticky="w")
        btn._tag = tag  # 独自属性としてtagを持たせる
        self.check_vars[tag] = var
        col += 1

    # タグフレームのレイアウトを更新し、ウィジェットの配置を確定させる
    self.tag_frame.update_idletasks()

def show_thumbnails(self):
    # 選択中のタグ・日付範囲でサムネイルをフィルタし、一覧表示する
    for widget in self.image_frame.winfo_children():
        widget.destroy()
    self.thumbnails.clear()
    self.thumbnail_labels.clear()

    df = pd.DataFrame(self.image_tag_map).T
    df["createday"] = pd.to_datetime(df["createday"])

    # 日付範囲でファイルをフィルタリング
    from_date = self.from_date_entry.get_date()
    to_date = self.to_date_entry.get_date()
    
    df = df[(df["createday"].dt.date >= from_date) & (df["createday"].dt.date <= to_date)] 

    # df = df.reset_index(drop=False)
    # 選択中のタグがある場合は、そのタグを含むファイルをフィルタリング
    if self.selected_tags == ["タグなし"]:
        df = df[df['tags'].apply(lambda x: len(x) == 0)]

    elif self.selected_tags:
        df = df[df['tags'].apply(lambda x: set(self.selected_tags).issubset(set(x)))]
 
   
    # サムネイル表示の列数を計算    
    frame_width = self.winfo_width()

    columns = max(1, frame_width // self.min_thumb_width)
    self.current_columns = columns

    # サムネイルが選択されている状態と選択されていない状態の表示スタイル
    style = ttk.Style()
    style.configure("Selected.TLabel", background="#0066cc") # 選択中のサムネイルの背景色
    style.configure("TLabel", background="#ffffff") # 選択中でないサムネイルの背景色
    
    idx = 0
    for file, row in df.iterrows():
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
            idx += 1

            # サムネイルが選択されている状態と選択されていない状態で表示方法を変える
            style_name = "Selected.TLabel" if file in self.selected_items else "TLabel"
            # lbl = ttk.Label(thumb_frame, image=tk_img, text=os.path.basename(file), compound="top", style=style_name)
            
            date_str = row.createday.strftime("%Y-%m-%d")
            lbl_text = f"{os.path.basename(file)}\n{date_str}"

            # ファイル名と日付を表示
            lbl = ttk.Label(thumb_frame, image=tk_img, text=lbl_text, compound="top", style=style_name)
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
