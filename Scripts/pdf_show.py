#!/usr/bin/python3

from pdfminer.high_level import extract_text
import os
import sys

index = 3

file = sys.argv[1]

text = extract_text(file).split("\n")
print(text)
