#!/usr/bin/python

import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import zipfile
import re
import json
import time
import requests
from bs4 import BeautifulSoup

class current_file_index:
    def set_current_file_index(self, new_index):
        self.index = new_index

    def return_current_file_index(self):
        return self.index
    
    def add_current_file_index(self, files):
        self.index += 1 % len(files)

    def remove_current_file_index(self, files):
        self.index -= 1 % len(files)

def mouse_scroll(canvas, event, my_listbox):
    if event.num == 5:
        direction = 1 
    elif event.num == 4:
        direction = -1

    if event.widget != my_listbox:
        canvas.yview_scroll(direction, "units")
    else:
        pass
    
    images.show_next_image()

def space_scroll(canvas, event, stop):
    for _ in range(8):
        canvas.yview_scroll(1, "units")
        canvas.update()
        root.after(10)

    images.show_next_image()

def shift_space_scroll(canvas, event):
    for _ in range(8):
        canvas.yview_scroll(-1, "units")
        canvas.update()
        root.after(10)

    images.show_next_image()

def arrow_up_scroll(canvas, event):
    canvas.yview_scroll(-1, "units")  
    images.show_next_image()

def arrow_down_scroll(canvas, event):
    canvas.yview_scroll(1, "units")
    images.show_next_image()

def on_canvas_configure(canvas, total_image_height, name):
    show_images(canvas, total_image_height, name)

def get_display_size(img):
    return img.width, img.height

def toggle_listbox(my_listbox):
    new_x = my_listbox.winfo_reqwidth()
    if my_listbox.winfo_ismapped():
        my_listbox.place_forget()
    else:
        my_listbox.place(x=new_x)

def on_listbox_select(my_listbox, files):
    selected_index = my_listbox.curselection()
    if selected_index:
        selected_index = int(selected_index[0])
        load_chapter(root, canvas, files, selected_index, my_listbox, current_manga)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def load_images_from_zip(zip_file_path):
    image_files = []
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        image_files = [name for name in zip_ref.namelist() if name.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return sorted(image_files, key=natural_sort_key)  

class images():
    def input_loaded_images(self, loaded_images):
        self.total_image_height = 0
        self.image_points = []
        self.loaded_images = loaded_images
        y_offset = 0

        for i in self.loaded_images:
            self.total_image_height += i.height + 5

        for i in self.loaded_images:
            self.image_points.append((i.height / 2 + y_offset) / self.total_image_height)
            y_offset += i.height + 5

    def show_next_image(self):
        while canvas.yview()[1] > self.image_points[0]:
            y_offset = self.current_y_offsety
            try:
                img = self.loaded_images[0]
            except:
                break
            if get_display_size(img)[0] > 1920:
                img.thumbnail((1920, get_display_size(img)[1]), Image.Resampling.LANCZOS)
            else:
                pass
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(canvas, image=photo, bg="#171717")
            label.image = photo
            canvas.create_image(canvas.winfo_width() // 2, self.current_y_offsety + img.height // 2, anchor=tk.CENTER, image=photo)

            y_offset += img.height + 5
            images.input_current_y_offset(y_offset)

            del self.loaded_images[0]
            del self.image_points[0]

    def input_current_y_offset(self, y_offset):
        self.current_y_offsety = y_offset

    def return_current_yoffset(self):
        return self.current_y_offsety

    def return_loaded_images(self):
        return self.loaded_images

    def return_image_height(self):
        return self.total_image_height

    def return_image_points(self):
        return self.image_points

def load_all_images(zip_file_path, image_files):
    loaded_images = []
    total_image_height = 0
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        for image_path in image_files:
            with zip_ref.open(image_path) as img_file:
                img = Image.open(img_file)
                img = img.convert("RGB")
                loaded_images.append(img)
                total_image_height += img.height + 5
    
    images.input_loaded_images(loaded_images)

def show_images(canvas, total_image_height, name):
    for widget in canvas.winfo_children():
        widget.destroy()

    loaded_images = images.return_loaded_images()

    y_offset = 0

    while canvas.winfo_height() > y_offset:
        img = loaded_images[0]
        if get_display_size(img)[0] > 1920:
            img.thumbnail((1920, get_display_size(img)[1]), Image.Resampling.LANCZOS)
        else:
            pass
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(canvas, image=photo, bg="#171717")
        label.image = photo
        canvas.create_image(canvas.winfo_width() // 2, y_offset + img.height // 2, anchor=tk.CENTER, image=photo)
        y_offset += img.height + 5
        images.input_current_y_offset(y_offset)

        del loaded_images[0]

    canvas.update_idletasks()
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_image_height))
    scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    scrollbar.config(command=lambda *args: (images.show_next_image(), canvas.yview(*args)))
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.focus_set()


def load_chapter(root, canvas, files, selected_index, my_listbox, name):
    index_object.set_current_file_index(selected_index)
    current_file_index = index_object.return_current_file_index()
    my_listbox.selection_clear(0, tk.END)
    my_listbox.selection_set(current_file_index)
    zip_file_path = files[current_file_index] + ".zip"
    image_files = load_images_from_zip(zip_file_path)
    load_all_images(zip_file_path, image_files)
    loaded_images = images.return_loaded_images()
    total_image_height = images.return_image_height()
    on_canvas_configure(canvas, total_image_height, name)

    root.title(f"Comic Book Reader - {os.path.splitext(os.path.basename(zip_file_path))[0]}")

    try:
        if data[name]["path"] == zip_file_path and data[name]["last_y_axis"]:
            canvas.yview_moveto(data[name]["last_y_axis"])
            
            y_offset = images.return_current_yoffset()
            image_points = images.return_image_points()
            loaded_images = images.return_loaded_images()

            while canvas.yview()[1] > image_points[0]:
                img = loaded_images[0]
                if get_display_size(img)[0] > 1920:
                    img.thumbnail((1920, get_display_size(img)[1]), Image.Resampling.LANCZOS)
                else:
                    pass
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(canvas, image=photo, bg="#171717")
                label.image = photo
                canvas.create_image(canvas.winfo_width() // 2, y_offset + img.height // 2, anchor=tk.CENTER, image=photo)

                y_offset += img.height + 5
                images.input_current_y_offset(y_offset)

                del loaded_images[0]
                del image_points[0]

        else:
            canvas.yview_moveto(0)
    except:
        canvas.yview_moveto(0)


    try:
        if zip_file_path != data[name]:
            with open(json_file_path, "w") as file:
                data[name]["path"] = zip_file_path
                json.dump(data, file, indent=4)
    except:
        pass

def next_file(root, canvas, files, my_listbox):
    index_object.add_current_file_index(files)
    current_file_index = index_object.return_current_file_index()

    load_chapter(root, canvas, files, current_file_index, my_listbox, current_manga)

def previous_file(root, canvas, files, my_listbox):
    index_object.remove_current_file_index(files)
    current_file_index = index_object.return_current_file_index()
    load_chapter(root, canvas, files, current_file_index, my_listbox, current_manga)

def on_listbox_mousewheel(event):
    return 'break'

current_manga = None
index_object = current_file_index()
images = images()

def load_manga(manga, name):
    global current_manga
    current_manga = name
    file_path = os.path.abspath(manga)
    file_directory = os.path.dirname(file_path)
    files = get_files(file_directory)

    index_object.set_current_file_index(files.index(file_path.replace(".zip", "")))
    current_file_index = index_object.return_current_file_index()

    zip_file_path = files[current_file_index] + ".zip"
    
    my_listbox = tk.Listbox(root, selectmode=tk.SINGLE, selectbackground='lightblue', activestyle='none')

    for file in files:
        my_listbox.insert(tk.END, "Chapter " + os.path.basename(file).split()[-1])

    my_listbox.config(height=min(my_listbox.size(), 20), width=70, font='Helvetica 13')
    my_listbox.selection_set(current_file_index)
    my_listbox.bind('<<ListboxSelect>>', lambda event: on_listbox_select(my_listbox, files))

    load_chapter(root, canvas, files, current_file_index, my_listbox, name)

    root.unbind("<Button-1>")
    root.bind("<Button-4>", lambda event: mouse_scroll(canvas, event, my_listbox))  
    root.bind("<Button-5>", lambda event: mouse_scroll(canvas, event, my_listbox))  

    root.bind("<space>", lambda event: space_scroll(canvas, event, False))  
    root.bind("<KeyPress-space>", lambda event: space_scroll(canvas, event, True))
    root.bind("<Shift-space>", lambda event: shift_space_scroll(canvas, event))  
    root.bind("<Up>", lambda event: arrow_up_scroll(canvas, event))  
    root.bind("<Down>", lambda event: arrow_down_scroll(canvas, event))  
    root.bind("n", lambda event: next_file(root, canvas, files, my_listbox))
    root.bind("p", lambda event: previous_file(root, canvas, files, my_listbox))  
    root.bind("l", lambda event: toggle_listbox(my_listbox))
    root.bind("<Escape>", lambda event: home(False, my_listbox)) 

def load_image(image_path, width):
    try:
        jpeg_image = Image.open(image_path)
        jpeg_image = jpeg_image.resize((250, width))
        png_image = jpeg_image.convert("RGBA")
        return ImageTk.PhotoImage(png_image)
    except:
        pass

path = os.path.dirname(os.path.realpath(__file__))
json_file_path = os.path.join(path, "data.json")

if os.path.isfile(json_file_path):
    pass
else:
    open(json_file_path, "w").close()

if os.path.isdir(os.path.join(path, "mangas")):
    pass
else:
    os.mkdir(os.path.join(path, "mangas"))

mangas = os.listdir(os.path.join(path, "mangas"))

def get_files(manga_path):
    files = os.listdir(manga_path)
    files = [file for file in files if file.endswith(".zip")]
    files = [os.path.join(manga_path, file) for file in files]
    files = [name.replace(".zip", "") for name in files]
    files = sorted(files, key=natural_sort_key)

    return files


def load_pressed(button):
    name = button.cget("text")
    files = get_files((os.path.join(path, "mangas", name)))

    try:
        location = data[name]
        if location:
            load_manga(data[name]["path"], name)
    except: 
        with open(json_file_path, "w") as file:
            data[name] = {"path": files[0] + ".zip"}
            json.dump(data, file, indent=4)
            load_manga(files[0] + ".zip", name)

def save_y_axis_position():
    if canvas is not None:
        y = canvas.yview()[0]
        if current_manga:
            data[current_manga]["last_y_axis"] = y
            with open(json_file_path, "w") as file:
                json.dump(data, file, indent=4)
        root.destroy()

class home:
    def __init__(self, first_time, my_listbox):
        if not first_time:
            y = canvas.yview()[0]
            data[current_manga]["last_y_axis"] = y
            images.return_loaded_images().clear()
            with open(json_file_path, "w") as file:
                json.dump(data, file, indent=4)
            for widget in canvas.winfo_children():
                widget.destroy()
            for binding in ["<space>", "<Shift-space>", "<Up>", "<Down>", "n", "p","l", "<Escape>", "<Button-4>", "<Button-5>"]:
                root.unbind(binding)
    
            if my_listbox:
                my_listbox.destroy()

        root.bind("<Button-4>", lambda event: self.home_scroll(canvas, event)) 
        root.bind("<Button-5>", lambda event: self.home_scroll(canvas, event))
        root.bind("<Button-1>", self.handle_click_outside_entry)
        
        self.scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.search_bar = tk.Entry(canvas, width=50, font=("arial", 24))
        self.search_bar.bind("<KeyRelease>", lambda event: self.search_result())
        self.search_bar.pack(pady=20)

        self.download_button = tk.Button(canvas, text="+", font=("arial", 18))
        self.download_button.place(x=self.search_bar.winfo_reqwidth()*1.5 + 70, y=20)
        self.download_button.config(command=self.download_menu)

        button_frame = tk.Frame(canvas, bg="#171717")
        button_frame.pack(side=tk.TOP)
        self.button_frame = button_frame

        self.show_mangas(mangas, icons)
        
        canvas.update_idletasks()
        
        total_height = sum(widget.winfo_reqheight() for widget in canvas.winfo_children())

        canvas.configure(yscrollcommand=self.scrollbar.set)
        canvas.config(scrollregion=(0, 0, canvas.winfo_reqwidth(), total_height))
        
        canvas.create_window((self.button_frame.winfo_reqwidth() / 5 + self.scrollbar.winfo_reqwidth() * 2, self.search_bar.winfo_reqheight() + 21), window=button_frame, anchor="nw")

        root.title(f"Comic Book Reader")
    
    def home_scroll(self, canvas, event):
        if event.num == 5:
            direction = 1 
        elif event.num == 4:
            direction = -1

        canvas.yview_scroll(direction, "units")

    def search_menu_scroll(self,event):
        if event.num == 5:
            direction = 1 
        elif event.num == 4:
            direction = -1

        if event.widget == canvas:
            canvas.yview_scroll(direction, "units")
        else:
            self.canvas.yview_scroll(direction, "units")

    def download_menu(self):
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            self.menu.destroy()
            root.bind("<Button-4>", lambda event: self.home_scroll(canvas, event)) 
            root.bind("<Button-5>", lambda event: self.home_scroll(canvas, event))
            return
        
        root.bind("<Button-4>", lambda event: self.search_menu_scroll(event)) 
        root.bind("<Button-5>", lambda event: self.search_menu_scroll(event))

        self.menu = tk.Frame(canvas, bg="#2E2E2E")
        self.menu.place(relx=0.5, rely=0.45, anchor="center")

        self.menu_search_bar = tk.Entry(self.menu, width=50, font=("arial", 15))
        self.menu_search_bar.pack(pady=(30,70), padx=200)
        self.menu_search_bar.focus_set()
        self.menu_search_bar.bind("<Return>", self.manga_search)

        self.canvas = tk.Canvas(self.menu, bg="#2E2E2E", height=400, width=500, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.menu_button_frame = tk.Frame(self.menu, bg="#2E2E2E", highlightthickness=0)
        self.canvas.create_window((0, 0), window=self.menu_button_frame, anchor="nw")

        self.menu_scrollbar = tk.Scrollbar(self.menu, orient="vertical", command=self.canvas.yview)
        self.menu_scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.menu_scrollbar.set)

    def manga_search(self, event):
        manga_to_search = self.menu_search_bar.get()
        manga_to_search = manga_to_search.replace(" ", "_")
        page = 1
        url = "https://manganato.com/search/story/" + manga_to_search + "?page=" + str(page)
        r = requests.get(url)
        r = BeautifulSoup(r.text, 'html.parser')
        
        try:
            results = r.find(class_="panel-search-story").find_all("div")
        except:
            print("cant find the specified manga/manhwa/manhua")
        
        titles = []
        urls = []
        last_chapter = []
        len_biggest_chapter = 0

        for result in results:
            titles.append(result.h3.text.strip())
            urls.append(result.a["href"])
            last_chapter.append(result.find(class_="item-chapter a-h text-nowrap")["href"])
            if len(result.find(class_="item-chapter a-h text-nowrap")["href"].split("-")[-1]) > len_biggest_chapter:
                len_biggest_chapter = len(result.find(class_="item-chapter a-h text-nowrap")["href"].split("-")[-1])
                biggest_chapter = result.find(class_="item-chapter a-h text-nowrap")["href"].split("-")[-1]

        titles = list(dict.fromkeys(titles))
        urls = list(dict.fromkeys(urls))
        last_chapters = list(dict.fromkeys(last_chapter))

        len_biggest_chapter = tk.Button(self.menu_button_frame, text=biggest_chapter, fg="white", font=("Arial Bold", 15), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)
        len_biggest_chapter = len_biggest_chapter.winfo_reqwidth()

        for i,(text,last_chapter) in enumerate(zip(titles, last_chapters)):
            button = tk.Button(self.menu_button_frame, text=text, fg="white", font=("Arial Bold", 15), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)
            last_chapter_button = tk.Button(self.menu_button_frame, text=last_chapter.split("-")[-1], fg="white", font=("Arial Bold", 15), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)

            while (button.winfo_reqwidth() + len_biggest_chapter) > self.canvas.winfo_width():
                text = text[:-1]
                button = tk.Button(self.menu_button_frame, text=text[:-4] + "....", fg="white", font=("Arial Bold", 15), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)

            button.grid(row=i, column=0, sticky="w")
            last_chapter_button.grid(row=i, column=1, sticky="e")

        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def handle_click_outside_entry(self, event):
        try:
            if event.widget != self.search_bar and event.widget != self.search_menu:
                self.button_frame.focus_set()
        except:
            pass

    def show_mangas(self, mangas, icons):
        buttons_per_row = 5

        for i, (name, icon) in enumerate(zip(mangas, icons)):
            button_container = tk.Frame(self.button_frame, bg="#171717")
            button_container.grid(row=i // buttons_per_row, column=i % buttons_per_row)

            manga_button = tk.Button(button_container, image=icon, text=name, borderwidth=0, highlightthickness=0)
            manga_button.config(command=lambda button=manga_button: load_pressed(button))
            manga_button.pack(side=tk.TOP, padx=5, pady=20)

            text_label = tk.Label(button_container, text=f"{name}", bg="#171717", fg="#ffffff", font="Helvetica 13 bold")
            text_label.pack(side=tk.TOP)

            if name in data:
                last_chapter = os.path.splitext(os.path.basename(data[name]["path"]))[0].split()[-1]
                text_label2 = tk.Label(button_container, text=f"Last Chapter: {last_chapter}", bg="#171717", fg="#ffffff", font="Helvetica 13 bold")
                text_label2.pack(side=tk.TOP)
            else:
                text_label2 = tk.Label(button_container, text=f"Last Chapter: 0", bg="#171717", fg="#ffffff", font="Helvetica 13 bold")
                text_label2.pack(side=tk.TOP)

            while text_label.winfo_reqwidth() > manga_button.winfo_reqwidth():
                name = name[:-1]
                text_label.config(text=name[:len(name) - 4] + "....")
    
    def search_result(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        results = [manga for manga in mangas if self.search_bar.get() in manga.lower()]

        for i, name in enumerate(results):
            button_container = tk.Frame(self.button_frame, bg="#171717")
            button_container.grid(row=i // 5, column=i % 5)

            manga_button = tk.Button(button_container, image=icons[mangas.index(name)], text=name, borderwidth=0, highlightthickness=0)
            manga_button.config(command=lambda button=manga_button: load_pressed(button))
            manga_button.pack(side=tk.TOP, padx=5, pady=20)

            text_label = tk.Label(button_container, text=f"{name}", bg="#171717", fg="#ffffff", font="Helvetica 13 bold")
            text_label.pack(side=tk.TOP)

            if name in data:
                last_chapter = os.path.splitext(os.path.basename(data[name]["path"]))[0].split()[-1]
                text_label2 = tk.Label(button_container, text=f"Last Chapter: {last_chapter}", bg="#171717", fg="#ffffff", font="Helvetica 13 bold")
                text_label2.pack(side=tk.TOP)
            else:
                text_label2 = tk.Label(button_container, text=f"Last Chapter: 0", bg="#171717", fg="#ffffff", font="Helvetica 13 bold")
                text_label2.pack(side=tk.TOP)

            while text_label.winfo_reqwidth() > manga_button.winfo_reqwidth():
                name = name[:-1]
                text_label.config(text=name[:len(name) - 4] + "....")
        canvas.config(scrollregion=self.button_frame.bbox("all"))
        canvas.create_window((self.button_frame.winfo_reqwidth() / 5 + self.scrollbar.winfo_reqwidth() * 2, self.search_bar.winfo_reqheight() + 21), window=self.button_frame, anchor="nw")

        #print(results, end="\r")


root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", save_y_axis_position)
if os.name == "nt":
    root.state('zoomed')
else:
    root.attributes('-zoomed', True)

canvas = tk.Canvas(root, bg="#171717", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

try:
    with open(json_file_path, "r") as file:
        data = json.load(file)
except json.decoder.JSONDecodeError:
    data = {}

icons = [load_image(os.path.join(path, "mangas", name, "icon.jpg"), canvas.winfo_reqwidth()) for name in mangas]

home(True, None)
root.mainloop()

for name in data:
    if name not in mangas:
        del data[name]
