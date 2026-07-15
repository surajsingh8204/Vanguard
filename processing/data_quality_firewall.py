from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from config.settings import (
    CLOUDFLARE_PATTERNS,
    CSS_JS_HIT_THRESHOLD,
    CSS_JS_PATTERNS,
    HTML_TAG_RATIO_THRESHOLD,
    LANGUAGE_QUALITY_THRESHOLD,
    LOW_INFORMATION_THRESHOLD,
    MIN_CHUNK_LENGTH,
    NAVIGATION_HIT_THRESHOLD,
    NAVIGATION_PATTERNS,
)


@dataclass(slots=True)
class FirewallReport:
    attempted: int = 0
    accepted: int = 0
    cloudflare: int = 0
    html: int = 0
    css_js: int = 0
    navigation: int = 0
    short: int = 0
    duplicate: int = 0
    low_information: int = 0
    language_quality: int = 0


class DataQualityFirewall:
    """Validate article quality and reject low-value content."""

    def __init__(self) -> None:
        self.report = FirewallReport()
        self._existing_hashes: set[str] = set()

    def validate_batch(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.report = FirewallReport(attempted=len(articles))
        self._existing_hashes = set()
        accepted_articles: list[dict[str, Any]] = []

        for article in articles:
            is_valid, _reason = self.validate(article)
            if is_valid:
                accepted_articles.append(article)

        self.report.accepted = len(accepted_articles)
        self.print_report()
        return accepted_articles

    def validate(
        self,
        article_or_text: dict[str, Any] | str,
        existing_hashes: set[str] | None = None,
    ) -> tuple[bool, str]:
        text = self._extract_text(article_or_text)
        hash_store = existing_hashes if existing_hashes is not None else self._existing_hashes

        if self.is_cloudflare(text):
            self.report.cloudflare += 1
            return False, "cloudflare"

        if self.is_html_heavy(text):
            self.report.html += 1
            return False, "html"

        if self.is_css_or_js(text):
            self.report.css_js += 1
            return False, "css_js"

        if self.is_navigation(text):
            self.report.navigation += 1
            return False, "navigation"

        if self.is_too_short(text):
            self.report.short += 1
            return False, "short"

        is_duplicate, text_hash = self.is_duplicate(text, hash_store)
        if is_duplicate:
            self.report.duplicate += 1
            return False, "duplicate"

        if self.is_low_information(text):
            self.report.low_information += 1
            return False, "low_information"

        if self.is_language_quality(text):
            self.report.language_quality += 1
            return False, "language_quality"

        hash_store.add(text_hash)
        self.report.accepted += 1
        return True, "valid"

    def _extract_text(self, article_or_text: dict[str, Any] | str) -> str:
        if isinstance(article_or_text, dict):
            return str(article_or_text.get("content", ""))
        return str(article_or_text)

    def is_cloudflare(self, text: str) -> bool:
        lowered = text.lower()
        return any(pattern in lowered for pattern in CLOUDFLARE_PATTERNS)

    def is_html_heavy(self, text: str) -> bool:
        words = text.split()
        if not words:
            return True

        html_markers = text.count("<") + text.count(">") + text.count("</") + text.count("/>")
        return (html_markers / len(words)) > HTML_TAG_RATIO_THRESHOLD

    def is_css_or_js(self, text: str) -> bool:
        lowered = text.lower()
        hits = sum(1 for pattern in CSS_JS_PATTERNS if pattern in lowered)
        return hits >= CSS_JS_HIT_THRESHOLD

    def is_navigation(self, text: str) -> bool:
        lowered = text.lower()
        hits = sum(1 for pattern in NAVIGATION_PATTERNS if pattern in lowered)
        return hits >= NAVIGATION_HIT_THRESHOLD

    def is_too_short(self, text: str) -> bool:
        return len(text.split()) < MIN_CHUNK_LENGTH

    def is_duplicate(self, text: str, existing_hashes: set[str] | None = None) -> tuple[bool, str]:
        hash_store = existing_hashes if existing_hashes is not None else self._existing_hashes
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return text_hash in hash_store, text_hash

    def is_low_information(self, text: str) -> bool:
        words = [word.strip().lower() for word in text.split() if word.strip()]
        if not words:
            return True

        unique_ratio = len(set(words)) / len(words)
        return unique_ratio < LOW_INFORMATION_THRESHOLD

    def is_language_quality(self, text: str) -> bool:
        if not text:
            return True

        alphabetic_characters = sum(1 for character in text if character.isalpha())
        return (alphabetic_characters / len(text)) < LANGUAGE_QUALITY_THRESHOLD

    def print_report(self) -> None:
        print("========================================")
        print()
        print("FIREWALL REPORT")
        print()
        print("========================================")
        print()
        print(f"Attempted: {self.report.attempted}")
        print()
        print(f"Accepted: {self.report.accepted}")
        print()
        print(f"Cloudflare: {self.report.cloudflare}")
        print()
        print(f"HTML: {self.report.html}")
        print()
        print(f"CSS/JS: {self.report.css_js}")
        print()
        print(f"Navigation: {self.report.navigation}")
        print()
        print(f"Short: {self.report.short}")
        print()
        print(f"Duplicate: {self.report.duplicate}")
        print()
        print(f"Low Information: {self.report.low_information}")
        print()
        print(f"Language Quality: {self.report.language_quality}")
        print()
        print("========================================")
