#!/usr/bin/python3

from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        if button == mouse.Button.left:
            print('{} at {}'.format('Pressed Left Click', (x, y)))
        else:
            print('{} at {}'.format('Pressed Right Click', (x, y)))

listener = mouse.Listener(on_click=on_click)
listener.start()
listener.join()
