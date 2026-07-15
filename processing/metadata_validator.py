from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MetadataValidationReport:
    attempted: int = 0
    accepted: int = 0
    rejected_missing_fields: int = 0
    rejected_invalid_word_count: int = 0


class MetadataValidator:
    """Validate required article metadata without cleaning or content analysis."""

    REQUIRED_FIELDS = ("url", "title", "formatted_date", "content", "word_count")

    def __init__(self) -> None:
        self.report = MetadataValidationReport()

    def validate_batch(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.report = MetadataValidationReport(attempted=len(articles))
        valid_articles: list[dict[str, Any]] = []

        for article in articles:
            is_valid, reason = self.validate_article(article)
            if not is_valid:
                if reason == "missing_fields":
                    self.report.rejected_missing_fields += 1
                else:
                    self.report.rejected_invalid_word_count += 1
                continue
            valid_articles.append(article)

        self.report.accepted = len(valid_articles)
        self.print_report()
        return valid_articles

    def validate_article(self, article: dict[str, Any]) -> tuple[bool, str]:
        if any(not article.get(field) for field in self.REQUIRED_FIELDS):
            return False, "missing_fields"

        word_count = article.get("word_count")
        if not isinstance(word_count, int) or word_count <= 0:
            return False, "invalid_word_count"

        actual_word_count = len(str(article.get("content", "")).split())
        if actual_word_count != word_count:
            article["word_count"] = actual_word_count

        return True, "valid"

    def print_report(self) -> None:
        print("========================================")
        print()
        print("VALIDATION REPORT")
        print()
        print("========================================")
        print()
        print(f"Attempted: {self.report.attempted}")
        print()
        print(f"Accepted: {self.report.accepted}")
        print()
        print(f"Rejected Missing Fields: {self.report.rejected_missing_fields}")
        print()
        print(f"Rejected Invalid Word Count: {self.report.rejected_invalid_word_count}")
        print()
        print("========================================")
