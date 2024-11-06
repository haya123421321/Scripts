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

index = 3
for file in nordea_files:
    text = extract_text(file).split("\n")

    while True:
        try:
            kroner_index = text.index("Rentedato") + index
        except ValueError:
            print("Something wrong with " + file)
            index = 3
            break

        try:
            kroner_no_strip = text[kroner_index].strip()
            if "DKK" not in kroner_no_strip:
                index += 1
                continue

            kroner = text[kroner_index].strip("-DKK").strip().replace(",", ".")
            date = text[kroner_index + 2]

            kroner_split = kroner.split(".")

            if len(kroner_split) > 1:
                kroner = "".join(kroner_split[:-1]) + "." + kroner_split[-1]

            total += float(kroner)
            print(round(float(kroner), 2), " ", date," ", file)
            index = 3
            break
        except:
            if kroner_index > len(text):
                print("Couldnt get information of: " + file)
                index = 3
                break
            else:
                index += 1

print(f"Total: {round(total, 2)} kr")                                                 
