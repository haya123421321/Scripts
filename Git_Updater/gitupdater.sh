#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

file=$SCRIPTPATH"/GitToCommits.txt"

while read -r line; do
	if [ -d $line ]; then
		cd $line
		git add .
		git commit -m "Commit"
		git push
	fi
done < $file

