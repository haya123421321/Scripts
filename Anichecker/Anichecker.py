import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import os

dir_path = os.path.dirname(__file__)

conn = sqlite3.connect(dir_path + "/" + "a.db")
c = conn.cursor()

try:
	c.execute("CREATE TABLE an (name text, url text, ep integer)")
except:
	pass
conn.commit()

if os.name == "nt":
	file_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + "\\Updated.txt".replace("\\", "\\")
else:
	file_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + "/Updated.txt"

options = ChromeOptions()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

urls = open(dir_path + "/" "urls.txt").read().split()

def animetv(url):
	r = driver.get(url)
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	name = soup.find(class_="film-name dynamic-name").text
	status = soup.find_all(class_="item-content")[3].text.strip()

	eps = soup.find(class_="episodes-ul").find_all("a")
	new_ep = eps[-1]["href"]
	return eps, name, new_ep, status

for url in urls:	
	if "9animetv.to" in url:
		variables = animetv(url)
	else:
		print(f"The url is not a 9anime link: {url}")
		continue
	
	eps = variables[0]
	name = variables[1]
	new_ep = variables[2]
	status = variables[3]

	c.execute('SELECT * FROM an WHERE url="{}"'.format(url))
	conn.commit()
	try:
		previous_ep = c.fetchone()[2]
	except:
		c.execute('INSERT INTO an VALUES ("{}", "{}", {})'.format(name.replace("'", "\\'"), url, len(eps)))
		conn.commit()
		print(f"{name} Added to the DB")
		continue

	if len(eps) > previous_ep:
		t = f"{name} | Ep {len(eps)} | {status} | https://9animetv.to{new_ep}\n"
		open(file_path, "a").write("-"*len(t) + "\n" + t)
		c.execute('UPDATE an SET ep = {} WHERE url = "{}"'.format(len(eps), url))
		conn.commit()
		print(f"{name} Updated to Ep {len(eps)}")
	else:
		pass

driver.close()
conn.close()
