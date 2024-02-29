#!/usr/bin/python3

import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import zipfile
import re

def scroll(canvas, event):
    if event.num == 5:
        direction = 1 
    elif event.num == 4:
        direction = -1
    canvas.yview_scroll(direction, "units")  

def space_scroll(canvas, event):
    for _ in range(8):
        canvas.yview_scroll(1, "units")
        canvas.update()
        root.after(10)

def shift_space_scroll(canvas, event):
    for _ in range(8):
        canvas.yview_scroll(-1, "units")
        canvas.update()
        root.after(10)

def arrow_up_scroll(canvas, event):
    canvas.yview_scroll(-1, "units")  

def arrow_down_scroll(canvas, event):
    canvas.yview_scroll(1, "units")  

def on_canvas_configure(canvas, loaded_images, total_image_height):
    show_images(canvas, loaded_images, total_image_height)

def get_display_size(img):
    return img.width, img.height

def scrollbar(canvas, total_image_height):
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_image_height))
    scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.yview_moveto(0)

def toggle_listbox():
    new_x = my_listbox.winfo_reqwidth()
    if my_listbox.winfo_ismapped():
        my_listbox.place_forget()
    else:
        my_listbox.place(x=new_x)

def on_listbox_select(event):
    selected_index = my_listbox.curselection()
    if selected_index:
        selected_index = int(selected_index[0])
        load_chapter(root, canvas, files, selected_index)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def load_images_from_zip(zip_file_path):
    image_files = []
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        image_files = [name for name in zip_ref.namelist() if name.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return sorted(image_files, key=natural_sort_key)  

def load_all_images(zip_file_path, image_files):
    loaded_images = []
    total_image_height = 0
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        for image_path in image_files:
            with zip_ref.open(image_path) as img_file:
                img = Image.open(img_file)
                img = img.convert("RGB")
                loaded_images.append(img)
                total_image_height += img.height
    return loaded_images, total_image_height

def show_images(canvas, loaded_images, total_image_height):
    for widget in canvas.winfo_children():
        widget.destroy()

    y_offset = 0
    for img in loaded_images:
        if get_display_size(img)[0] > 1920:
            img.thumbnail((1920, get_display_size(img)[1]), Image.Resampling.LANCZOS)
        else:
            pass
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(canvas, image=photo, bg="#1E1E1E")
        label.image = photo
        canvas.create_image(canvas.winfo_width() // 2, y_offset + img.height // 2, anchor=tk.CENTER, image=photo)
        y_offset += img.height + 1 * 5

    scrollbar(canvas, total_image_height)
    canvas.focus_set()

def load_chapter(root, canvas, files, selected_index):
    global current_file_index
    current_file_index = selected_index
    zip_file_path = files[current_file_index] + ".zip"
    image_files = load_images_from_zip(zip_file_path)
    loaded_images, total_image_height = load_all_images(zip_file_path, image_files)
    on_canvas_configure(canvas, loaded_images, total_image_height)
    root.title(f"Comic Book Reader - {zip_file_path}")


def next_file(root, canvas, files):
    global current_file_index
    current_file_index = (current_file_index + 1) % len(files)
    load_chapter(root, canvas, files, current_file_index)

def previous_file(root, canvas, files):
    global current_file_index
    current_file_index = (current_file_index - 1) % len(files)
    load_chapter(root, canvas, files, current_file_index)


if len(sys.argv) != 2:
    print("Usage: python comic_reader.py <path_to_cbr_file>")
    sys.exit(1)

file_path = os.path.abspath(sys.argv[1])
file_directory = os.path.dirname(file_path)
files = os.listdir(file_directory)
files = [file_directory + "/" + name for name in files]
files = [name.replace(".zip", "") for name in files]
files = sorted(files, key=natural_sort_key)

current_file_index = files.index(file_path.replace(".zip", ""))

zip_file_path = files[current_file_index] + ".zip"

root = tk.Tk()
root.attributes('-zoomed', True)

canvas = tk.Canvas(root, bg="#1E1E1E", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

my_listbox = tk.Listbox(root, selectmode=tk.SINGLE, selectbackground='lightblue', activestyle='none')

for file in files:
    my_listbox.insert(tk.END, "Chapter " + os.path.basename(file).split()[-1])

my_listbox.config(height=min(my_listbox.size(), 20), width=70, font='Helvetica 13')

my_listbox.selection_set(current_file_index)

canvas.bind("<Configure>", lambda event: on_canvas_configure(canvas, loaded_images, total_image_height))
my_listbox.bind('<<ListboxSelect>>', on_listbox_select)

canvas.bind("<Button-4>", lambda event: scroll(canvas, event))  
canvas.bind("<Button-5>", lambda event: scroll(canvas, event))  
root.bind("<space>", lambda event: space_scroll(canvas, event))  
root.bind("<Shift-space>", lambda event: shift_space_scroll(canvas, event))  
root.bind("<Up>", lambda event: arrow_up_scroll(canvas, event))  
root.bind("<Down>", lambda event: arrow_down_scroll(canvas, event))  
root.bind("n", lambda event: next_file(root, canvas, files))  
root.bind("p", lambda event: previous_file(root, canvas, files))  
root.bind("l", lambda event: toggle_listbox())


image_files = load_images_from_zip(zip_file_path)
loaded_images, total_image_height = load_all_images(zip_file_path, image_files)
show_images(canvas, loaded_images, total_image_height)

root.title(f"Comic Book Reader - {zip_file_path}")

root.mainloop()
