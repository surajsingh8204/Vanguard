from __future__ import annotations

import re
from collections import Counter
from typing import Any


class ClusterLabeler:
    CLICKBAIT_WORDS = {
        "breaking",
        "watch",
        "live",
        "update",
        "updates",
        "shocking",
        "viral",
        "exclusive",
        "must",
        "read",
        "revealed",
        "latest",
        "today",
        "now",
        "video",
        "story",
        "stories",
        "report",
        "reports",
    }

    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
        "into", "is", "it", "of", "on", "or", "that", "the", "their", "this",
        "to", "was", "were", "will", "with", "after", "before", "over", "under",
        "amid", "during", "says", "say", "said", "new", "news",
    }

    ENTITY_PATTERN = re.compile(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}))*\b")
    TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")

    def __init__(self, top_n: int = 6) -> None:
        self.top_n = top_n

    def generate_label(self, items: list[Any]) -> str:
        texts = self._collect_texts(items)
        if not texts:
            return "Unknown Narrative"

        entities = self._extract_entities(texts)
        keywords = self._extract_keywords(texts)
        parts = self._build_label_parts(entities, keywords)

        if not parts:
            return "Unknown Narrative"

        label = " ".join(parts[:8]).strip()
        if len(label.split()) < 4 and keywords:
            extra = [word for word, _ in keywords if word.title() not in parts]
            label = " ".join((parts + [word.title() for word in extra])[:6]).strip()

        return label or "Unknown Narrative"

    def _collect_texts(self, items: list[Any]) -> list[str]:
        texts: list[str] = []
        for item in items:
            if isinstance(item, dict):
                for key in ("title", "topic", "text"):
                    value = item.get(key)
                    if isinstance(value, str) and value.strip():
                        texts.append(value.strip())
            elif isinstance(item, str) and item.strip():
                texts.append(item.strip())
        return texts

    def _extract_entities(self, texts: list[str]) -> list[tuple[str, int]]:
        counter: Counter[str] = Counter()
        for text in texts:
            for match in self.ENTITY_PATTERN.findall(text):
                candidate = " ".join(match.split())
                if not candidate:
                    continue
                lowered_tokens = [token.lower() for token in candidate.split()]
                if all(token in self.STOPWORDS or token in self.CLICKBAIT_WORDS for token in lowered_tokens):
                    continue
                counter[candidate] += 1
        return counter.most_common(self.top_n)

    def _extract_keywords(self, texts: list[str]) -> list[tuple[str, int]]:
        counter: Counter[str] = Counter()
        for text in texts:
            for token in self.TOKEN_PATTERN.findall(text.lower()):
                if token in self.STOPWORDS or token in self.CLICKBAIT_WORDS:
                    continue
                counter[token] += 1
        return counter.most_common(self.top_n * 2)

    def _build_label_parts(
        self,
        entities: list[tuple[str, int]],
        keywords: list[tuple[str, int]],
    ) -> list[str]:
        parts: list[str] = []

        for entity, _count in entities:
            normalized = entity.strip()
            if normalized and normalized not in parts:
                parts.append(normalized)
            if len(parts) >= 3:
                break

        for keyword, _count in keywords:
            normalized = keyword.title()
            if normalized not in parts:
                parts.append(normalized)
            if len(parts) >= 6:
                break

        return parts
