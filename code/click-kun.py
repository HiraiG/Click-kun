import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
from datetime import datetime
import random
import sys
import threading
import os
import markdown2

class click_app:
    def __init__(self, root):
        self.root = root
        self.root.title("クリックくん")
        self.root.geometry("600x400+400+300")
        
        # メインフレーム
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 間隔設定
        ttk.Label(main_frame, text="クリック間隔（秒）: min").grid(row=0, column=0, pady=5)
        self.min_interval = ttk.Entry(main_frame, width=10)
        self.min_interval.insert(0, "10")
        self.min_interval.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text=" ～ max").grid(row=0, column=2, pady=5)
        
        self.max_interval = ttk.Entry(main_frame, width=10)
        self.max_interval.insert(0, "30")
        self.max_interval.grid(row=0, column=3, pady=5)
        
        # ステータス表示
        self.status_text = tk.Text(main_frame, height=10, width=35)
        self.status_text.grid(row=1, column=0, columnspan=4, pady=10)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=1, column=4, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # ボタン
        self.start_button = ttk.Button(main_frame, text="開始", command=self.start_clicking)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.stop_button = ttk.Button(main_frame, text="停止", command=self.stop_clicking, state="disabled")
        self.stop_button.grid(row=2, column=2, columnspan=2, pady=5)
        
        self.use_button = ttk.Button(main_frame, text="使い方", command=self.show_help)
        self.use_button.grid(row=2, column=4, columnspan=2, pady=5)
        
        # クリック状態
        self.is_clicking = False
        self.click_thread = None
        
        # 安全機能を有効化
        pyautogui.FAILSAFE = True
        
                # 使い方のMarkdown
        self.help_markdown = """
# クリックくんの使い方 📱

---
## 1. クリック間隔の設定 ⚙️
- 設定した範囲内でランダムな間隔でクリックします
- 左の数値 : 最小間隔（秒）
- 右の数値 : 最大間隔（秒）


## 2. 基本操作 🖱️
1. 「開始」ボタンをクリック
2. 5秒以内に、自動クリックしたい画面位置にマウスカーソルを移動
3. 自動クリックが開始されます
4. 停止したい場合は「停止」ボタンをクリック

## 3. 安全機能 🛡️
- マウスを画面の左上隅に素早く移動すると緊急停止します
- アプリケーションを閉じる際は確認メッセージが表示されます

## 4. 注意事項 ⚠️
- クリック間隔は1秒以上を推奨します
- 最小間隔は最大間隔より小さい値を設定してください
- クリック位置は画面内の安全な場所を選んでください

## 5. トラブルシューティング 🔧
- エラーが表示された場合は、入力値を確認してください
- 予期せぬ動作が発生した場合は「停止」ボタンを押してください

---
"""
        
    def update_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        
    def clicking_loop(self):
        try:
            while self.is_clicking:
                current_time = datetime.now().strftime("%H:%M:%S")
                current_x, current_y = pyautogui.position()
                
                # クリック実行
                pyautogui.click()
                self.update_status(f"[{current_time}] クリック実行 - 位置: ({current_x}, {current_y})")
                
                # 待機時間計算（分をセカンドに変換）
                min_time = float(self.min_interval.get())
                max_time = float(self.max_interval.get())
                wait_time = random.uniform(min_time, max_time)
                
                # 1秒ごとにチェック
                for _ in range(int(wait_time)):
                    if not self.is_clicking:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            self.update_status(f"エラーが発生しました: {e}")
            self.stop_clicking()
            
    def start_clicking(self):
        try:
            # 入力値チェック
            min_val = float(self.min_interval.get())
            max_val = float(self.max_interval.get())
            
            if min_val <= 0 or max_val <= 0 or min_val > max_val:
                messagebox.showerror("エラー", "正しい間隔を入力してください")
                return
                
            self.is_clicking = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            self.update_status("5秒後に開始します。マウスを目的の位置に移動してください...")
            self.root.after(5000, self.start_click_thread)
            
        except ValueError:
            messagebox.showerror("エラー", "数値を入力してください")
            
    def start_click_thread(self):
        self.click_thread = threading.Thread(target=self.clicking_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
        self.update_status("クリックを開始しました")
        
    def stop_clicking(self):
        self.is_clicking = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.update_status("クリックを停止しました")
        
    def show_help(self):
        # 使い方ウィンドウの作成
        help_window = tk.Toplevel(self.root)
        help_window.title("クリックくんの使い方")
        help_window.geometry("900x500+300+300")
        
        # HTMLテキストウィジェット
        help_text = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        help_text.pack(expand=True, fill='both')
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(help_text, orient="vertical", command=help_text.yview)
        scrollbar.pack(side='right', fill='y')
        help_text.configure(yscrollcommand=scrollbar.set)
        
        # フォント設定
        help_text.tag_configure('h1', font=('Helvetica', 16, 'bold'))
        help_text.tag_configure('h2', font=('Helvetica', 14, 'bold'))
        help_text.tag_configure('normal', font=('Helvetica', 11))
        help_text.tag_configure('bullet', font=('Helvetica', 11))
        help_text.tag_configure('code', font=('Courier', 11))
        # help_text.tag_configure('em', font=('Helvetica', 11, 'italic'))
        # help_text.tag_configure('strong', font=('Helvetica', 11, 'bold'))
        
        # Markdownをテキストに変換して表示
        html_content = markdown2.markdown(self.help_markdown)
        
        # HTMLコンテンツを行のリストとして保存
        lines = html_content.split('\n')
        
        # テキストを最後に挿入していく
        for line in lines:
            if line.startswith('<h1>'):
                text = line.replace('<h1>', '').replace('</h1>', '')
                help_text.insert('end', f"{text}\n", 'h1')
            elif line.startswith('<h2>'):
                text = line.replace('<h2>', '').replace('</h2>', '')
                help_text.insert('end', f"\n{text}\n", 'h2')
            elif line.startswith('<li>'):
                text = line.replace('<li>', '• ').replace('</li>', '')
                help_text.insert('end', f"{text}\n", 'bullet')
            elif line.startswith('<em>'):
                text = line.replace('<em>', '').replace('</em>', '')
                help_text.insert('end', f"{text}\n", 'italic')
            elif line.startswith('<strong>'):
                text = line.replace('<strong>', '').replace('</strong>', '')
                help_text.insert('end', f"{text}", 'bold')
            elif line.startswith('<code>'):
                text = line.replace('<code>', '').replace('</code>', '')
                help_text.insert('end', f"{text}\n", 'code')
            elif line.startswith('<p>'):
                text = line.replace('<p>', '').replace('</p>', '')
                if text.strip():
                    help_text.insert('end', f"{text}\n", 'normal')
            elif line == '<hr />':
                help_text.insert('end', "─" * 50 + "\n", 'normal')
        
        # テキストを読み取り専用に設定
        help_text.configure(state='disabled')
        
        # ウィンドウを最前面に表示
        help_window.transient(self.root)
        
        # 閉じるボタン
        close_button = ttk.Button(help_window, text="閉じる", command=help_window.destroy)
        close_button.pack(pady=10)
        
    def on_closing(self):
        if messagebox.askokcancel("終了確認", "アプリケーションを終了しますか？"):
            self.stop_clicking()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = click_app(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
