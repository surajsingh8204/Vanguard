import logging
import os
import time
from datetime import datetime, timedelta

import requests

from config.settings import (
    FEED_DOWNLOAD_BACKOFF_SECONDS,
    FEED_DOWNLOAD_RETRIES,
    FEED_DOWNLOAD_TIMEOUT_SECONDS,
    GDELT_FEED_BASE_URL,
    RAW_FEEDS_DIR,
)


logger = logging.getLogger(__name__)


def generate_feed_urls(hours_back=24, base_url=GDELT_FEED_BASE_URL):

    now = datetime.utcnow()
    minute = (now.minute // 15) * 15
    aligned_now = now.replace(minute=minute, second=0, microsecond=0)

    urls = []

    for index in range(hours_back * 4):

        timestamp = (
            aligned_now - timedelta(minutes=15 * index)
        ).strftime("%Y%m%d%H%M00")
        urls.append(f"{base_url}{timestamp}.gkg.csv.zip")

    return urls


def download_feed(url, session=None, raw_feed_dir=RAW_FEEDS_DIR):

    os.makedirs(raw_feed_dir, exist_ok=True)

    http_session = session or requests.Session()
    filename = url.split("/")[-1]
    path = os.path.join(raw_feed_dir, filename)

    if os.path.exists(path):
        logger.info("Already downloaded: %s", filename)
        return path

    for attempt in range(FEED_DOWNLOAD_RETRIES):

        try:
            logger.info("Downloading: %s", filename)
            response = http_session.get(
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
