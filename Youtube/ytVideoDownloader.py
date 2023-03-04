from pytube import YouTube
from sys import argv
import ffmpeg
from os import remove
from threading import Thread

if not len(argv) == 3:
    print("./script.py <Video link> <Output path>")
    exit()

link = argv[1]

yt = YouTube(link)

def AudioDownload():
    a = YouTube(link).streams.filter(only_audio=True).first().download(output_path=argv[2], filename="audio.mp3")

def VideoDownload():
    v = YouTube(link).streams.filter(adaptive=True).first().download(output_path=argv[2], filename="video.mp4")

A = Thread(target=AudioDownload)
V = Thread(target=VideoDownload)

A.start()
V.start()
A.join()
V.join()
audio = ffmpeg.input(argv[2] + "/" + "audio.mp3")
video = ffmpeg.input(argv[2] + "/" + "video.mp4")

ffmpeg.output(audio, video, argv[2] + "/" + str(yt.title) + ".mp4").run(overwrite_output=True)

remove(argv[2] + "/" + "audio.mp3")
remove(argv[2] + "/" + "video.mp4")
