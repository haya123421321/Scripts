import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import os

conn = sqlite3.connect("a.db")
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

urls = open("urls.txt").read().split()
file_path = f"{desktop}\\Updated.txt".replace("\\", "\\")

for url in urls:
	r = driver.get(url)
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	eps = len(soup.find(class_="episodes-ul").find_all("a"))
	name = soup.find(class_="film-name dynamic-name").text
	c.execute('SELECT * FROM an WHERE url="{}"'.format(url))
	conn.commit()
	try:
		previous_ep = c.fetchone()[2]
	except:
		c.execute('INSERT INTO an VALUES ("{}", "{}", {})'.format(name.replace("'", "\\'"), url, eps))
		conn.commit()
		print(f"{name} Added to the DB")
		continue
	if eps > previous_ep:
		open(file_path, "a").write(f"{name} Ep {eps}    {url}")
		c.execute('UPDATE an SET ep = {} WHERE url = "{}"'.format(eps, url))
		conn.commit()
		print(f"{name} Updated to {eps}")
	else:
		pass
	conn.commit()


conn.commit()
conn.close()
driver.close()
