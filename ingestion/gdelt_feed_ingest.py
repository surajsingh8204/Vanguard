import requests
import zipfile
import csv
import os
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://data.gdeltproject.org/gdeltv2/"
TRACKER_FILE = "data_lake/processed_feeds.txt"


# 🔥 Generate multiple feed URLs (last N hours)
def generate_feed_urls(hours_back=3):

    now = datetime.utcnow()

    # 🔥 Align to nearest lower 15-min boundary
    minute = (now.minute // 15) * 15
    aligned_now = now.replace(minute=minute, second=0, microsecond=0)

    urls = []

    for i in range(hours_back * 4):

        ts = aligned_now - timedelta(minutes=15 * i)

        timestamp = ts.strftime("%Y%m%d%H%M00")

        url = f"{BASE_URL}{timestamp}.gkg.csv.zip"

        urls.append(url)

    return urls

# 📥 Download feed safely
def download_feed(url):

    os.makedirs("data_lake/raw_feeds", exist_ok=True)

    filename = url.split("/")[-1]
    path = f"data_lake/raw_feeds/{filename}"

    if os.path.exists(path):
        print("Already downloaded:", filename)
        return path

    try:
        print("Downloading:", filename)

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print("Failed:", filename)
            return None

        with open(path, "wb") as f:
            f.write(r.content)

        time.sleep(1)  # 🔥 avoid rate limit

        return path

    except Exception as e:
        print("Error downloading:", filename)
        return None


# 📊 Parse GKG
def parse_gkg(path):

    articles = []

    try:
        with zipfile.ZipFile(path, 'r') as z:

            filename = z.namelist()[0]

            with z.open(filename) as f:

                reader = csv.reader(
                    (line.decode("utf-8", errors="ignore") for line in f),
                    delimiter="\t"
                )

                for row in reader:

                    try:

                        url = row[4]

                        if not url.startswith("http"):
                            continue

                        article = {
                            "date": row[1],
                            "source": row[3],
                            "url": url
                        }

                        articles.append(article)

                    except:
                        continue

    except Exception:
        print("Error parsing:", path)

    return articles


# 💾 Save articles
def save_articles(articles):

    if not articles:
        return

    now = datetime.utcnow()

    folder = f"data_lake/raw/{now.year}/{now.month}/{now.day}"

    os.makedirs(folder, exist_ok=True)

    filename = f"{folder}/articles_{now.hour}_{now.minute}_{now.second}.json"

    with open(filename, "w") as f:
        json.dump(articles, f)

    print(f"Saved {len(articles)} articles → {filename}")


# 📌 Load processed feeds
def load_processed():

    if not os.path.exists(TRACKER_FILE):
        return set()

    with open(TRACKER_FILE) as f:
        return set(f.read().splitlines())


# 📌 Save processed feed
def mark_processed(filename):

    os.makedirs("data_lake", exist_ok=True)

    with open(TRACKER_FILE, "a") as f:
        f.write(filename + "\n")


# 🚀 MAIN RUN
def run():

    HOURS_BACK = 24

    urls = generate_feed_urls(
        hours_back=HOURS_BACK
    )
    print(
         f"Processing {len(urls)} feeds "
         f"from last {HOURS_BACK} hours"
    )

    processed = load_processed()

    total_articles = 0
    processed_count = 0

    for url in urls:

        filename = url.split("/")[-1]

        if filename in processed:
            print("Already processed:", filename)
            continue

        path = download_feed(url)

        if not path:
            continue

        articles = parse_gkg(path)

        if articles:
            save_articles(articles)
            total_articles += len(articles)

        mark_processed(filename)
        processed_count += 1

    print("\n==========================")
    print("Feeds processed:", processed_count)
    print("Total articles:", total_articles)
    print("==========================")


if __name__ == "__main__":
    run()