import discord
import sqlite3
from bs4 import BeautifulSoup
import requests
import os
import asyncio
import cloudscraper
import argparse
import platform
import subprocess
import socket

dir_path = os.path.dirname(__file__)

intents = discord.Intents.default()
intents.all()

client = discord.Client(intents=intents)
TOKEN = "MTE5NTEwMTU4MDc4NjE0MzMzMg.Ggj5pX.ssV6bX60l4S6PwYmHTrrwrGdJepm05xPuRPZzQ"
channel_id = 938988530485559366
user_channel_id = 1195444285680656434
user_id = 513687538960039946
scraper = cloudscraper.create_scraper()

parser = argparse.ArgumentParser()
parser.add_argument("--clear", help="Clear error messeges in your PM" , action="store_true")
parser.add_argument("--fix-wb", help="Fix windbreaker", action="store_true")
args = parser.parse_args()

def void_scans(url):
    r = scraper.get(url)

    soup = BeautifulSoup(r.text, "html.parser")
    latest_chapter = [url["data-num"] for url in soup.find(class_="eplister").ul.find_all("li", recursive=False)]
    name = soup.find(class_="entry-title").text
    latest_chapter_url = [url.div.div.a["href"] for url in soup.find(class_="eplister").ul.find_all("li", recursive=False)]

    return name, latest_chapter, latest_chapter_url

def manga_rolls(url):
    if url.endswith("/"):
        url = url + "ajax/chapters/"
    else:
        url = url + "/ajax/chapters/"
    r = requests.post(url)
    r_name = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    latest_chapter_url = [url.a["href"] for url in soup.find_all(class_="wp-manga-chapter")]
    latest_chapter = [url.split("/")[-2].split("-")[1] for url in latest_chapter_url]

    soup = BeautifulSoup(r_name.text, "html.parser")
    name = soup.find(class_="post-title").h1.text.strip()

    return name, latest_chapter, latest_chapter_url

def top_manhua(url):
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    latest_chapter = [url.text.split()[1] for url in soup.find_all(class_="wp-manga-chapter")]
    latest_chapter_url = [url.a["href"] for url in soup.find_all(class_="wp-manga-chapter")]

    name = soup.find(class_="post-title").h1.text.strip()
    
    return name, latest_chapter, latest_chapter_url

def asura_toon(url):
    r = scraper.get(url)
    if r.status_code == 404:
        return False
    else:
        soup = BeautifulSoup(r.text, "html.parser")
        latest_chapter = [url["data-num"] for url in soup.find(class_="eplister").ul.find_all("li")]
        name = soup.find(class_="entry-title").text
        latest_chapter_url = [url.div.div.a["href"] for url in soup.find(class_="eplister").ul.find_all("li", recursive=False)]
    
        return name, latest_chapter, latest_chapter_url

def luminous_scans(url):
    r = requests.get(url)
    if r.status_code == 404:
        return False
    else:   
        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find(class_="entry-title").text
        latest_chapter_url = [url.div.div.a["href"] for url in soup.find(class_="eplister").ul.find_all("li", recursive=False)]
        latest_chapter = [url.split("-")[-1].strip("/") for url in latest_chapter_url]

        return name, latest_chapter, latest_chapter_url

async def edit_luminous_scans_message(channel, new_id, role, url, name):
    last_20_urls = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    latest_chapters = soup.find(class_="eplister").ul.find_all("li")

    for i in latest_chapters:
        last_20_urls.append(i.div.div.a["href"])
        if len(last_20_urls) == 20:
            break

    async for message in channel.history(limit=20):
        if message.author == client.user and ("luminouscomics" in message.content.split()[-1] or "lumitoon" in message.content.split()[-1]) and role in message.content.split()[0]:
            if message.content.split()[-1] != last_20_urls[0]:
                await message.edit(content=f"<@&{role}> <@&939178294442606642>\n{last_20_urls[0]}")
                del last_20_urls[0]
            else:
                del last_20_urls[0]
                continue

def reaper_scan(url):
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    latest_chapter = soup.find(class_="truncate font-medium text-neutral-200").text.strip().split()[1]
    latest_chapter_url = [url.a["href"] for url in soup.find(role="list").find_all("li")]
    name = soup.find(class_="overflow-hidden").img["alt"]

    return name, latest_chapter, latest_chapter_url

def stonescape(url):
    if url.endswith("/"):
        url = url + "ajax/chapters/"
    else:
        url = url + "/ajax/chapters/"
    r = requests.post(url)
    r_name = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    latest_chapter = [url.text.split()[2] for url in soup.find(class_="main version-chap no-volumn").find_all("li")]
    latest_chapter_url = [url.a["href"] for url in soup.find(class_="main version-chap no-volumn").find_all("li")]

    soup = BeautifulSoup(r_name.text, "html.parser")
    name = soup.find(class_="post-title").h1.text.strip()
    return name, latest_chapter, latest_chapter_url

@client.event
async def on_ready():
    conn = sqlite3.connect(dir_path + "/" + "a.db")
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE an (name text, url text, ch integer)")
    except:
        pass

    urls_file = open(dir_path + "/" "urls.txt")
    urls_lines = urls_file.read().split("\n")
        
    roles = [url.split("\\")[1].strip() for url in urls_lines]
    urls = [url.split("\\")[0].strip() for url in urls_lines]
        
    for url,role,index in zip(urls,roles,range(len(urls))):
        if url.startswith("#"):
            continue

        channel = client.get_channel(channel_id)

        try:
            if "hivetoon" in url:
                variables = void_scans(url)
            elif "cosmic-scans" in url:
                variables = cosmic_scans(url)
            elif "mangarolls" in url:
                variables = manga_rolls(url)
            elif "asuratoon" in url:
                variables = asura_toon(url)
                if variables == False:
                    r = scraper.get("https://asuratoon.com/?s={}".format("+".join(url.split("/")[4].split("-")[1:])))
                    soup = BeautifulSoup(r.text, "html.parser")
                    url = soup.find(class_="listupd").div.div.a["href"]
                    urls_lines[index] = f"{url} \\ {role}"
                    with open(dir_path + "/" "urls.txt", "w+") as urls_file:
                        urls_file.write("\n".join(urls_lines))

                        variables = asura_toon(url)
                        new_id = url.split("/")[4].split("-")[0]

            elif "luminous" in url:
                variables = luminous_scans(url)

                if variables == False:

                    r = requests.get("https://luminouscomics.org/?s={}".format("+".join(url.split("/")[4].split("-")[1:])))
                    soup = BeautifulSoup(r.text, "html.parser")
                    url = soup.find(class_="listupd").div.div.a["href"]
                    urls_lines[index] = f"{url} \\ {role}"
                    with open(dir_path + "/" "urls.txt", "w+") as urls_file:
                        urls_file.write("\n".join(urls_lines))

                    variables = luminous_scans(url)
                    if variables[0] == "Wind Breaker":
                        channel = client.get_channel(952924548695752704)

                    new_id = url.split("/")[4].split("-")[0]
                    data = await edit_luminous_scans_message(channel, new_id, role, url, variables[0])

            elif "manhuatop" in url:
                variables = top_manhua(url)
            elif "reaperscans" in url:
                variables = reaper_scan(url)
            elif "readreality-quest" in url:
                variables = readreality(url)
            elif "stonescape" in url:
                variables = stonescape(url)            
            else:
                user = await client.fetch_user(user_id)
                sent_messege = await user.send(f"Didnt process url: {url}")

        except:
            print(f"Something wrong with the url: {url}")
            user = await client.fetch_user(user_id)
            sent_messege = await user.send(f"Something wrong with the url: {url}")

            continue
        
        name = variables[0]
        latest_chapter = int(variables[1][0])
        latest_chapters = variables[1]
        latest_chapter_url = variables[2][0]
        latest_chapter_urls = variables[2]
        
        if name == "Wind Breaker":
            channel = client.get_channel(952924548695752704)

        c.execute('SELECT * FROM an WHERE name="{}"'.format(name))
        conn.commit()
        try:
            previous_ch = c.fetchone()[2]
        except:
            c.execute('INSERT INTO an VALUES ("{}", "{}", {})'.format(name.replace("'", "\\'"), url, latest_chapter))
            conn.commit()
            print(f"{name} Added to the DB")
            continue

        if latest_chapter > previous_ch:
            if (latest_chapter - previous_ch) == 1:
                c.execute('UPDATE an SET ch = {} WHERE name = "{}"'.format(latest_chapter, name))
                conn.commit()
                await channel.send(f"<@&{role}> <@&939178294442606642>\n{latest_chapter_url}")
            else:
                print(latest_chapters)
                multiple_urls = list(reversed(latest_chapter_urls[:latest_chapters.index(str(previous_ch))]))
                len_multiple_urls = len(multiple_urls)
                multiple_urls = "\n".join(multiple_urls)
                c.execute('UPDATE an SET ch = {} WHERE name = "{}"'.format(latest_chapter, name))
                conn.commit()
                await channel.send(f"<@&{role}> <@&939178294442606642> {len_multiple_urls} New Chapters\n{multiple_urls}")

    conn.close()
    urls_file.close()
    await client.close()

if os.path.isfile(dir_path + "/" "urls.txt"):
    pass
else:
    open(dir_path + "/" "urls.txt", "w").close()

if args.fix_wb: 
    @client.event
    async def on_ready():
        urls_file = open(dir_path + "/" "urls.txt").read().split("\n")
            
        urls = [url.split("\\")[0].strip() for url in urls_file]
        roles = [url.split("\\")[1].strip() for url in urls_file]

        for url,role in zip(urls,roles):
            if "wind-breaker" in url:
                wind_break_url = url
                wind_break_role = role
                break
            else:
                continue
        
        r = requests.get(wind_break_url)
        soup = BeautifulSoup(r.text, "html.parser")
        latest_chapters = soup.find(class_="eplister").ul.find_all("li")
        temp = []
        for i in latest_chapters:
            temp.append(i.div.div.a["href"])

        channel = client.get_channel(952924548695752704)

        async for message in channel.history(limit=20):
            if message.author == client.user and "wind-breaker" in message.content.split()[-1]:
                new_latest_chapter_url = temp[0]
                await message.edit(content=f"<@&{role}> <@&939178294442606642>\n{new_latest_chapter_url}")
                del temp[0]
        await client.close()
    client.run(TOKEN)

elif args.clear:
    @client.event
    async def on_ready():
        try:
            channel = await client.fetch_channel(user_channel_id)
        except discord.NotFound:
            print(f"Channel with ID {channel_id} not found.")
            await client.close()

        async for message in channel.history(limit=None):
            try:
                await message.delete()
            except:
                pass
        await client.close()

    client.run(TOKEN)
else:
    #ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    #host = "192.168.110.91"
    #if socket.gethostbyname(socket.gethostname()) != str(host):   
    #    try:
    #        response = subprocess.check_output(f"ping -w 2 {ping_str} {host}", shell=True, text=True)
    #    except:
    #        client.run(TOKEN)
    #else:
    #    client.run(TOKEN)
    client.run(TOKEN)
