from requests import get
from sys import argv
from os import makedirs, chdir
from bs4 import BeautifulSoup

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
chapters = r.find(class_="row-content-chapter").find_all("li")
Title = r.find(class_="story-info-right").h1.text
makedirs(Title)
chdir(Title)

for i in chapters:
    name = i.a["href"].split("/")[4].split("-")[1]
    url = i.a["href"]
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

    makedirs(name)
    chdir(name)

    for link,name in zip(links, range(len(links))):
        r = get(link["src"], headers=headers)
        print(f"Downloading Picture: {str(name)}.jpg")
        open(str(name) + ".jpg", "wb").write(r.content)
    chdir("..")