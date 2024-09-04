 #!/usr/bin/python

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

for file in nordea_files:
    text = extract_text(file).split("\n")
    index = text.index("Rentedato") + 4
    kroner = text[index].strip("-DKK").strip().replace(",", ".")
    total += float(kroner)
    print(file + ":", str(round(float(kroner), 2)) + "kr")


print(f"Total: {round(total, 2)} kr")                                                 
