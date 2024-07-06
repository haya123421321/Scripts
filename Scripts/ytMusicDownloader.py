#!/usr/bin/python3

from pytube import YouTube
import os
from sys import argv

if not len(argv) == 3:
	print("./script.py <Video link> <Output path>")
	exit()

yt = YouTube(argv[1])
  
video = yt.streams.filter(only_audio=True).first()
  

destination = argv[2]
  
out_file = video.download(output_path=destination)
  
base, ext = os.path.splitext(out_file)
new_file = base + '.mp3'
os.rename(out_file, new_file)
  
print(yt.title + " has been successfully downloaded.")
