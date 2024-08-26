#!/usr/bin/python

import subprocess
import sys
import os

directory = sys.argv[1]
find_command = subprocess.run(["find", directory, "-iname", "*.pdf"], capture_output=True, text=True).stdout
files = find_command.split("\n")

if len(files) == 0:
    print("No PDF files found.")
    sys.exit(1)

files_without_empty = []
for file in files:
    if file != "":
        files_without_empty.append(file)

if sys.argv[1] == ".":
    directory = os.path.basename(os.getcwd()) + ".pdf"
else:
    directory = sys.argv[1] + ".pdf"
print(directory)
pdfunite_command = ["pdfunite"] + files_without_empty + [directory]
subprocess.run(pdfunite_command)
