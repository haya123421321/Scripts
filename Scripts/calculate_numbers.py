#!/usr/bin/python

import sys

file = open(sys.argv[1]).read().split()

result = 0

for i in file:
	result += float(i.replace(",", "."))
print(result)