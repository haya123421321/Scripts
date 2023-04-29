import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
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
	desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
else:
	desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 

options = ChromeOptions()
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

urls = open(dir_path + "/" "urls.txt").read().split()
file_path = f"{desktop}\\Updated.txt".replace("\\", "\\")

for url in urls:
	r = driver.get(url)
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	name = soup.find(class_="film-name dynamic-name").text
	eps = soup.find(class_="episodes-ul").find_all("a")
	new_ep = eps[-1]["href"]
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
		open(file_path, "a").write(f"{name} Ep {len(eps)} https://9animetv.to{new_ep}\n")
		c.execute('UPDATE an SET ep = {} WHERE url = "{}"'.format(len(eps), url))
		conn.commit()
		print(f"{name} Updated to {eps}")
	else:
		pass
	conn.commit()


conn.close()
driver.close()
