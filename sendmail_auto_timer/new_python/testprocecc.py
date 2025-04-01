from pystray import Icon, MenuItem, Menu
from PIL import Image
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
import main 

def on_exit(icon, item):
    icon.stop()

def on_mg():
    main()
    pass

def show_message():
    root = tk.Tk()
    root.withdraw()  # Tkinterのメインウィンドウを非表示にする
    messagebox.showinfo("Reminder", "指定した時刻になりました！")
    root.destroy()

def schedule_message(target_hour, target_minute):
    def check_time():
        while True:
            now = time.localtime()
            if now.tm_hour == target_hour and now.tm_min == target_minute:
                show_message()
                break
            time.sleep(30)  # 30秒ごとに確認
    
    threading.Thread(target=check_time, daemon=True).start()

def main():
    # アイコン画像を作成（16x16ピクセルのシンプルな画像）
    image = Image.new('RGB', (16, 16), (255, 0, 0))
    
    # メニューを作成
    menu = Menu(
        MenuItem('Exit', on_exit),
        MenuItem('管理メニュー', on_mg)
    )
    
    # タスクトレイアイコンを作成
    icon = Icon("TestApp", image, menu=menu)
    
    # 指定した時刻にメッセージを表示（例: 15時30分）
    schedule_message(22, 10)
    
    # タスクトレイに常駐
    icon.run()

if __name__ == "__main__":
    main()
