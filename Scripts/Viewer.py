#!/usr/bin/python3

import sys
import zipfile
import tkinter as tk
from PIL import Image, ImageTk

class ComicBookReader:
    def __init__(self, root, zip_file_path):
        self.root = root
        self.root.title("Comic Book Reader")

        self.zip_file_path = zip_file_path
        
        self.total_image_height = 0

        self.init_ui()
        self.load_images_from_zip()
        self.load_all_images()
        self.show_images()

    def init_ui(self):
        self.canvas = tk.Canvas(self.root, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.on_canvas_configure) 

        self.canvas.bind("<Button-4>", self.scroll)  # Scroll up
        self.canvas.bind("<Button-5>", self.scroll)  # Scroll down
        self.root.bind("<space>", self.space_scroll)  # Bind spacebar to scroll down
        self.root.bind("<Shift-space>", self.shift_space_scroll)  # Bind Shift + spacebar to scroll up
        self.root.bind("<Up>", self.arrow_up_scroll)  # Bind arrow up key to scroll up
        self.root.bind("<Down>", self.arrow_down_scroll)  # Bind arrow down key to scroll down

    def scroll(self, event):
        direction = 1 if event.num == 5 else -1  # Determine scroll direction
        self.canvas.yview_scroll(direction, "units")  # Scroll by 1 unit up or down
    
    def space_scroll(self, event):
        self.canvas.yview_scroll(8, "units")  

    def shift_space_scroll(self, event):
        self.canvas.yview_scroll(-8, "units")  # Scroll up by 3 units with Shift + spacebar

    def arrow_up_scroll(self, event):
        self.canvas.yview_scroll(-1, "units")  # Scroll up by 1 unit with arrow up key

    def arrow_down_scroll(self, event):
        self.canvas.yview_scroll(1, "units")  # Scroll down by 1 unit with arrow down key


    def load_images_from_zip(self):
        self.image_files = []
        with zipfile.ZipFile(self.zip_file_path, "r") as zip_ref:
            self.image_files = [name for name in zip_ref.namelist() if name.lower().endswith(('.jpg', '.jpeg', '.png'))]
        self.image_files = sorted(self.image_files, key=self.natural_sort_key)  # Sort image files

    def load_all_images(self):
        self.loaded_images = []
        self.total_image_height = 0
        with zipfile.ZipFile(self.zip_file_path, "r") as zip_ref:
            for image_path in self.image_files:
                with zip_ref.open(image_path) as img_file:
                    img = Image.open(img_file)
                    img = img.convert("RGB")
                    self.loaded_images.append(img)
                    self.total_image_height += img.height

    def show_images(self):
        y_offset = 0
        for img in self.loaded_images:
            if self.get_display_size(img)[0] > 1920:
                img.thumbnail((1920,self.get_display_size(img)[1]), Image.Resampling.LANCZOS)
            else:
                pass
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(self.canvas, image=photo, bg="#1E1E1E")
            label.image = photo
            self.canvas.create_image(self.canvas.winfo_width() // 2, y_offset + img.height // 2, anchor=tk.CENTER, image=photo)
            y_offset += img.height + 1 * 5
        self.canvas.config(scrollregion=(0, 0, self.canvas.winfo_width(), self.total_image_height))

    def on_canvas_configure(self, event):
        self.canvas.delete("all")
        self.show_images()
        self.canvas.yview_moveto(0)

    def get_display_size(self, img):
        return img.width, img.height

    def natural_sort_key(self, s):
        import re
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)] 

def main():
    if len(sys.argv) != 2:
        print("Usage: python comic_reader.py <path_to_cbr_file>")
        sys.exit(1)

    root = tk.Tk()
    root.attributes('-zoomed', True)
    zip_file_path = sys.argv[1]
    reader = ComicBookReader(root, zip_file_path)
    root.mainloop()

if __name__ == "__main__":
    main()
