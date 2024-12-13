#!/bin/bash

Config="$(dirname $(realpath "$0"))/config.json"

if [ ! -f "$Config" ];then
	echo "{}" > "$Config"
	echo "Config file created: "$Config""
fi

if [[ $(cat "$Config") == "" ]];then
	echo "{}" > "$Config"
fi

BackupUser=$(jq -r .User "$Config")
if [[ $BackupUser == "null" ]];then
	echo "There are no backup user, you will need to add one"
	read -p "Backup User: " New_user
	temp="$(dirname "$0")/temp.json"
	jq ".User = \"$New_user\"" "$Config" > "$temp" && mv "$temp" "$Config"
	BackupUser=$New_User
fi

BackupUserHome=$(sudo -u $BackupUser bash -c "echo ~")
BackupDirectory="$BackupUserHome/.Backup"
ToMakeBackup="$BackupDirectory/Backup"

if [ ! -d $BackupDirectory ] ;then
	mkdir -p $BackupDirectory
	echo "Directory created: $BackupDirectory"
fi

run=false

while getopts ":r" opt; do
  case $opt in
    r)
	    run=true
  esac
done

if [[ $run == false ]];then
	echo "[1] Show current backup user"
	echo "[2] Show Backup List"
	echo "[3] Change current Backup User"
	echo "[4] Add a file to Backup List"
	echo "[5] Remove a file from Backup List"
	while true;do
		read -p "Option: " Option

		if [[ "$Option" == 1 ]];then
			jq_data=$(jq -r .User "$Config")
			if [[ "$jq_data" == "null" ]];then
				echo "No backup user"
			else
				echo $jq_data
			fi
		fi

		if [[ "$Option" == 2 ]];then
			jq_data=$(jq .Files "$Config")
			if [[ "$jq_data" == "null" ]];then
				echo "No files in the Backup List"
			else
				echo $jq_data
			fi
		fi
		
		if [[ "$Option" == 3 ]];then
			jq_data=$(jq .User "$Config")
			echo "Current Backup User: $jq_data"
			read -p "New Backup User: " New_user
			temp="$(dirname "$0")/temp.json"
			jq ".User = \"$New_user\"" "$Config" > "$temp" && mv "$temp" "$Config"
		fi

		if [[ "$Option" == 4 ]];then 
			jq_data=$(jq .Files "$Config")
			if [[ "$jq_data" == "null" ]];then
				echo "No files right now"
			else 
				echo "Current Files:"
				echo $jq_data
			fi

			read -p "Full path to file: " New_file
			temp="$(dirname "$0")/temp.json"
			jq ".Files |= .+ [\"$New_file\"]" "$Config" > "$temp" && mv "$temp" "$Config"
			echo "Added: $New_file"
		fi

		if [[ "$Option" == 5 ]];then 
			i=0
			jq -r ".Files[]" "$Config" | while read -r line;do
				echo "$i. $line"
				i=$((i + 1))
			done
			read -p "Which file to remove, insert a index: " index
			temp="$(dirname "$0")/temp.json"
			deleted=$(jq ".Files[$index]" "$Config")
			jq "del(.Files[$index])" "$Config" > "$temp" && mv "$temp" "$Config"
			echo "Deleted: $deleted"
		fi
	done
else
	rm -r "$ToMakeBackup"
	mkdir -p "$ToMakeBackup"

	jq -r .Files[] "$Config" | while read line;do
		cp -r "$line" "$ToMakeBackup"
	done

	cd "$BackupDirectory"
	7z a Backup.zip $ToMakeBackup
	
	mount -m /dev/nvme1n1p1 Drive
	
	if [ ! -d "Drive/Backups" ] ;then
		mkdir -p "Drive/Backups"
		echo "Directory created: $BackupDirectory/Drive/Backups"
	fi
	
	Already_Made_Backups=$(stat -c "%y %n" Drive/Backups/* 2>/dev/null | sort)
	if [[ $Already_Made_Backups == "" ]];then
		How_Many_Made_Backups=0
	else
		How_Many_Made_Backups=$(echo "$Already_Made_Backups" | wc -l)
	fi

	if [[ $How_Many_Made_Backups -lt 10 ]];then
		mv Backup.zip "Drive/Backups/Backup $How_Many_Made_Backups.zip"
		echo "Success: $BackupDirectory/Drive/Backups/Backup $How_Many_Made_Backups.zip"
	else
		Oldest_file=$(echo "$Already_Made_Backups" | head -1 | cut -d " " -f 4-)
		mv Backup.zip "$Oldest_file"
		echo "Success: $BackupDirectory/$Oldest_file"
	fi

	umount Drive
	rm -rf Drive
fi
