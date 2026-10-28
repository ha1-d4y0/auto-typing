import time
import threading
import tkinter as tk
import pyautogui
import pytesseract
import keyboard
import cv2
import numpy as np
from PIL import Image

#environment
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

INTERVAL_TIME = 0.10  #監視周期
TYPE_INTERVAL = 0.002 #打鍵速度

KEY_TOGGLE = "^"   
KEY_SELECT = "\\"  
# ====================================================

class StealthOCRApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 

#window
        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.geometry("800x120+10+10") 
        self.overlay.config(bg="maroon")
        self.overlay.attributes("-transparentcolor", "maroon")
        
        self.canvas = tk.Canvas(self.overlay, bg="maroon", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

#debug
        self.box_window = tk.Toplevel()
        self.box_window.overrideredirect(True)
        self.box_window.attributes("-topmost", True)
        self.box_window.config(bg="maroon")
        self.box_window.attributes("-transparentcolor", "maroon")
        self.box_window.withdraw()
        
        self.box_canvas = tk.Canvas(self.box_window, bg="maroon", highlightthickness=0)
        self.box_canvas.pack(fill="both", expand=True)

        self.running = False
        self.selected_region = None
        
        self.current_full_text = ""  
        self.typed_index = 0         
        self.last_sent_text = "" 
        
        self.selector_window = None
        self.toggle_key_pressed = False
        self.select_key_pressed = False

        print("====================")
        print("[\\] キーで範囲を選択")
        print("====================")
        self.draw_overlay_ui("---")

        self.loop_thread = threading.Thread(target=self.ocr_worker, daemon=True)
        self.loop_thread.start()
        self.monitor_loop()

    def draw_overlay_ui(self, text):
        self.canvas.delete("all")
        status_symbol = "🟢" if self.running else "🔴"
        display_text = f"{status_symbol} {text}"
        guide_text = f"操作方法 ── [{KEY_TOGGLE}]: 開始/一時停止  │  [{KEY_SELECT}]: 範囲選択"
        
        x, y = 10, 10
        font_main = ("Impact", 26, "bold")
        offsets = [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]
        
        for ox, oy in offsets:
            self.canvas.create_text(x + ox, y + oy, text=display_text, font=font_main, fill="black", anchor="nw")
            
        main_color = "#4af626" if self.running else "#ff9f43"
        self.canvas.create_text(x, y, text=display_text, font=font_main, fill=main_color, anchor="nw")

        gx, gy = 12, 60
        font_guide = ("Meiryo", 9, "bold")
        for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            self.canvas.create_text(gx + ox, gy + oy, text=guide_text, font=font_guide, fill="black", anchor="nw")
        self.canvas.create_text(gx, gy, text=guide_text, font=font_guide, fill="#e3e3e3", anchor="nw")

    def update_debug_box(self):
        if not self.selected_region:
            return
        x, y, w, h = self.selected_region
        self.box_window.geometry(f"{w+6}x{h+6}+{x-3}+{y-3}")
        self.box_canvas.delete("all")
        self.box_canvas.create_rectangle(2, 2, w+4, h+4, outline="#FF0000", width=2)
        self.box_window.deiconify()

    def toggle_range_selection(self):
        if self.selector_window and self.selector_window.winfo_exists():
            self.selector_window.destroy()
            return

        self.selector_window = tk.Toplevel()
        self.selector_window.attributes("-fullscreen", True, "-alpha", 0.3, "-topmost", True)
        self.selector_window.config(cursor="cross")
        
        canvas = tk.Canvas(self.selector_window, bg="grey", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def press(e): self.start_x, self.start_y = e.x, e.y
        def move(e):
            canvas.delete("rect")
            canvas.create_rectangle(self.start_x, self.start_y, e.x, e.y, outline="#00a8ff", width=2, tags="rect")
        def release(e):
            x, y = min(self.start_x, e.x), min(self.start_y, e.y)
            w, h = abs(self.start_x - e.x), abs(self.start_y - e.y)
            if w > 10 and h > 10:
                self.selected_region = (x, y, w, h)
                self.update_debug_box()
                self.selector_window.destroy()
                print(f"[DEBUG] 範囲設定完了: 座標(X={x}, Y={y}), サイズ(W={w}, H={h})")
                self.draw_overlay_ui("READY")

        canvas.bind("<ButtonPress-1>", press)
        canvas.bind("<B1-Motion>", move)
        canvas.bind("<ButtonRelease-1>", release)

    def monitor_loop(self):
        try:
            if keyboard.is_pressed(KEY_TOGGLE):
                if not self.toggle_key_pressed:
                    if self.selected_region:
                        self.running = not self.running
                        print(f"[STATUS] 状態変更 -> {'ON(🟢)' if self.running else 'OFF(🔴)'}")
                        self.draw_overlay_ui(self.current_full_text if self.current_full_text else "START")
                    self.toggle_key_pressed = True
            else:
                self.toggle_key_pressed = False

            if keyboard.is_pressed(KEY_SELECT):
                if not self.select_key_pressed:
                    self.toggle_range_selection()
                    self.select_key_pressed = True
            else:
                self.select_key_pressed = False
        except: pass
        self.root.after(20, self.monitor_loop)

    def process_image_fast(self, screenshot):
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_yellow = np.array([10, 40, 60])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        frame[yellow_mask > 0] = [255, 255, 255]

        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        frame[red_mask > 0] = [255, 255, 255]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        return binary

    def clean_and_correct_text(self, raw_text):
        t = raw_text.strip().upper()
        t = t.replace('L', 'I')
        t = "".join([c for c in t if c.isupper() or c in [',', '-', '.']])
        t = t.lower()

        if t.endswith('ti,') or t.endswith('ti-') or t.endswith('ti.'): t = t.replace('ti', 'i')
        if t.endswith('t,') or t.endswith('t-') or t.endswith('t.'): t = t.replace('t', 'i')
        t = t.replace('lti', 'i').replace('lt', 'i')

        if t and t[-1] in [',', '-']:
            t = t[:-1] + '.'
        elif t and not t.endswith('.'):
            t = t + '.'
            
        return t

    def ocr_worker(self):
        while True:
            if not self.running or not self.selected_region:
                time.sleep(0.1)
                continue

            try:
                screenshot = pyautogui.screenshot(region=self.selected_region)
                binary_img = self.process_image_fast(screenshot)
                pil_img = Image.fromarray(binary_img)
                
                raw_text = pytesseract.image_to_string(
                    pil_img, 
                    lang='eng', 
                    config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz,-.'
                )
                
                ocr_result = self.clean_and_correct_text(raw_text)
                
                if not ocr_result or len(ocr_result) < 3 or ocr_result == self.last_sent_text:
                    time.sleep(0.05)
                    continue

                current_remains = self.current_full_text[self.typed_index:]
                
                if not self.current_full_text or (ocr_result not in current_remains and len(ocr_result) >= 5):
                    self.current_full_text = ocr_result
                    self.typed_index = 0
                    print(f"\n [検知]:{self.current_full_text}")

                match_index = self.current_full_text.rfind(ocr_result)
                
                if match_index != -1:
                    to_type = self.current_full_text[self.typed_index : match_index + len(ocr_result)]
                    
                    if to_type:
                        if to_type == ".":
                            continue
                            
                        print("\n--デバック--")
                        print(f"1.OCR認識    : '{ocr_result}'")
                        print(f"2.現在の問題文   : '{self.current_full_text}'")
                        print(f"3.送信する差分テキスト: '{to_type}'")
                        
                        self.typed_index += len(to_type)
                        self.last_sent_text = ocr_result 
                        self.root.after(0, self.draw_overlay_ui, self.current_full_text)
                        
                        pyautogui.write(to_type, interval=TYPE_INTERVAL)
                        print("4. 処理結果               : 送信成功")
                        
                        time.sleep(0.22)

            except Exception as e:
                print(f"[ERROR] : {e}")
            
            time.sleep(INTERVAL_TIME)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StealthOCRApp()
    app.run()