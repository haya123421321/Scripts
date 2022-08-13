import requests
import sys

url =  "https://discord.com/api/v9/channels/934148467616522311/messages"

Tepz2 = {"authorization": "OTM0MTAzNTkzNDQ1ODg4MDIw.YerOQA.31UyvMliNoOZEQncN808P2llwuo"}
Tayyab = {"authorization": "NTU0MDU2NzQyMjA0NjA0NDU2.Yk8VoQ.5Y7E0GnnEFscJkbIzoMHwgSwxLc"}

sys = sys.argv[1]

if sys.upper() == "TEPZ2":
	while True:
		try:
			messege = input("")
			data = {"content": f"{messege}", "tts": "false"}
			r = requests.post(url, data=data, headers=Tepz2)
			print("Sent!")
		except:
			print("Something went wrong!")
			break

if sys.upper() == "TAYYAB":
	while True:
		try:
			messege = input("")
			data = {"content": f"{messege}", "tts": "false"}
			r = requests.post(url, data=data, headers=Tayyab)
			print("Send!")
		except:
			print("Something went wrong!")
			break