#!/usr/bin/python

import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import zipfile
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import shutil

class current_file_index:
    def set_current_file_index(self, new_index):
        self.index = new_index

    def return_current_file_index(self):
        return self.index
    
    def add_current_file_index(self, files):
        self.index += 1 % len(files)

    def remove_current_file_index(self, files):
        self.index -= 1 % len(files)

def manga_mouse_scroll(canvas, event, my_listbox):
    if event.num == 5:
        direction = 1 
    elif event.num == 4:
        direction = -1

    if event.widget != my_listbox:
        canvas.yview_scroll(direction, "units")
    else:
        pass
    
    images.show_next_image()

def main_scroll(canvas, event):
    if event.num == 5:
        direction = 1 
    elif event.num == 4:
        direction = -1
    canvas.yview_scroll(direction, "units")

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
    root.bind("<Button-4>", lambda event: manga_mouse_scroll(canvas, event, my_listbox))  
    root.bind("<Button-5>", lambda event: manga_mouse_scroll(canvas, event, my_listbox))  

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

        keys_to_delete = []
        for name in data:
            if name not in mangas:
                keys_to_delete.append(name)
       
        if len(keys_to_delete) >= 1:
            for key in keys_to_delete:
                del data[key]
            try:
                with open(json_file_path, "w") as file:
                    json.dump(data, file, indent=4)
            except Exception as e:
                print(f"Error while saving JSON file: {e}")

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

        root.bind("<Button-4>", lambda event: main_scroll(canvas, event)) 
        root.bind("<Button-5>", lambda event: main_scroll(canvas, event))
        root.bind("<Button-1>", self.handle_click_outside_entry)
        
        self.scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.search_bar = tk.Entry(canvas, width=50, font=("arial", 26))
        self.search_bar.bind("<KeyRelease>", lambda event: self.search_result())
        self.search_bar.pack(pady=20)
        root.update()
        print(self.search_bar.winfo_x())

        self.Plus_image = Image.open(os.path.join(path,"assets", "add_button.png"))
        self.Plus_image = self.Plus_image.resize((50,50))
        self.photoImg = ImageTk.PhotoImage(self.Plus_image)

        self.download_button = tk.Button(canvas, text="+", font=("arial", 18), image=self.photoImg, bg="#171717", borderwidth=0, highlightthickness=0)
        self.download_button.place(x=self.search_bar.winfo_x() + self.search_bar.winfo_width() + 20, y=15)
        self.download_button.config(command=self.download_menu)

        button_frame = tk.Frame(canvas, bg="#171717")
        button_frame.pack(side=tk.TOP)
        self.button_frame = button_frame

        self.icon_photo_img = ""
        self.icons = []
        for name in mangas:
            icon = os.path.join(path, "mangas", name, "icon.jpg")
            if os.path.exists(icon):
                self.icons.append(load_image(icon, icons_height))
            else:
                if isinstance(self.icon_photo_img, ImageTk.PhotoImage):
                    self.icons.append(self.icon_photo_img)
                else:
                    self.No_icon_icon = Image.open(os.path.join(path, "assets", "No_icon.jpg"))
                    self.icon_photo_img = ImageTk.PhotoImage(self.No_icon_icon)
                    self.icons.append(self.icon_photo_img)

        self.show_mangas(mangas, self.icons)
        self.removed_manga = []
        
        canvas.update_idletasks()
        
        total_height = sum(widget.winfo_reqheight() for widget in canvas.winfo_children())

        canvas.configure(yscrollcommand=self.scrollbar.set)
        canvas.config(scrollregion=(0, 0, canvas.winfo_reqwidth(), total_height))
        
        canvas.create_window((self.button_frame.winfo_reqwidth() / 5 + self.scrollbar.winfo_reqwidth() * 2, self.search_bar.winfo_reqheight() + 21), window=button_frame, anchor="nw")
        # TEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEST

        #self.download_menu()
        #canvas.update_idletasks()
        #self.manga_search("solo")
        # TEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEST

        root.title(f"Comic Book Reader")
    
    def home_scroll(self, canvas, event):
        if event.num == 5:
            direction = 1 
        elif event.num == 4:
            direction = -1

        canvas.yview_scroll(direction, "units")

    def self_canvas_scroll(self,event):
        if event.num == 5:
            direction = 1 
        elif event.num == 4:
            direction = -1

        self.canvas.yview_scroll(direction, "units")

    def download_menu(self):
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            self.menu.destroy()
            root.bind("<Button-4>", lambda event: main_scroll(canvas, event)) 
            root.bind("<Button-5>", lambda event: main_scroll(canvas, event))
            try:
                if self.info_canvas.winfo_exists():
                    self.info_canvas.destroy()
            except:
                pass
            return

        root.bind("<Button-4>", lambda event: main_scroll(self.canvas, event)) 
        root.bind("<Button-5>", lambda event: main_scroll(self.canvas, event))

        self.menu = tk.Frame(canvas, bg="#2E2E2E")
        self.menu.place(relx=0.5, rely=0.45, anchor="center")

        self.menu_search_bar = tk.Entry(self.menu, width=40, font=("arial", 20))
        self.menu_search_bar.pack(pady=(30,70), padx=200)
        self.menu_search_bar.focus_set()
        self.menu_search_bar.bind("<Return>", lambda event: self.manga_search(self.menu_search_bar.get()))

        self.canvas = tk.Canvas(self.menu, bg="#2E2E2E", height=400, width=500, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.menu_button_frame = tk.Frame(self.menu, bg="#2E2E2E", highlightthickness=0)
        self.canvas.create_window((0, 0), window=self.menu_button_frame, anchor="nw")

        self.menu_scrollbar = tk.Scrollbar(self.menu, orient="vertical", command=self.canvas.yview)
        self.menu_scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.menu_scrollbar.set)

    def manga_search(self, promt):
        for widget in self.menu_button_frame.winfo_children():
            widget.destroy()
        
        manga_to_search = promt
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
            try:
                last_chapter.append(result.find(class_="item-chapter a-h text-nowrap")["href"])
            except:
                last_chapter.append(f"{result.a['href']}-0")
                continue

            if len(result.find(class_="item-chapter a-h text-nowrap")["href"].split("-")[-1]) > len_biggest_chapter:
                len_biggest_chapter = len(result.find(class_="item-chapter a-h text-nowrap")["href"].split("-")[-1])
                biggest_chapter = result.find(class_="item-chapter a-h text-nowrap")["href"].split("-")[-1]

        self.titles = list(dict.fromkeys(titles))
        self.urls = list(dict.fromkeys(urls))
        last_chapters = list(dict.fromkeys(last_chapter))

        font = 20

        len_biggest_chapter = tk.Label(self.canvas, text=biggest_chapter, fg="white", font=("Arial Bold", font), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)
        len_biggest_chapter = len_biggest_chapter.winfo_reqwidth()

        for i,(text,last_chapter) in enumerate(zip(self.titles, last_chapters)):
            button = tk.Button(self.menu_button_frame, text=text, fg="white", font=("Arial Bold", font), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0, anchor="w")
            button.config(command=lambda button=button: self.manga_info(button))
            last_chapter_button = tk.Label(self.menu_button_frame, text=last_chapter.split("-")[-1], fg="white", font=("Arial Bold", font), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)

            while (button.winfo_reqwidth() + len_biggest_chapter + self.menu_scrollbar.winfo_width()) > self.canvas.winfo_width():
                text = text[:-1]
                button = tk.Button(self.menu_button_frame, text=text[:-4] + "....", fg="white", font=("Arial Bold", font), bg="#2E2E2E", bd=0, highlightthickness=0, borderwidth=0)

            button.grid(row=i, column=0, sticky="we")
            last_chapter_button.grid(row=i, column=1, sticky="e")

        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def manga_info(self, button):
        self.title = button.cget("text")
        index = self.titles.index(self.title)

        r = requests.get(self.urls[index])
        soup = BeautifulSoup(r.text, "html.parser")

        author = soup.find(class_="variations-tableInfo").find_all("tr")[1].find(class_="table-value").text.strip()
        status = soup.find(class_="variations-tableInfo").find_all("tr")[2].find(class_="table-value").text.strip()
        genres = soup.find(class_="variations-tableInfo").find_all("tr")[3].find(class_="table-value").text.strip()
        try:
            all_chapters = soup.find(class_="row-content-chapter").find_all("li")
            self.chapterss = [chapter.a["href"] for chapter in all_chapters]
        except:
            self.chapterss = []
            pass

        self.icon = soup.find(class_="info-image").img["src"]

        self.info_canvas = tk.Canvas(canvas, bg="#2E2E2E", highlightthickness=0, height=self.menu.winfo_height(), width=self.menu.winfo_width())
        self.info_canvas.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        
        root.bind("<Button-4>", lambda event: main_scroll(self.info_canvas, event)) 
        root.bind("<Button-5>", lambda event: main_scroll(self.info_canvas, event))
        
        info_frame = tk.Frame(self.info_canvas, bg="#2E2E2E")
        self.info_canvas.create_window((0, 0), window=info_frame, anchor="nw")

        download_all_button = tk.Button(info_frame, text="Download All", padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", anchor="w")
        download_all_button.config(command=lambda: Thread(target=self.download_single, args=(self.chapterss[::-1],)).start())
        download_all_button.pack(anchor="e", pady=15, padx=10)

        title_label = tk.Label(info_frame, text=self.title, padx=15, pady=15, font=("Helvetica bold", 25), bg="#2E2E2E", fg="white")
        author_label = tk.Label(info_frame, text="Author:      " + author, padx=10, pady=5, font=("Helvetica", 17), bg="#2E2E2E", fg="white")
        status_label = tk.Label(info_frame, text="Status:       " + status, padx=10, pady=5, font=("Helvetica", 17), bg="#2E2E2E", fg="white")
        genres_label = tk.Label(info_frame, text="Genres:     " + genres, padx=10, pady=5, font=("Helvetica", 17), bg="#2E2E2E", fg="white")

        title_label.pack(anchor="w")
        author_label.pack(anchor="w")
        status_label.pack(anchor="w")
        genres_label.pack(anchor="w")

        chapters_frame = tk.Frame(info_frame, bg="#2E2E2E", highlightbackground="white", highlightthickness=2, bd=0)
        chapters_frame.pack(side="left", pady=(30,0), fill="both", expand=True)

        Chapter_name = tk.Label(chapters_frame, text="Chapter name" + " "*97, padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", anchor="w", highlightthickness=2, bd=0)
        View = tk.Label(chapters_frame, text="Views  ", padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", highlightthickness=2, bd=0)
        Uploaded = tk.Label(chapters_frame, text="Uploaded", padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", highlightthickness=2, bd=0)

        Chapter_name.grid(row=0, column=0, sticky="w")
        View.grid(row=0, column=1, sticky="e")
        Uploaded.grid(row=0, column=2, sticky="e")

        if len(self.chapterss) > 1:
            for i,chapter in enumerate(all_chapters):
                chapter_button = tk.Button(chapters_frame, text=chapter.a.text, padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", anchor="w", highlightthickness=0, borderwidth=0)
                chapter_button.config(command=lambda i=i: Thread(target=self.download_single, args=([self.chapterss[i]],)).start())
                chapter_button.grid(row=i + 1, column=0, sticky="we")

                view_button = tk.Label(chapters_frame, text=chapter.span.text, padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", anchor="w", highlightthickness=0, borderwidth=0)
                view_button.grid(row=i + 1, column=1, sticky="e")

                uploaded_button = tk.Label(chapters_frame, text=chapter.find(class_="chapter-time text-nowrap").text, padx=10, pady=5, font=("Helvetica bold", 17), bg="#2E2E2E", fg="white", anchor="w", highlightthickness=0, borderwidth=0)
                uploaded_button.grid(row=i + 1, column=2, sticky="e")

        scrollbar = tk.Scrollbar(self.info_canvas, orient="vertical", command=self.info_canvas.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor=tk.NE)

        self.info_canvas.configure(yscrollcommand=scrollbar.set)

        info_frame.update_idletasks()
        self.info_canvas.config(scrollregion=self.info_canvas.bbox("all"))

    def download_single(self, urls):
        num_digits = len(str(len(self.chapterss)))
        os.makedirs(os.path.join(path, "mangas", self.title), exist_ok=True) 

        if os.path.isfile(os.path.join(path, "mangas", self.title, "icon.jpg")):
            pass
        else:
            r = requests.get(self.icon)
            open(os.path.join(path, "mangas", self.title, "icon.jpg"), "wb").write(r.content)

        mangas = os.listdir(os.path.join(path, "mangas"))
        
        self.icons = [load_image(os.path.join(path, "mangas", name, "icon.jpg"), icons_height) for name in mangas]
        self.show_mangas(mangas, self.icons)


        self.image = os.path.join(path, "mangas", self.title, "icon.jpg")
        
        jpeg_image = Image.open(self.image)
        jpeg_image = jpeg_image.resize((250, 100))

        png_image = jpeg_image.convert("RGBA")
        self.image = ImageTk.PhotoImage(png_image)

        progress_button = tk.Button(canvas, text=f"{self.title}\n0%", width=20, borderwidth=0, highlightthickness=0, font=("arial", 18), bg="red", anchor="center")
        progress_button.pack(anchor="e", padx=20, pady=5)

        s = requests.Session()
        
        progress = 0
        what_to_go_up_with = 100 / len(urls)
        check_with_this = 25
        colors = ["yellow", "dark green", "light green", "light green"]

        for url in urls:
            chapter_name  = self.title + " " + url.split("/")[4].split("-")[1].zfill(num_digits)
            if os.path.isfile(os.path.join(path, "mangas", self.title, chapter_name + ".zip")):
                progress += what_to_go_up_with
                progress_button.config(text=f"{self.title}\n{int(progress)}%")
                continue

            os.makedirs(os.path.join(path, "mangas", self.title, chapter_name), exist_ok=True)

            q = Queue()
            names = Queue()
            r = s.get(url)
            r = BeautifulSoup(r.text, 'html.parser')

            links = r.find(class_="container-chapter-reader").find_all("img")
            headers = {
            "DNT" : "1",
            "Referer" : "https://readmanganato.com/",
            "sec-ch-ua-mobile" : "?0",
            "sec-ch-ua-platform" : "Linux",
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            }

            for url in links:
                q.put(url["src"])
            for name in range(len(links)):
                names.put(name)

            def downloadlink():
                while not q.empty():
                    link = q.get()
                    name = names.get()
                    r = s.get(link, headers=headers, stream=True)
                    open(os.path.join(path, "mangas", self.title, chapter_name, str(name)) + ".jpg", "wb").write(r.content)
                    q.task_done()

            def download_all():
                num_threads = min(20, len(links))
                for i in range(num_threads):
                    t_worker = Thread(target=downloadlink)
                    t_worker.start()
                q.join()

            download_all()
            shutil.make_archive(os.path.join(path, "mangas", self.title, chapter_name), "zip", os.path.join(path, "mangas", self.title, chapter_name))
            shutil.rmtree(os.path.join(path, "mangas", self.title, chapter_name))
            progress += what_to_go_up_with
            progress_button.config(text=f"{self.title}\n{int(progress)}%")

            if progress > check_with_this:
                progress_button.config(bg=colors[0])
                del colors[0]
                check_with_this += 25

        progress_button.destroy()

    def handle_click_outside_entry(self, event):
        try:
            if event.widget != self.search_bar and event.widget != self.search_menu:
                self.button_frame.focus_set()
        except:
            pass
    
    def right_click_menu(self, event, title):
       self.my_menu.tk_popup(event.x_root, event.y_root)
       self.title = title

    def delete(self):
        shutil.rmtree(os.path.join(path, "mangas", self.title))
        mangas = os.listdir(os.path.join(path, "mangas"))
        self.icons = [load_image(os.path.join(path, "mangas", name, "icon.jpg"), icons_height) for name in mangas]
        for i in self.button_frame.grid_slaves():
            i.destroy()
            
        self.show_mangas(mangas, self.icons)

    def show_mangas(self, mangas, icons):
        buttons_per_row = 5
        self.my_menu = tk.Menu(root, tearoff=False, bg="#171717", fg="red")
        self.my_menu.add_command(label="Delete", font=("", 15), command=self.delete) 

        for i, (name, icon) in enumerate(zip(mangas, icons)):
            button_container = tk.Frame(self.button_frame, bg="#171717")
            button_container.grid(row=i // buttons_per_row, column=i % buttons_per_row)

            manga_button = tk.Button(button_container, image=icon, text=name, borderwidth=0, highlightthickness=0, bg="#141414")
            manga_button.config(command=lambda button=manga_button: load_pressed(button))
            manga_button.pack(side=tk.TOP, padx=5, pady=20)
            manga_button.bind("<Button-3>", lambda event, button = manga_button.cget("text"): self.right_click_menu(event,button))

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

            while text_label2.winfo_reqwidth() > manga_button.winfo_reqwidth():
                last_chapter = last_chapter[:-1]
                text_label2.config(text=f"Last Chapter: {last_chapter[:len(last_chapter) - 4]}" + "....")

    
    def search_result(self):
        results = [manga for manga in mangas if self.search_bar.get().lower() in manga.lower()]
        
        for name in self.button_frame.grid_slaves():
            if name.pack_slaves()[0].cget("text") not in results:
                self.removed_manga.append(name)
                name.grid_remove()
        
        for name in self.removed_manga:
            if name.pack_slaves()[0].cget("text") in results:
                name.grid()
                del name
        
        for i,name in enumerate(self.button_frame.grid_slaves()):
            name.grid(row=i // 5, column=i % 5)


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

icons_height = canvas.winfo_reqwidth()

home(True, None)
root.mainloop()
