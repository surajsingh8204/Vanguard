from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PurifierReport:
    attempted: int = 0
    changed: int = 0
    unchanged: int = 0


class DocumentPurifier:
    """Clean article text without validating acceptance quality."""

    def __init__(self) -> None:
        self.report = PurifierReport()
        self._line_patterns = tuple(
            re.compile(pattern, re.IGNORECASE)
            for pattern in (
                r"^\s*copyright\b.*$",
                r"^\s*all rights reserved\b.*$",
                r"^\s*recommended stories\b.*$",
                r"^\s*recommended for you\b.*$",
                r"^\s*related articles\b.*$",
                r"^\s*related story\b.*$",
                r"^\s*you may also like\b.*$",
                r"^\s*share (this article|on)\b.*$",
                r"^\s*follow us\b.*$",
                r"^\s*newsletter\b.*$",
                r"^\s*subscribe\b.*$",
                r"^\s*sign up\b.*$",
                r"^\s*click here\b.*$",
                r"^\s*read more\b.*$",
                r"^\s*watch live\b.*$",
                r"^\s*(menu|home|privacy policy|terms of service|cookie preferences)\b.*$",
            )
        )
        self._email_pattern = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE)
        self._phone_pattern = re.compile(r"\+?\d[\d\s().-]{7,}\d")
        self._share_url_pattern = re.compile(r"https?://\S+", re.IGNORECASE)
        self._space_pattern = re.compile(r"\s+")

    def clean_batch(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.report = PurifierReport(attempted=len(articles))
        cleaned_articles: list[dict[str, Any]] = []

        for article in articles:
            cleaned_article = dict(article)
            original_content = str(article.get("content", ""))
            cleaned_content = self.clean(original_content)
            cleaned_article["content"] = cleaned_content
            cleaned_article["word_count"] = len(cleaned_content.split())

            if cleaned_content != original_content:
                self.report.changed += 1
            else:
                self.report.unchanged += 1

            cleaned_articles.append(cleaned_article)

        self.print_report()
        return cleaned_articles

    def clean(self, text: str) -> str:
        if not text:
            return ""

        lines = []
        for line in text.splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            if any(pattern.search(candidate) for pattern in self._line_patterns):
                continue
            lines.append(candidate)

        cleaned = "\n".join(lines)
        cleaned = self._email_pattern.sub(" ", cleaned)
        cleaned = self._phone_pattern.sub(" ", cleaned)
        cleaned = self._share_url_pattern.sub(" ", cleaned)
        cleaned = self._space_pattern.sub(" ", cleaned)
        return cleaned.strip()

    def is_valid(self, text: str) -> bool:
        if not text:
            return False

        if len(text.split()) < 40:
            return False

        bad_tokens = ("...", "###", "|", ">>", "<<")
        bad_count = sum(text.count(token) for token in bad_tokens)
        return bad_count <= 15

    def print_report(self) -> None:
        print("========================================")
        print()
        print("PURIFIER REPORT")
        print()
        print("========================================")
        print()
        print(f"Attempted: {self.report.attempted}")
        print()
        print(f"Changed: {self.report.changed}")
        print()
        print(f"Unchanged: {self.report.unchanged}")
        print()
        print("========================================")
