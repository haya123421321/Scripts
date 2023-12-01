import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import zipfile
import re

def scroll(canvas, event):
    direction = 1 if event.num == 5 else -1  # Determine scroll direction
    canvas.yview_scroll(direction, "units")  # Scroll by 1 unit up or down

def space_scroll(canvas, event):
    canvas.yview_scroll(8, "units")

def shift_space_scroll(canvas, event):
    canvas.yview_scroll(-8, "units")  # Scroll up by 3 units with Shift + spacebar

def arrow_up_scroll(canvas, event):
    canvas.yview_scroll(-1, "units")  # Scroll up by 1 unit with arrow up key

def arrow_down_scroll(canvas, event):
    canvas.yview_scroll(1, "units")  # Scroll down by 1 unit with arrow down key

def on_canvas_configure(canvas, loaded_images, total_image_height):
    canvas.delete("all")
    show_images(canvas, loaded_images, total_image_height)
    canvas.yview_moveto(0)

def get_display_size(img):
    return img.width, img.height

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def load_images_from_zip(zip_file_path):
    image_files = []
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        image_files = [name for name in zip_ref.namelist() if name.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return sorted(image_files, key=natural_sort_key)  # Sort image files

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
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_image_height))


def next_file(root, canvas, files):
    global current_file_index
    current_file_index = (current_file_index + 1)
    zip_file_path = files[current_file_index] + ".zip"
    image_files = load_images_from_zip(zip_file_path)
    loaded_images, total_image_height = load_all_images(zip_file_path, image_files)
    on_canvas_configure(canvas, loaded_images, total_image_height)
    root.title(f"Comic Book Reader - {zip_file_path}")
    print(current_file_index)


def main():
    if len(sys.argv) != 2:
        print("Usage: python comic_reader.py <path_to_cbr_file>")
        sys.exit(1)
    global current_file_index

    file_directory = os.path.abspath(sys.argv[1])
    file_directory = os.path.dirname(file_directory)
    files = os.listdir(file_directory)
    files = [name.replace(".zip", "") for name in files]
    files = sorted(files, key=natural_sort_key)

    current_file_index = files.index(os.path.basename(sys.argv[1]).replace(".zip", ""))

    zip_file_path = files[current_file_index] + ".zip"

    root = tk.Tk()
    root.attributes('-zoomed', True)

    canvas = tk.Canvas(root, bg="#1E1E1E", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda event: on_canvas_configure(canvas, loaded_images, total_image_height))

    canvas.bind("<Button-4>", lambda event: scroll(canvas, event))  # Scroll up
    canvas.bind("<Button-5>", lambda event: scroll(canvas, event))  # Scroll down
    root.bind("<space>", lambda event: space_scroll(canvas, event))  # Bind spacebar to scroll down
    root.bind("<Shift-space>", lambda event: shift_space_scroll(canvas, event))  # Bind Shift + spacebar to scroll up
    root.bind("<Up>", lambda event: arrow_up_scroll(canvas, event))  # Bind arrow up key to scroll up
    root.bind("<Down>", lambda event: arrow_down_scroll(canvas, event))  # Bind arrow down key to scroll down
    root.bind("n", lambda event: next_file(root, canvas, files))  # Bind 'n' key to go to the next file


    image_files = load_images_from_zip(zip_file_path)
    loaded_images, total_image_height = load_all_images(zip_file_path, image_files)
    show_images(canvas, loaded_images, total_image_height)

    root.title(f"Comic Book Reader - {zip_file_path}")

    root.mainloop()

if __name__ == "__main__":
    main()
