from requests import get
from re import findall
from sys import argv
from os import makedirs, chdir

if len(argv) > 1:
    result = argv[1]
else:
    result = False

if result == False:
    print("Usage: python3 download.py <chapter>")
    exit()
else:
    pass
url = "https://mangaesp.co/ver/the-girl-from-tinder/" + argv[1]


r = get(url)

links = findall("https://imagizer.imageshack.com.*.jpg", r.text)
if len(links) < 5:
        links = findall("https://i.yapx.ru.*.jpg", r.text)

if len(links) < 5:
        links = findall("http://i.yapx.ru.*.jpg", r.text)

makedirs(argv[1])
chdir(argv[1])

for link,name in zip(links, range(len(links))):
    r = get(link)
    print(f"Downloading Picture: {str(name)}.jpg")
    open(str(name) + ".jpg", "wb").write(r.content)

print("Done!")
