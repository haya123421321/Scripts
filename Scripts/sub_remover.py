#!/usr/bin/python
import subprocess
import os

try:
    subprocess.run(["mkvmerge", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except:
    print("mkvmerge is not installed on this system or not in PATH.")
    exit()


path = os.getcwd()
files = os.listdir(path)
files =  [file for file in files if file.endswith(".mkv")]

options = {}

for file in files:
    mkvmerge_output = subprocess.run(["mkvmerge", "-i", os.path.join(path, file)], capture_output=True, text=True)

    for line in mkvmerge_output.stdout.splitlines():
        if "subtitles" in line and line not in options:
            track_id = line.split()[2].strip(":")
            options[track_id] = line

print("\n".join(options.values()))

choice = input("\nWhat Track ID to use: ")

while choice not in options:
    choice = input("\nSorry not a valid ID: ")

for file in files:
    mkvmerge_output = subprocess.run(["mkvmerge" , "-o", f"{os.path.join(path, file)}CACHE", "-s", choice, f"{os.path.join(path, file)}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["mv", f"{os.path.join(path, file)}CACHE", os.path.join(path, file)])  # Fixed this line
    print(f"✅ {file} done")
