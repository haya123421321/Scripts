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

os.makedirs(search_query, exist_ok=True)

def main():
    while not q.empty():
        post = q.get()
        if post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')) and "imgur" not in post.url:
            os.makedirs(os.path.join(cwd, "pics"), exist_ok=True)
            media_url = post.url
            media_name = f"{post.title.replace(' ', '_')}." + media_url.split(".")[-1]
            media_name = truncate_filename(media_name)
            media_path = os.path.join(cwd, "pics", media_name)
        elif 'v.redd.it' in post.url:
            os.makedirs(os.path.join(cwd, "vids"), exist_ok=True)
            submission = reddit.submission(id=post.id)
            media_url = submission.media['reddit_video']['fallback_url']
            media_name = f"{post.title.replace(' ', '_')}.mp4"
            media_name = truncate_filename(media_name)
            media_path = os.path.join(cwd, "vids", media_name)
        else:
            continue

        response = requests.get(media_url)
        with open(media_path, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded: {media_name}")

for i in range(5):
    t_worker = threading.Thread(target=main)
    t_worker.start()
