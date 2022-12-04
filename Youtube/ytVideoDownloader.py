from pytube import YouTube
from sys import argv

if not len(argv) == 3:
    print("./script.py <Video link> <Output path>")
    exit()

link = argv[1]
yt = YouTube(link).streams.get_highest_resolution()

yt.download(output_path=argv[2])