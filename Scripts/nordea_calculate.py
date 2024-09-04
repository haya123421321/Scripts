#!/usr/bin/python3

from pdfminer.high_level import extract_text
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python script.py <directory>")
    sys.exit(1)


def find_Nordea_files(directory):
    Nordea_files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if "Nordea - Transaktioner & detaljer" in filename and filename.endswith(".pdf"):
            Nordea_files.append(filepath)
    return Nordea_files

nordea_files = find_Nordea_files(sys.argv[1])
total = 0

i = 0
index = 3
while True:
    if i == len(nordea_files):
        break
    file = nordea_files[i]
    text = extract_text(file).split("\n")
    try:
        kroner_index = text.index("Rentedato") + index
    except ValueError:
        print("Something wrong with " + file)
        i += 1
        
    try:
        kroner = text[kroner_index].strip("-DKK").strip().replace(",", ".")
        total += float(kroner)
        print(file + ":", str(round(float(kroner), 2)) + "kr")
        i += 1
        index = 3
    except:
        index += 1


print(f"Total: {round(total, 2)} kr")                                                 
