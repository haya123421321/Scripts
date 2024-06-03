#!/usr/bin/python
import subprocess
import os
from threading import Thread
from queue import Queue
import argparse

try:
    subprocess.run(["mkvmerge", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except:
    print("mkvmerge is not installed on this system or not in PATH.")
    exit()

searcher_parser = argparse.ArgumentParser()
searcher_parser.add_argument("--multi", action='store_true')
args = searcher_parser.parse_args()

path = os.getcwd()
files = os.listdir(path)
q = Queue()
if args.multi:
    [q.put(file) for file in files if file.endswith(".mkv")]
else:
    for file in files:
        if file.endswith("mkv"):
            q.put(file)
            break

threads = min(25, q.qsize())
options = {}

def thread_job():
    while not q.empty():
        file = q.get()
        mkvmerge_output = subprocess.run(["mkvmerge", "-i", os.path.join(path, file)], capture_output=True, text=True)
        ffmpeg_output = subprocess.run(["ffmpeg", "-i", os.path.join(path, file)], capture_output=True, text=True)
        
        titles = []
        for index,i in enumerate(ffmpeg_output.stderr.splitlines()):
            if "Subtitle" in i:
                titles.append(" ".join(ffmpeg_output.stderr.splitlines()[index + 2].split()[2:]))
        
        index = 0
        for line in mkvmerge_output.stdout.splitlines():
            if "subtitles" in line and line not in options:
                track_id = line.split()[2].strip(":")
                options[track_id] = f"Track id {track_id}: {titles[index]}"
                index += 1
        q.task_done()

t_list = []
for i in range(threads):
    t = Thread(target=thread_job)
    t_list.append(t)
    t.start()

for i in t_list:
    i.join()

print("\n".join(options.values()))

choice = input("\nWhat Track ID to use: ")

while choice not in options:
    choice = input("\nSorry not a valid ID: ")

[q.put(file) for file in files if file.endswith(".mkv")]

def main():
    while not q.empty():
        file = q.get()
        mkvmerge_output = subprocess.run(["mkvmerge" , "-o", f"{os.path.join(path, file)}CACHE", "-s", choice, f"{os.path.join(path, file)}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["mv", f"{os.path.join(path, file)}CACHE", os.path.join(path, file)])
        print(f"✅ {file} done")

t_list = []
threads = min(25, q.qsize())

for i in range(threads):
    t = Thread(target=main)
    t_list.append(t)
    t.start()
