from requests import get
from re import findall
from sys import argv
from os import makedirs, chdir, remove
from PIL import Image
from queue import Queue
from threading import Thread

if len(argv) > 1:
    result = argv[1]
else:
    result = False

if result == False:
    print("Usage: python3 download.py <chapter>")
    exit()
else:
    pass
url = "https://mangaesp.co/ver/junwoo-wonka-y-la-fabrica-de-prras-locas/" + argv[1]

q = Queue()
r = get(url)
names = Queue()

links = findall("https://imagizer.imageshack.com.*.jpg", r.text)
if len(links) < 1:
        links = findall("https://i.yapx.ru.*.jpg", r.text)

if len(links) < 1:
        links = findall("http://i.yapx.ru.*.jpg", r.text)

if len(links) < 1:
        links = findall("https://cdn.snf18.xyz/images/.*.webp", r.text)

for url in links:
    q.put(url)
for name in range(len(links)):
    names.put(name)

makedirs(argv[1])
chdir(argv[1])

def downloadlink():
    while not q.empty():
        link = q.get()
        name = names.get()
        r = get(link)
        if link.endswith("webp"):
            print(f"Downloading Picture: {str(name)}.jpg")
            open(str(name) + ".webp", "wb").write(r.content)
            Image.open(str(name) + ".webp").save(str(name) + ".jpg")
            remove(str(name) + ".webp")

        elif link.endswith("jpg"):
            print(f"Downloading Picture: {str(name)}.jpg")
            open(str(name) + ".jpg", "wb").write(r.content)
        q.task_done()


def download_all():
    for i in range(len(links)):
        t_worker = Thread(target=downloadlink)
        t_worker.start()
    q.join()

download_all()

print("Done!")
