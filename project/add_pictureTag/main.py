import os
import cv2
import json
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ExifTags

# グローバル変数でファイルリストとインデックスを管理
file_dict = {}  # {ファイルパス: 'image' or 'video'}
file_order = []  # ファイルパスの順番リスト
current_index = 0
current_video_cap = None

# トグルボタンを5つにし、表示名と内部値を指定通りに変更
# 表示名:内部値 のペア
TOGGLE_TAGS = [
    ("風景", "landscape"),
    ("人物", "person"),
    ("仕事", "work"),
    ("家族", "Family"),
    ("その他", "other"),
]
toggle_states = {tag_val: False for _, tag_val in TOGGLE_TAGS}
toggle_buttons = {}  # 追加

TAGS_JSON = "tags.json"

def load_tags():
    if os.path.exists(TAGS_JSON):
        with open(TAGS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tags(tags_dict):
    with open(TAGS_JSON, "w", encoding="utf-8") as f:
        json.dump(tags_dict, f, ensure_ascii=False, indent=2)

def select_folder():
    global file_dict, file_order, current_index, current_video_cap
    folder = filedialog.askdirectory()
    if folder:
        files = os.listdir(folder)
        image_files = [f for f in files if f.lower().endswith((
            '.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        video_files = [f for f in files if f.lower().endswith((
            '.mp4', '.avi', '.mov', '.wmv'))]
        file_order = [os.path.join(folder, f) for f in image_files + video_files]
        file_dict = {os.path.join(folder, f): 'image' for f in image_files}
        file_dict.update({os.path.join(folder, f): 'video' for f in video_files})
        current_index = 0
        if file_order:
            show_current()

def show_current():
    global file_dict, file_order, current_index, current_video_cap
    if not file_order:
        return
    if current_video_cap is not None:
        current_video_cap.release()
        current_video_cap = None
    file_path = file_order[current_index]
    ftype = file_dict[file_path]
    # タグの自動反映
    file_name = os.path.basename(file_path)
    tags_dict = load_tags()

    
    if file_name not in tags_dict:
        tags_dict[file_name] = []
    tags = tags_dict[file_name]

    for disp, tag_val in TOGGLE_TAGS:
        if disp in tags:
            toggle_states[tag_val] = True
            toggle_buttons[tag_val].config(bg='lightgreen')
        else:
            toggle_states[tag_val] = False
            toggle_buttons[tag_val].config(bg='SystemButtonFace')
    if ftype == 'image':
        show_image_with_orientation(file_path)
    elif ftype == 'video':
        play_video(file_path)

def next_file():
    global current_index, file_order
    save_current_image_tags_to_json()

    if file_order and current_index < len(file_order) - 1:
        current_index += 1
        show_current()

def prev_file():
    global current_index, file_order
    save_current_image_tags_to_json()

    if file_order and current_index > 0:
        current_index -= 1
        show_current()

def show_image_with_orientation(file_path):
    img = Image.open(file_path)
    # ExifのOrientationで回転補正
    try:
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == 'Orientation':
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
    except Exception as e:
        pass

    width, height = img.size
    max_w, max_h = 400, 300

    # アスペクト比を維持してリサイズ
    if width > height:
        # 横長（ランドスケープ）
        ratio = max_w / width
        new_w = max_w
        new_h = int(height * ratio)
    else:
        # 縦長（ポートレート）または正方形
        ratio = max_h / height
        new_h = max_h
        new_w = int(width * ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # キャンバスを作り中央に配置（余白は白）
    canvas = Image.new('RGB', (max_w, max_h), (255, 255, 255))
    x = (max_w - new_w) // 2
    y = (max_h - new_h) // 2
    canvas.paste(img, (x, y))

    img_tk = ImageTk.PhotoImage(canvas)
    label.config(image=img_tk)
    label.image = img_tk

def play_video(video_path):
    global current_video_cap
    cap = cv2.VideoCapture(video_path)
    current_video_cap = cap
    def next_frame():
        if cap != current_video_cap:
            cap.release()
            return
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((400, 300))
            imgtk = ImageTk.PhotoImage(image=img)
            label.config(image=imgtk)
            label.image = imgtk
            label.after(30, next_frame)
        else:
            cap.release()
    next_frame()


def toggle_button(tag_val):
    toggle_states[tag_val] = not toggle_states[tag_val]
    btn = toggle_buttons[tag_val]
    if toggle_states[tag_val]:
        btn.config(bg='lightgreen')
    else:
        btn.config(bg='SystemButtonFace')
    print(f"{tag_val}トグル: {'ON' if toggle_states[tag_val] else 'OFF'}")

def save_current_image_tags_to_json():
    file_path = file_order[current_index]
    file_name = os.path.basename(file_path)
    tags = [disp for (disp, tag_val) in TOGGLE_TAGS if toggle_states[tag_val]]
    tags_dict = load_tags()
    tags_dict[file_name] = tags
    save_tags(tags_dict)
    print(f"{file_name} にタグ {tags} を保存しました")

# --- ここからウィジェット生成 ---
root = tk.Tk()
root.geometry("600x500")
root.resizable(False, False)

y_offset = 30
btn = tk.Button(root, text="フォルダ選択", command=select_folder)
btn.place(x=300, y=y_offset, anchor="center")

y_offset += 40
x_start = 100
for i, (disp, tag_val) in enumerate(TOGGLE_TAGS):
    btn_toggle = tk.Button(root, text=disp, width=8, command=lambda t=tag_val: toggle_button(t))
    btn_toggle.place(x=x_start + i*100, y=y_offset, anchor="center")
    toggle_buttons[tag_val] = btn_toggle
    toggle_states[tag_val] = False  # 初期状態をFalseに設定

label = tk.Label(root)
label.place(x=300, y=270, anchor="center", width=400, height=300)

btn_prev = tk.Button(root, text="← 戻る", command=prev_file)
btn_prev.place(x=80, y=270, anchor="center")
btn_next = tk.Button(root, text="次へ →", command=next_file)
btn_next.place(x=520, y=270, anchor="center")

root.mainloop()