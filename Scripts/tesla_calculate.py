#!/usr/bin/python

from pdfminer.high_level import extract_text
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python script.py <directory>")
    sys.exit(1)


def find_pdfs(directory):
    pdf_files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            pdf_files.extend(find_pdfs(filepath))
        elif filename.endswith('.pdf'):
            pdf_files.append(filepath)
    return pdf_files

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print("Error: Not a valid directory")
        sys.exit(1)

    pdf_files = find_pdfs(directory)

all_pdf_files = find_pdfs(sys.argv[1])
total = 0

for file in all_pdf_files:
    try:
        text = extract_text(file).split()
        index = text.index("Kode") - 1
        kroner = text[index]
        total += float(kroner)
        print(round(float(kroner), 2))
    except:
        continue

print(f"Total: {round(total, 2)} kr")