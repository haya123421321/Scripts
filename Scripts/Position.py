#!/usr/bin/python3

from pynput import mouse
import argparse
import time

search_parser = argparse.ArgumentParser(description="A simple python auto clicker on specific positions")
search_parser.add_argument("-o", metavar="<file>", help="The python output file")
search_parser.add_argument("-t", metavar="<time>", help="The time between every click")
search_parser.add_argument("-r", help="Real time checking how many seconds between every click you make", action="store_true")

args = search_parser.parse_args()

positions = []
seconds = []

last_click_time = time.time()

def on_click(x, y, button, pressed):
    global last_click_time
    if pressed:
        if button == mouse.Button.left:
            current_time = time.time()
            time_since_last_click_seconds = current_time - last_click_time
            time_since_last_click_seconds = "".join(str(time_since_last_click_seconds).split(".")[0] + "." + str(time_since_last_click_seconds).split(".")[1][:2])

            print('{} at {}'.format('Pressed Left Click', (x, y)))
            positions.append((x,y))
            seconds.append(time_since_last_click_seconds)
            last_click_time = current_time

try:
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
except KeyboardInterrupt:
    if args.o is not None:
        with open(str(args.o), "a") as file:
            file.write("import pyautogui\nimport time\n\n")
            file.write(f"positions = {positions}\n")

            if args.r:
                file.write(f"seconds = {seconds}")

            file.write("\n\nwhile True:\n")

            if args.r:
                file.write("    for i,t in zip(positions, seconds):\n")
            else:
                file.write("    for i in positions:\n")

            file.write("        pyautogui.click(i)")

            if args.t is not None:
                file.write(f"\n        time.sleep({args.t})")
            elif args.r:
                file.write(f"\n        time.sleep(float(t))")
