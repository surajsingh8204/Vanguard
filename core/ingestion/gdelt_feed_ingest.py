import logging

import requests

from core.config.settings import GDELT_FEED_BASE_URL
from core.ingestion.feed_parser import parse_gkg
from core.ingestion.gdelt_client import download_feed, generate_feed_urls
from core.ingestion.raw_storage import load_processed, mark_processed, save_articles


logger = logging.getLogger(__name__)


class GDELTFeedIngest:

    def __init__(self, hours_back=24, base_url=GDELT_FEED_BASE_URL):

        self.hours_back = hours_back
        self.base_url = base_url
        self.session = requests.Session()

    def generate_feed_urls(self):

        return generate_feed_urls(
            hours_back=self.hours_back,
            base_url=self.base_url,
        )

    def download_feed(self, url):

        return download_feed(url, session=self.session)

    def parse_gkg(self, path):

        return parse_gkg(path)

    def load_processed(self):

        return load_processed()

    def mark_processed(self, filename):

        return mark_processed(filename)

    def save_articles(self, articles):

        return save_articles(articles)

    def run(self):

        urls = self.generate_feed_urls()
        print(
            f"Processing {len(urls)} feeds from the last {self.hours_back} hours"
        )

        feeds_processed = 0
        urls_discovered = 0
        collected_articles = []

        for url in urls:

            filename = url.split("/")[-1]

            path = self.download_feed(url)
            if not path:
                continue

            articles = self.parse_gkg(path)
            urls_discovered += len(articles)

            if articles:
                collected_articles.extend(articles)

            self.mark_processed(filename)
            feeds_processed += 1

        saved_path = self.save_articles(collected_articles)
        articles_saved = len(collected_articles) if saved_path else 0

        print("\n==========================")
        print("Feeds processed:", feeds_processed)
        print("URLs discovered:", urls_discovered)
        print("Total articles:", articles_saved)
        print("==========================")

        return {
            "feeds_processed": feeds_processed,
            "urls_discovered": urls_discovered,
            "total_articles": articles_saved,
        }


def run():
    return GDELTFeedIngest().run()


if __name__ == "__main__":
    run()
