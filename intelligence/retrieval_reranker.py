from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


class RetrievalReranker:
    TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z'-]{1,}")
    ENTITY_PATTERN = re.compile(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}))*\b")

    def rerank(
        self,
        results: list[dict[str, Any]],
        query: str,
        expanded_terms: list[str] | None = None,
        max_per_subcluster: int = 2,
        top_k: int = 8,
    ) -> list[dict[str, Any]]:
        query_terms = self._tokenize(" ".join([query] + (expanded_terms or [])))
        query_entities = self._extract_entities(" ".join([query] + (expanded_terms or [])))

        scored_results: list[dict[str, Any]] = []
        for result in results:
            vector_similarity = self._normalize_score(result.get("score", 0.0))
            text_terms = self._tokenize(result.get("text", ""))
            title_terms = self._tokenize(result.get("title", ""))
            doc_entities = self._extract_entities(
                " ".join(
                    [
                        str(result.get("title", "")),
                        str(result.get("topic", "")),
                        str(result.get("text", "")),
                    ]
                )
            )

            keyword_overlap = self._overlap_score(query_terms, text_terms)
            title_similarity = self._overlap_score(query_terms, title_terms)
            entity_overlap = self._overlap_score(query_entities, doc_entities)

            reranker_score = (
                (0.35 * vector_similarity)
                + (0.30 * keyword_overlap)
                + (0.20 * title_similarity)
                + (0.15 * entity_overlap)
            )

            enriched = dict(result)
            enriched["vector_similarity"] = vector_similarity
            enriched["keyword_overlap"] = keyword_overlap
            enriched["title_similarity"] = title_similarity
            enriched["entity_overlap"] = entity_overlap
            enriched["reranker_score"] = reranker_score
            scored_results.append(enriched)

        grouped: dict[tuple[Any, Any], list[dict[str, Any]]] = defaultdict(list)
        for result in scored_results:
            key = (result.get("cluster"), result.get("subcluster", 0))
            grouped[key].append(result)

        diversified: list[dict[str, Any]] = []
        for chunks in grouped.values():
            ranked = sorted(
                chunks,
                key=lambda item: item["reranker_score"],
                reverse=True,
            )
            diversified.extend(ranked[:max_per_subcluster])

        diversified.sort(key=lambda item: item["reranker_score"], reverse=True)
        return diversified[:top_k]

    def _tokenize(self, text: str) -> set[str]:
        return {
            token.lower()
            for token in self.TOKEN_PATTERN.findall(text or "")
        }

    def _extract_entities(self, text: str) -> set[str]:
        return {
            " ".join(match.split()).lower()
            for match in self.ENTITY_PATTERN.findall(text or "")
            if match.strip()
        }

    def _overlap_score(self, left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        intersection = len(left.intersection(right))
        union = len(left.union(right))
        if union == 0:
            return 0.0
        return intersection / union

    def _normalize_score(self, score: float) -> float:
        return max(0.0, min(1.0, (float(score) + 1.0) / 2.0))
