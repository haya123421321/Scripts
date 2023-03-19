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
    print("Usage: python3 download.py <Id> <Chapter>")
    exit()
else:
    pass

q = Queue()
names = Queue()
url = f"https://readmanganato.com/manga-{argv[1]}/chapter-{argv[2]}"
r = get(url)
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

Title = r.find(class_="panel-chapter-info-top").h1.text.split(":")[0]

def downloadlink():
    while not q.empty():
        link = q.get()
        name = names.get()
        r = get(link, headers=headers)
        print(f"Downloading Picture: {str(name)}.jpg")
        open(str(name) + ".jpg", "wb").write(r.content)
        q.task_done()

def download_all():
    for i in range(15):
        t_worker = Thread(target=downloadlink)
        t_worker.start()
    q.join()

makedirs(Title)
chdir(Title)
download_all()
chdir("..")
shutil.make_archive(Title, "zip", Title)
shutil.rmtree(Title)
