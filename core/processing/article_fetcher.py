from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from random import choice
from time import sleep
from typing import Any

import requests

from core.config.settings import (
    ARTICLE_FETCH_BACKOFF_SECONDS,
    ARTICLE_FETCH_RETRIES,
    ARTICLE_FETCH_TIMEOUT_SECONDS,
    ARTICLE_FETCH_USER_AGENTS,
    ARTICLE_FETCH_WORKERS,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FetchReport:
    attempted: int = 0
    succeeded: int = 0
    failed: int = 0


class ArticleFetcher:
    """Fetch article HTML without parsing or transforming page content."""

    def __init__(
        self,
        max_workers: int = ARTICLE_FETCH_WORKERS,
        retries: int = ARTICLE_FETCH_RETRIES,
        timeout_seconds: int = ARTICLE_FETCH_TIMEOUT_SECONDS,
        backoff_seconds: int = ARTICLE_FETCH_BACKOFF_SECONDS,
        user_agents: tuple[str, ...] = ARTICLE_FETCH_USER_AGENTS,
    ) -> None:
        self.max_workers = max_workers
        self.retries = retries
        self.timeout_seconds = timeout_seconds
        self.backoff_seconds = backoff_seconds
        self.user_agents = user_agents
        self.session = requests.Session()
        self.report = FetchReport()

    def fetch_batch(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.report = FetchReport(attempted=len(articles))
        if not articles:
            self.print_report()
            return []

        results: list[dict[str, Any] | None] = [None] * len(articles)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single, article): index
                for index, article in enumerate(articles)
            }

            for future in as_completed(futures):
                index = futures[future]

                try:
                    results[index] = future.result()
                except requests.RequestException:
                    logger.exception("Article fetch worker failed")
                    results[index] = None

        fetched = [result for result in results if result is not None]
        self.report.succeeded = len(fetched)
        self.report.failed = self.report.attempted - self.report.succeeded
        self.print_report()
        return fetched

    def _fetch_single(self, article: dict[str, Any]) -> dict[str, Any] | None:
        url = article.get("url")
        if not url:
            logger.warning("Skipping article without URL during fetch")
            return None

        html = self.fetch_html(url)
        if not html:
            return None

        fetched = dict(article)
        fetched["raw_html"] = html
        return fetched

    def fetch_html(self, url: str) -> str | None:
        last_error: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout_seconds,
                    headers={"User-Agent": self._select_user_agent()},
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                last_error = exc
                logger.warning(
                    "Fetch failed for %s on attempt %s/%s: %s",
                    url,
                    attempt,
                    self.retries,
                    exc,
                )
                if attempt < self.retries:
                    sleep(self.backoff_seconds)

        logger.error("Unable to fetch article HTML for %s", url, exc_info=last_error)
        return None

    def _select_user_agent(self) -> str:
        if not self.user_agents:
            return "Mozilla/5.0"
        return choice(self.user_agents)

    def print_report(self) -> None:
        print("========================================")
        print()
        print("FETCH REPORT")
        print()
        print("========================================")
        print()
        print(f"Attempted: {self.report.attempted}")
        print()
        print(f"Succeeded: {self.report.succeeded}")
        print()
        print(f"Failed: {self.report.failed}")
        print()
        print("========================================")
