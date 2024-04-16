#!/usr/bin/python

import praw
import requests
import os
import sys
import threading
from queue import Queue

reddit = praw.Reddit(client_id='jq4Q3TJoclXGS1Ft985gdg',
                     client_secret='3o8jGNIjtrn3j1jgdxTpw5_VZHi7pQ',
                     user_agent='"MyScript by /u/Translator1122"')

search_query = " ".join(sys.argv[2:])

search_results = reddit.subreddit("all").search(search_query, limit=int(sys.argv[1]), params={'include_over_18': 'on'})

def truncate_filename(filename, max_length=100):
    if len(filename) <= max_length:
        return filename
    else:
        filename_extension = os.path.splitext(filename)[-1]
        truncated_filename = filename[:max_length - len(filename_extension)] + filename_extension
        return truncated_filename

cwd = os.getcwd()
cwd = os.path.join(cwd, search_query)
q = Queue()

for post in search_results:
    q.put(post)
    print(post.url)


os.makedirs(search_query, exist_ok=True)

blacklisted = ["gfycat"]

def main():
    while not q.empty():
        post = q.get()
        
        if "imgur" in post.url:
            media_url = post.url
            media_url.replace("http://", "https://")
            referer_url = "".join(media_url.split("/")[0] + "//" + media_url.split("/")[2].replace("i.", "") + "/" + media_url.split("/")[-1].split(".")[0])
            download_url = "".join(media_url.split("/")[0] + "//" + media_url.split("/")[2].replace("i.", "") + "/download/" + media_url.split("/")[-1].split(".")[0]) + "/"
            
            media_name = f"{post.title.replace(' ', '_')}." + media_url.split(".")[-1]
            media_name = media_name.replace("/", "").replace("[", "").replace("]", "")
            media_name = truncate_filename(media_name)
            media_path = os.path.join(cwd, "pics", media_name)
            name_index = 2
            while os.path.isfile(os.path.join(media_path)):
                media_name = f"{post.title.replace(' ', '_')} {name_index}." + media_url.split("?")[0].split(".")[-1]
                media_path = os.path.join(cwd, "pics", media_name)
                name_index += 1
            media_path = os.path.join(cwd, "pics", media_name)

            headers = {'referer': f'{referer_url}'}
            
            try:
                response = requests.get(download_url, headers=headers)
                if len(response.content) == 0:
                    continue
                else:
                    with open(media_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"Downloaded: {media_name}")
                    continue
            except:
                continue

        elif post.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv')) and all(site not in post.url for site in blacklisted):
            os.makedirs(os.path.join(cwd, "pics"), exist_ok=True)
            media_url = post.url
            media_name = f"{post.title.replace(' ', '_')}." + media_url.split(".")[-1]
            media_name = media_name.replace("/", "").replace("[", "").replace("]", "")
            media_name = truncate_filename(media_name)
            media_path = os.path.join(cwd, "pics", media_name)
            name_index = 2
            while os.path.isfile(media_path):
                media_name = f"{post.title.replace(' ', '_')} {name_index}." + media_url.split("?")[0].split(".")[-1]
                media_path = os.path.join(cwd, "pics", media_name)
                name_index += 1
            media_path = os.path.join(cwd, "pics", media_name)
            
            try:
                response = requests.get(media_url)
                with open(media_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {media_name}")
            except:
                continue


        elif 'v.redd.it' in post.url:
            os.makedirs(os.path.join(cwd, "vids"), exist_ok=True)
            try:
                submission = reddit.submission(id=post.id)
                media_url = submission.media['reddit_video']['fallback_url']
            except:
                print("couldnt get the submission media: " + post.url)
                continue
            media_name = f"{post.title.replace(' ', '_')}.mp4"
            media_name = media_name.replace("/", "").replace("[", "").replace("]", "")
            media_name = truncate_filename(media_name)
            media_path = os.path.join(cwd, "vids", media_name)
            name_index = 2
            while os.path.isfile(media_path):
                media_name = f"{post.title.replace(' ', '_')} {name_index}." + media_url.split("?")[0].split(".")[-1]
                media_path = os.path.join(cwd, "vids", media_name)
                name_index += 1

            try:
                response = requests.get(media_url)
                with open(media_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {media_name}")
            except:
                continue

            
        elif post.url.split("/")[3] == "gallery":
            submission = reddit.submission(url=post.url)

            if submission.is_gallery:
                for item in submission.media_metadata.values():
                    media_url = item["s"]["u"]
                    media_name = f"{post.title.replace(' ', '_')}." + media_url.split("?")[0].split(".")[-1]
                    media_name = media_name.replace("/", "").replace("[", "").replace("]", "")
                    media_name = truncate_filename(media_name)
                    media_path = os.path.join(cwd, "pics", media_name)
                    name_index = 2
                    while os.path.isfile(media_path):
                        media_name = f"{post.title.replace(' ', '_')} {name_index}." + media_url.split("?")[0].split(".")[-1]
                        media_path = os.path.join(cwd, "pics", media_name)
                        name_index += 1

            
                    try:
                        response = requests.get(media_url)

                        with open(media_path, 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded: {media_name}")
                    except:
                        continue

            continue



for i in range(5):
    t_worker = threading.Thread(target=main)
    t_worker.start()
