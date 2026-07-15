from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

import trafilatura
from bs4 import BeautifulSoup

from config.settings import ARTICLE_EXTRACT_WORKERS


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ExtractionReport:
    attempted: int = 0
    extracted: int = 0
    failed: int = 0
    trafilatura_success: int = 0
    beautifulsoup_success: int = 0


class ArticleExtractor:
    """Extract structured article content from raw HTML only."""

    def __init__(self, max_workers: int = ARTICLE_EXTRACT_WORKERS) -> None:
        self.max_workers = max_workers
        self.report = ExtractionReport()

    def extract_batch(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.report = ExtractionReport(attempted=len(articles))
        if not articles:
            self.print_report()
            return []

        results: list[dict[str, Any] | None] = [None] * len(articles)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single, article): index
                for index, article in enumerate(articles)
            }

            for future in as_completed(futures):
                index = futures[future]
                try:
                    results[index] = future.result()
                except (AttributeError, TypeError, ValueError):
                    logger.exception("Article extraction worker failed")
                    results[index] = None

        extracted = [result for result in results if result is not None]
        self.report.extracted = len(extracted)
        self.report.failed = self.report.attempted - self.report.extracted
        self.print_report()
        return extracted

    def extract_article(self, article: dict[str, Any]) -> dict[str, Any] | None:
        html = article.get("raw_html")
        if not html:
            return None

        trafilatura_record = self._extract_with_trafilatura(article, html)
        if trafilatura_record:
            self.report.trafilatura_success += 1
            return trafilatura_record

        beautifulsoup_record = self._extract_with_beautifulsoup(article, html)
        if beautifulsoup_record:
            self.report.beautifulsoup_success += 1
            return beautifulsoup_record

        return None

    def _process_single(self, article: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return self.extract_article(article)
        except (AttributeError, TypeError, ValueError):
            logger.exception("Article extraction failed for %s", article.get("url"))
            return None

    def _extract_with_trafilatura(self, article: dict[str, Any], html: str) -> dict[str, Any] | None:
        try:
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
            )
        except (AttributeError, TypeError, ValueError) as exc:
            logger.warning("Trafilatura extraction failed for %s: %s", article.get("url"), exc)
            return None

        normalized_content = self._normalize_text(content)
        if not normalized_content:
            return None

        title = article.get("title") or self._extract_title_from_html(html)
        return self._build_record(article, normalized_content, "trafilatura", title)

    def _extract_with_beautifulsoup(self, article: dict[str, Any], html: str) -> dict[str, Any] | None:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except (AttributeError, TypeError, ValueError) as exc:
            logger.warning("BeautifulSoup parsing failed for %s: %s", article.get("url"), exc)
            return None

        for tag in soup(
            ["script", "style", "noscript", "svg", "canvas", "header", "footer", "nav", "aside", "form"]
        ):
            tag.decompose()

        container = soup.find("article") or soup.find("main") or soup.body or soup
        paragraphs = [
            self._normalize_text(paragraph.get_text(" ", strip=True))
            for paragraph in container.find_all("p")
        ]
        content = " ".join(paragraph for paragraph in paragraphs if paragraph)
        if not content:
            content = self._normalize_text(container.get_text(" ", strip=True))
        if not content:
            return None

        title = article.get("title") or self._extract_title_from_soup(soup)
        return self._build_record(article, content, "beautifulsoup", title)

    def _build_record(
        self,
        article: dict[str, Any],
        content: str,
        extraction_method: str,
        title: str | None,
    ) -> dict[str, Any]:
        return {
            "url": article.get("url"),
            "title": title,
            "source": article.get("source"),
            "formatted_date": article.get("formatted_date"),
            "content": content,
            "word_count": len(content.split()),
            "extraction_method": extraction_method,
        }

    def _extract_title_from_html(self, html: str) -> str | None:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except (AttributeError, TypeError, ValueError):
            return None
        return self._extract_title_from_soup(soup)

    def _extract_title_from_soup(self, soup: BeautifulSoup) -> str | None:
        if soup.title and soup.title.string:
            return self._normalize_text(soup.title.string)

        heading = soup.find("h1")
        if heading:
            return self._normalize_text(heading.get_text(" ", strip=True))

        return None

    def _normalize_text(self, text: Any) -> str:
        if not text:
            return ""
        return " ".join(str(text).split()).strip()

    def print_report(self) -> None:
        print("========================================")
        print()
        print("EXTRACTION REPORT")
        print()
        print("========================================")
        print()
        print(f"Attempted: {self.report.attempted}")
        print()
        print(f"Extracted: {self.report.extracted}")
        print()
        print(f"Failed: {self.report.failed}")
        print()
        print(f"Trafilatura Success: {self.report.trafilatura_success}")
        print()
        print(f"BeautifulSoup Success: {self.report.beautifulsoup_success}")
        print()
        print("========================================")
