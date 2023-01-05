from requests import get
from sys import argv
from os import makedirs, chdir
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import shutil

if len(argv) > 1:
    result = argv[1]
else:
    result = False

if result == False:
    print("Usage: python3 download.py <Id>")
    exit()
else:
    pass

url = f"https://readmanganato.com/manga-{argv[1]}"
r = get(url)
r = BeautifulSoup(r.text, 'html.parser')

chapterss = r.find(class_="row-content-chapter").find_all("li")
Title = r.find(class_="story-info-right").h1.text
chapters = []
for i in chapterss:
    chapters.append(i.a["href"])
chapters = chapters[::-1]

makedirs(Title)
chdir(Title)

for i in chapters:
    chapter_name  = Title + " " + i.split("/")[4].split("-")[1]
    print(f"Downloading Chapter: {chapter_name }")
    q = Queue()
    names = Queue()
    r = get(i)
    r = BeautifulSoup(r.text, 'html.parser')
    
    makedirs(chapter_name)
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
            r = get(link, headers=headers)
            open(str(name) + ".jpg", "wb").write(r.content)
            q.task_done()

    def download_all():
        for i in range(10):
            t_worker = Thread(target=downloadlink)
            t_worker.start()
        q.join()


    download_all()
    chdir("..")
    shutil.make_archive(chapter_name, "zip", chapter_name)
    shutil.rmtree(chapter_name)
