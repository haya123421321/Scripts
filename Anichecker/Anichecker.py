import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import os
import time

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
options.page_load_strategy = 'eager'

driver = webdriver.Chrome(options=options)
if os.path.isfile(dir_path + "/" "urls.txt"):
	pass
else:
	open(dir_path + "/" "urls.txt", "w")

urls_file = open(dir_path + "/" "urls.txt")
urls = urls_file.read().split("\n")

def animetv(url):
	r = driver.get(url)

	tries = 0
	while True:
		try:
			if tries == 3:
				return False
				break

			soup = BeautifulSoup(driver.page_source, 'html.parser')
			name = soup.find(class_="film-name dynamic-name").text
			status = soup.find_all(class_="item-content")[3].text.strip()

			eps = soup.find(class_="episodes-ul").find_all("a")
			new_ep = eps[-1]["href"]
			tries += 1
			return eps, name, new_ep, status
			break
		except:
			time.sleep(1)

for url in urls:	
	if "9animetv.to" in url:
		variables = animetv(url)
	else:
		print(f"The url is not a 9anime link: {url}")
		continue
	
	if variables != False:
		eps = variables[0]
		name = variables[1]
		new_ep = variables[2]
		status = variables[3]
	else:
		continue

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
		t = f"{name} | Ep {len(eps)} | https://9animetv.to{new_ep}\n"
		open(file_path, "a").write("-"*len(t) + "\n" + t)
		c.execute('UPDATE an SET ep = {} WHERE url = "{}"'.format(len(eps), url))
		conn.commit()
		print(f"{name} Updated to Ep {len(eps)}")
	else:
		pass

	if status == "Finished Airing":
		urls = [line for line in urls if line != url]
		with open(dir_path + "/" "urls.txt", "w") as urls_file:
			urls_file.write("\n".join(urls))
		c.execute('DELETE FROM an WHERE url = "{}"'.format(url))
		conn.commit()


driver.close()
conn.close()
