from pytube import YouTube
import os
from sys import argv

yt = YouTube(argv[1])
  
video = yt.streams.filter(only_audio=True).first()
  

destination = "/home/tepz/.local/share/spotify-launcher/install/usr/share/spotify/LocalSongs"
  
out_file = video.download(output_path=destination)
  
base, ext = os.path.splitext(out_file)
new_file = base + '.mp3'
os.rename(out_file, new_file)
  
print(yt.title + " has been successfully downloaded.")
