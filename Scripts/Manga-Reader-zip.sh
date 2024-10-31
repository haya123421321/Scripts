#!/usr/bin/bash

GOOS=windows GOARCH=amd64 go build -o Manga-Reader.exe ./main.go
cd ..
7z a Manga-Reader.v1.0.0.x86-64.zip Manga-Reader
