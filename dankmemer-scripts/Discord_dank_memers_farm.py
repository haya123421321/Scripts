import requests
import time

url =  "https://discord.com/api/v9/channels/934148467616522311/messages"

Tepz = {"authorization": "NTEzNjg3NTM4OTYwMDM5OTQ2.Yep1AA.BFAvzK4WvZkbdFIyR2-WItSTCPQ"}
Tepz2 = {"authorization": "OTM0MTAzNTkzNDQ1ODg4MDIw.YerOQA.31UyvMliNoOZEQncN808P2llwuo"}

data = {"content": "pls fish", "tts": "false"}
data2 = {"content": "pls beg", "tts": "false"}
data3 = {"content": "pls hunt", "tts": "false"}

while True:
    requests.post(url, data=data, headers=Tepz)
    requests.post(url, data=data2, headers=Tepz)
    requests.post(url, data=data3, headers=Tepz)
    requests.post(url, data=data, headers=Tepz2)
    requests.post(url, data=data2, headers=Tepz2)
    requests.post(url, data=data3, headers=Tepz2)
    time.sleep(50)