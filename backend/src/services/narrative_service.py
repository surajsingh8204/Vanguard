import logging
from math import ceil

from backend.src.services.artifact_service import artifact_service

logger = logging.getLogger(__name__)


class NarrativeService:

    def _paginate(self, items, page=1, limit=50):
        page = max(int(page), 1)
        limit = max(int(limit), 1)
        start = (page - 1) * limit
        end = start + limit
        total = len(items)
        return {
            "items": items[start:end],
            "page": page,
            "limit": limit,
            "total": total,
            "pages": ceil(total / limit) if total else 0,
        }

    def summary(self):
        clusters = artifact_service.load_json(
            "narrative/clusters.json",
            default={},
        )
        cluster_labels = artifact_service.load_json(
            "narrative/cluster_labels.json",
            default={},
        )
        subcluster_labels = artifact_service.load_json(
            "narrative/subcluster_labels.json",
            default={},
        )
        statistics = artifact_service.load_json(
            "narrative/statistics.json",
            default={},
        )
        sentiment = artifact_service.load_json(
            "narrative/sentiment.json",
            default={},
        )
        emerging = artifact_service.load_json(
            "narrative/emerging.json",
            default=[],
        )
        spikes = artifact_service.load_json(
            "narrative/spikes.json",
            default=[],
        )

        subcluster_count = sum(
            len(value) if isinstance(value, dict) else 1
            for value in subcluster_labels.values()
        )

        return {
            "metadata": {
                "cluster_count": len(clusters),
                "subcluster_count": subcluster_count,
                "statistics": statistics,
                "sentiment": sentiment,
                "top_insights": emerging[:5],
                "warnings": spikes[:5],
            },
            "cluster_labels": cluster_labels,
            "subcluster_labels": subcluster_labels,
            "statistics": statistics,
            "sentiment": sentiment,
            "top_insights": emerging[:5],
            "warnings": spikes[:5],
        }

    def _strip_heavy_fields(self, documents):
        """Drop embedding vectors and keep only fields the UI needs."""
        cleaned = []
        for document in documents or []:
            if not isinstance(document, dict):
                continue
            cleaned.append({
                "text": document.get("text"),
                "title": document.get("title"),
                "source": document.get("source"),
                "date": document.get("date"),
                "country": document.get("country"),
                "language": document.get("language"),
                "topic": document.get("topic"),
            })
        return cleaned

    def clusters(self, page=1, limit=25, cluster=None):
        clusters = artifact_service.load_json("narrative/clusters.json", default={})

        if cluster is not None:
            cluster = str(cluster)
            clusters = {cluster: clusters.get(cluster, [])}

        items = [
            {
                "cluster": key,
                "items": self._strip_heavy_fields(value),
            }
            for key, value in clusters.items()
        ]
        return self._paginate(items, page=page, limit=limit)


narrative_service = NarrativeService()