import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

import requests
import trafilatura
from bs4 import BeautifulSoup

from config.settings import (
    ARTICLE_FETCH_BACKOFF_SECONDS,
    ARTICLE_FETCH_RETRIES,
    ARTICLE_FETCH_TIMEOUT_SECONDS,
)


logger = logging.getLogger(__name__)


class ArticleExtractor:

    def __init__(self, max_workers=10, retries=ARTICLE_FETCH_RETRIES):

        self.max_workers = max_workers
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0 Safari/537.36"
                )
            }
        )

    def _fetch_html(self, url):

        last_error = None

        for attempt in range(self.retries):

            try:
                response = self.session.get(
                    url,
                    timeout=ARTICLE_FETCH_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                return response.text

            except requests.RequestException as exc:
                last_error = exc
                logger.warning(
                    "Fallback fetch failed for %s on attempt %s: %s",
                    url,
                    attempt + 1,
                    exc,
                )

                if attempt < self.retries - 1:
                    sleep(ARTICLE_FETCH_BACKOFF_SECONDS)

        logger.error("Unable to fetch article HTML for %s", url, exc_info=last_error)
        return None

    def _extract_trafilatura(self, url):

        try:
            downloaded = trafilatura.fetch_url(url)

            if not downloaded:
                return None

            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
            )

            if text:
                return self._normalize_text(text)

        except (AttributeError, TypeError, ValueError, requests.RequestException) as exc:
            logger.warning("Trafilatura extraction failed for %s: %s", url, exc)

        return None

    def _extract_beautifulsoup(self, url):

        html = self._fetch_html(url)
        if not html:
            return None, None

        try:
            soup = BeautifulSoup(html, "html.parser")

            for tag in soup(["script", "style", "noscript", "svg", "canvas", "header", "footer", "nav", "aside", "form"]):
                tag.decompose()

            title = None
            if soup.title and soup.title.string:
                title = self._normalize_text(soup.title.string)

            container = soup.find("article") or soup.find("main") or soup.body or soup

            paragraphs = [
                self._normalize_text(paragraph.get_text(" ", strip=True))
                for paragraph in container.find_all("p")
            ]

            if paragraphs:
                text = " ".join(paragraph for paragraph in paragraphs if paragraph)
            else:
                text = self._normalize_text(container.get_text(" ", strip=True))

            return text or None, title

        except (AttributeError, TypeError, ValueError) as exc:
            logger.warning("BeautifulSoup extraction failed for %s: %s", url, exc)
            return None, None

    def _normalize_text(self, text):

        if not text:
            return ""

        return " ".join(text.split()).strip()

    def _build_record(self, article, content, extraction_method, title=None):

        record = {
            "url": article.get("url"),
            "title": title or article.get("title"),
            "source": article.get("source"),
            "formatted_date": article.get("formatted_date"),
            "content": content,
            "extraction_method": extraction_method,
            "word_count": len(content.split()),
        }

        return record

    def extract_article(self, article):

        url = article.get("url")
        if not url:
            return None

        text = self._extract_trafilatura(url)
        if text:
            return self._build_record(article, text, "trafilatura")

        text, title = self._extract_beautifulsoup(url)
        if text:
            return self._build_record(article, text, "beautifulsoup", title=title)

        return None

    def _process_single(self, article):

        try:
            return self.extract_article(article)

        except (requests.RequestException, UnicodeDecodeError, ValueError, TypeError) as exc:
            logger.exception("Article extraction failed for %s", article.get("url"))
            return None

    def extract_batch(self, articles):

        print(f"Extracting content using {self.max_workers} workers...")

        results = [None] * len(articles)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            futures = {
                executor.submit(self._process_single, article): index
                for index, article in enumerate(articles)
            }

            for future in as_completed(futures):

                index = futures[future]

                try:
                    results[index] = future.result()

                except (requests.RequestException, UnicodeDecodeError, ValueError, TypeError) as exc:
                    logger.exception("Extraction worker failed")
                    results[index] = None

        extracted = [result for result in results if result]

        print("Extraction complete:", len(extracted))

        return extracted