import csv
import json
import logging
import os
import time
import zipfile
from datetime import datetime, timedelta

import requests

from config.settings import (
    FEED_DOWNLOAD_BACKOFF_SECONDS,
    FEED_DOWNLOAD_RETRIES,
    FEED_DOWNLOAD_TIMEOUT_SECONDS,
    GDELT_FEED_BASE_URL,
    PROCESSED_FEEDS_FILE,
    RAW_ARTICLES_DIR,
    RAW_FEEDS_DIR,
)


logger = logging.getLogger(__name__)


class GDELTFeedIngest:

    def __init__(
        self,
        hours_back=24,
        base_url=GDELT_FEED_BASE_URL,
        raw_feed_dir=RAW_FEEDS_DIR,
        raw_articles_dir=RAW_ARTICLES_DIR,
        tracker_file=PROCESSED_FEEDS_FILE,
    ):

        self.hours_back = hours_back
        self.base_url = base_url
        self.raw_feed_dir = raw_feed_dir
        self.raw_articles_dir = raw_articles_dir
        self.tracker_file = tracker_file
        self.session = requests.Session()

    def generate_feed_urls(self):

        now = datetime.utcnow()
        minute = (now.minute // 15) * 15
        aligned_now = now.replace(minute=minute, second=0, microsecond=0)

        urls = []

        for index in range(self.hours_back * 4):

            timestamp = (
                aligned_now - timedelta(minutes=15 * index)
            ).strftime("%Y%m%d%H%M00")
            urls.append(f"{self.base_url}{timestamp}.gkg.csv.zip")

        return urls

    def download_feed(self, url):

        os.makedirs(self.raw_feed_dir, exist_ok=True)

        filename = url.split("/")[-1]
        path = os.path.join(self.raw_feed_dir, filename)

        if os.path.exists(path):
            logger.info("Already downloaded: %s", filename)
            return path

        for attempt in range(FEED_DOWNLOAD_RETRIES):

            try:
                logger.info("Downloading: %s", filename)
                response = self.session.get(
                    url,
                    timeout=FEED_DOWNLOAD_TIMEOUT_SECONDS,
                )
                response.raise_for_status()

                with open(path, "wb") as handle:
                    handle.write(response.content)

                return path

            except requests.RequestException as exc:
                logger.warning(
                    "Download failed for %s on attempt %s: %s",
                    filename,
                    attempt + 1,
                    exc,
                )

                if attempt < FEED_DOWNLOAD_RETRIES - 1:
                    time.sleep(FEED_DOWNLOAD_BACKOFF_SECONDS)

        logger.error("Unable to download feed: %s", filename)
        return None

    def parse_gkg(self, path):

        articles = []

        try:
            with zipfile.ZipFile(path, "r") as archive:

                file_name = archive.namelist()[0]

                with archive.open(file_name) as handle:

                    reader = csv.reader(
                        (
                            line.decode("utf-8", errors="ignore")
                            for line in handle
                        ),
                        delimiter="\t",
                    )

                    for row in reader:

                        try:
                            url = row[4]
                        except IndexError:
                            continue

                        if not url.startswith("http"):
                            continue

                        article = {
                            "date": row[1] if len(row) > 1 else None,
                            "source": row[3] if len(row) > 3 else None,
                            "url": url,
                        }

                        articles.append(article)

        except (FileNotFoundError, zipfile.BadZipFile, OSError, csv.Error) as exc:
            logger.exception("Error parsing feed %s: %s", path, exc)

        return articles

    def load_processed(self):

        if not os.path.exists(self.tracker_file):
            return set()

        try:
            with open(self.tracker_file, "r", encoding="utf-8") as handle:
                return set(line.strip() for line in handle if line.strip())

        except OSError as exc:
            logger.exception("Unable to read tracker file %s: %s", self.tracker_file, exc)
            return set()

    def mark_processed(self, filename):

        os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)

        try:
            with open(self.tracker_file, "a", encoding="utf-8") as handle:
                handle.write(filename + "\n")

        except OSError as exc:
            logger.exception("Unable to update tracker file %s: %s", self.tracker_file, exc)

    def save_articles(self, articles):

        if not articles:
            return None

        now = datetime.utcnow()
        folder = os.path.join(
            self.raw_articles_dir,
            str(now.year),
            str(now.month),
            str(now.day),
        )
        os.makedirs(folder, exist_ok=True)

        filename = os.path.join(
            folder,
            f"articles_{now.hour}_{now.minute}_{now.second}.json",
        )

        try:
            with open(filename, "w", encoding="utf-8") as handle:
                json.dump(articles, handle, indent=2, ensure_ascii=False)

            logger.info("Saved %s articles to %s", len(articles), filename)
            return filename

        except OSError as exc:
            logger.exception("Unable to save raw articles to %s: %s", filename, exc)
            return None

    def run(self):

        urls = self.generate_feed_urls()
        print(
            f"Processing {len(urls)} feeds from the last {self.hours_back} hours"
        )

        processed = self.load_processed()
        feeds_processed = 0
        articles_saved = 0

        for url in urls:

            filename = url.split("/")[-1]

            if filename in processed:
                logger.info("Already processed: %s", filename)
                continue

            path = self.download_feed(url)
            if not path:
                continue

            articles = self.parse_gkg(path)
            if articles:
                saved_path = self.save_articles(articles)
                if saved_path:
                    articles_saved += len(articles)

            self.mark_processed(filename)
            feeds_processed += 1

        print("\n==========================")
        print("Feeds processed:", feeds_processed)
        print("Total articles:", articles_saved)
        print("==========================")

        return {
            "feeds_processed": feeds_processed,
            "total_articles": articles_saved,
        }


def run():
    return GDELTFeedIngest().run()


if __name__ == "__main__":
    run()