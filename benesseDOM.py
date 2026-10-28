from selenium import webdriver
from selenium.webdriver.common.by import By
from pynput import keyboard
import pyautogui
import time
import argparse

# settings

parser = argparse.ArgumentParser()
parser.add_argument("--speed", type=float, default=5000)
parser.add_argument("--start-key", default="^")
parser.add_argument("--url", default="https://manabi-gakushu.benesse.ne.jp/gakushu/typing/nihongonyuryoku.html")
args = parser.parse_args()

interval = 0 / args.speed

print(f"""
[INFO]打鍵速度 : {args.speed}文字/秒
[INFO]開始キー : {args.start_key}
[INFO]ESC      : 終了
""")

# boot

driver = webdriver.Chrome()
driver.get(args.url)

running = False
stop = False
previous = ""

# key

def on_press(key):
    global running, stop

    try:
        if key.char == args.start_key:
            running = not running
            print(
                f"[KEY] {args.start_key} → "
                f"{'ON' if running else 'OFF'}"
            )
    except AttributeError:
        if key == keyboard.Key.esc:
            stop = True

keyboard.Listener(on_press=on_press).start()

# main

try:
    while not stop:

        if not running:
            time.sleep(0.05)
            continue

        try:
            m = driver.find_element(
                By.ID, "remainingTimeMinutes"
            ).text

            s = driver.find_element(
                By.ID, "remainingTimeSeconds"
            ).text

            if m == "0" and s == "0":
                running = False
                print("[INFO] 時間切れ")
                continue

            remaining = driver.find_element(
                By.ID, "remaining"
            ).text.strip()

        except Exception as e:
            print("[ERROR]", e)
            time.sleep(0.1)
            continue

        if remaining:
            if remaining != previous:
                print(f"[INPUT] {remaining}")

                pyautogui.write(
                    remaining,
                    interval=interval
                )

                previous = remaining

        else:
            previous = ""

        time.sleep(0.01)

finally:
    driver.quit()
    print("[INFO] 終了")