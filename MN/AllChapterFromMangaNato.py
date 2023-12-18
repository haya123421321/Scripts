#!/usr/bin/python3

from requests import get, Session
from sys import argv
from os import makedirs, chdir, system, name
from os.path import isfile
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from time import sleep
import shutil
import argparse


search_parser = argparse.ArgumentParser()

search_parser.add_argument("--id")

args = search_parser.parse_args()
page = 1

s = Session()

if args.id is not None:
    url = f"https://chapmanganato.com/manga-{args.id}"
else:
    search = input("Search: ")
    search = search.replace(" ", "_")
    url = "https://manganato.com/search/story/" + search + "?page=" + str(page)
    r = s.get(url)
    r = BeautifulSoup(r.text, 'html.parser')

    try:
        results = r.find(class_="panel-search-story").find_all("div")
    except:
        print("cant find the specified manga/manhwa/manhua")
    titles = []
    urls = []
    try:
        pages = r.find(class_="page-blue page-last").text.strip("LAST()")
    except:
        pages = "1"
    
    print(f"{page}/{pages}")
    
    for result in results:
        titles.append(result.h3.text.strip())
        urls.append(result.a["href"])

    titles = list(dict.fromkeys(titles))
    urls = list(dict.fromkeys(urls))
    biggest_title = 0
    
    for title in titles:
        if len(title) > biggest_title:
            biggest_title = len(title)
        else:
            pass
    t = 1
    for i,title,url in zip(range(len(titles)), titles, urls):
        if i < 10:
            minus = "------"
            space = "  "
        else:
            minus = "-----"
            space = " "
        minuses = "-"*biggest_title + "-"*len(str(i)) + minus + "-"
        spaces_left = len(minuses) - len(title) - len(str(i)) - len(minus) - 1
        menu = space + str(i) + " | " + title + " "*spaces_left + " |"

        while t == 1:
            print(minuses)
            spaces_left2 = len(minuses) - len(" ID | Title") - 2
            print(" ID | Title" + " "*spaces_left2 + " |")
            print(minuses)
            t = 0
        print(menu)
        print(minuses)

    print("\nNext page = n")
    print("Previous page = p")        
    
    Value_number = input("\nSelect the series by ID: ")
    if Value_number == "n":
        if str(page) != pages:
            page = int(page) + 1
        else:
            pass            
    elif Value_number == "p":
        if str(page) != "1":
            page = int(page) - 1    
        else:
            pass
    else:
        url = urls[int(Value_number)]
        args.search = None
    all_or_specific = input("Type the chapter number or press enter for all: ").split("-")

r = s.get(url)
r = BeautifulSoup(r.text, 'html.parser')

chapterss = r.find(class_="row-content-chapter").find_all("li")
Title = r.find(class_="story-info-right").h1.text
chapters = []
for i in chapterss:
    chapters.append(i.a["href"])
chapters = chapters[::-1]

chap_nums = [url.split("-")[2] for url in chapters]

try:
    if len(all_or_specific) == 2:
        chapters = chapters[chap_nums.index(all_or_specific[0]):chap_nums.index(all_or_specific[1]) + 1]
    elif all_or_specific[0] == "":
        chapters = chapters
    elif len(all_or_specific) == 1:
        chapters = chapters[chap_nums.index(all_or_specific[0])].split()
except:
    print(f"The Chapter Doesn't Exist: ")
    exit

try:
    makedirs(Title, exist_ok=True)
except:
    Title = input(f"The folder and files can't be named {Title} please choose another name: ")
    makedirs(Title, exist_ok=True)
chdir(Title)

Total_chapters = len(chapters)
num_digits = len(str(Total_chapters))

for index,i in enumerate(chapters, start=1):
    chapter_name  = Title + " " + i.split("/")[4].split("-")[1].zfill(num_digits)
    if isfile(chapter_name + ".zip"):
        continue
    else:
        pass

    progress = index / Total_chapters
    bar_length = int(40 * progress)
    bar = "█" * bar_length + '-' * (40 - bar_length)
    print(f'[{bar}] {index}/{Total_chapters}', end='\r')

    q = Queue()
    names = Queue()
    r = s.get(i)
    r = BeautifulSoup(r.text, 'html.parser')
    
    makedirs(chapter_name, exist_ok=True)
    chdir(chapter_name)

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
            open(str(name) + ".jpg", "wb").write(r.content)
            q.task_done()

    def download_all():
        for i in range(20):
            t_worker = Thread(target=downloadlink)
            t_worker.start()
        q.join()


    download_all()
    chdir("..")
    shutil.make_archive(chapter_name, "zip", chapter_name)
    shutil.rmtree(chapter_name)

print()
