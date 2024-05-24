#!/usr/bin/python
import subprocess
import os
from threading import Thread
from queue import Queue

try:
    subprocess.run(["mkvmerge", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except:
    print("mkvmerge is not installed on this system or not in PATH.")
    exit()


path = os.getcwd()
files = os.listdir(path)
q = Queue()
[q.put(file) for file in files if file.endswith(".mkv")]
threads = min(25, q.qsize())
options = {}

def thread_job():
    while not q.empty():
        file = q.get()
        mkvmerge_output = subprocess.run(["mkvmerge", "-i", os.path.join(path, file)], capture_output=True, text=True)

        for line in mkvmerge_output.stdout.splitlines():
            if "subtitles" in line and line not in options:
                track_id = line.split()[2].strip(":")
                options[track_id] = line
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
for i in range(threads):
    t = Thread(target=main)
    t_list.append(t)
    t.start()
