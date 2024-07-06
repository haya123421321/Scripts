#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

file=~/Scripts/Git_Updater/GitToCommits.txt

while read -r line; do
	if [ -d $line ]; then
		cd $line
		git add . > /dev/null 2>&1
		git commit -m "Commit" > /dev/null 2>&1
		git push > /dev/null 2>&1
		echo ✅ $line
	else
		echo "Directory" $line not found
	fi
done < $file

