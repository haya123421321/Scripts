import requests
import time
from win10toast import ToastNotifier
import sys

alert = ToastNotifier()

urltocheck = "https://mangaesp.co/ver/la-piba-del-tinder"
stringtocheck = "https://mangaesp.co/ver/la-piba-del-tinder/" + sys.argv[1]
msg = "The new chapter is here."



while True:
	checker = requests.get(urltocheck)
	if stringtocheck in checker.text:
		alert.show_toast(msg)
		break
	else:
		time.sleep(120)