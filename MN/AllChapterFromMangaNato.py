from requests import get
from sys import argv
from os import makedirs, chdir
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from time import sleep
import shutil
import argparse

if len(argv) > 1:
    result = argv[1]
else:
    result = False

if result == False:
    print("Usage: python3 script.py --search <name> --id <Id>")
    print("You can find the ID in the url")
    exit()
else:
    pass

search_parser = argparse.ArgumentParser()

search_parser.add_argument("--search")
search_parser.add_argument("--id")

args = search_parser.parse_args()

if args.search is not None:
    search = args.search.replace(" ", "_")
    r = get("https://manganato.com/search/story/" + search)
    r = BeautifulSoup(r.text, 'html.parser')

    results = r.find(class_="panel-search-story").find_all("div")

    titles = []
    urls = []

    for result in results:
        titles.append(result.h3.text.strip())
        urls.append(result.a["href"])

    titles = list(dict.fromkeys(titles))
    urls = list(dict.fromkeys(urls))

    for i,title,url in zip(range(len(titles)), titles, urls):
        menu = str(i) + "  " + title
        print(menu)

    Value_number = input()

    url = urls[int(Value_number)]
elif args.id is not None:
    url = f"https://chapmanganato.com/manga-{args.id}"

r = get(url)
r = BeautifulSoup(r.text, 'html.parser')

chapterss = r.find(class_="row-content-chapter").find_all("li")
Title = r.find(class_="story-info-right").h1.text
chapters = []
for i in chapterss:
    chapters.append(i.a["href"])
chapters = chapters[::-1]

try:
    makedirs(Title)
except:
    Title = input(f"The folder and files can't be named {Title} please choose another name: ")
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
    sleep(0.5)
