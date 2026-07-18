import logging
from math import ceil

from backend.src.services.artifact_service import artifact_service

logger = logging.getLogger(__name__)


class GraphService:

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

        graph_summary = artifact_service.load_json(
            "graphs/graph_summary.json",
            default={},
        )
        communities = artifact_service.load_json(
            "graphs/communities.json",
            default=[],
        )
        centrality = artifact_service.load_json(
            "graphs/centrality.json",
            default={},
        )
        influencers = artifact_service.load_json(
            "graphs/influencers.json",
            default=[],
        )
        diagnostics = artifact_service.load_json(
            "graphs/graph_diagnostics.json",
            default=[],
        )
        influence_mappings = artifact_service.load_json(
            "graphs/influence_mappings.json",
            default=[],
        )

        top_influencers = []
        if isinstance(influencers, dict):
            top_influencers = sorted(
                (
                    {"id": key, **value}
                    for key, value in influencers.items()
                    if isinstance(value, dict)
                ),
                key=lambda item: item.get("score", 0),
                reverse=True,
            )
        elif isinstance(influencers, list):
            top_influencers = influencers

        return {
            "metadata": {
                "node_count": graph_summary.get("node_count", 0),
                "edge_count": graph_summary.get("edge_count", 0),
                "community_count": len(communities),
                "centrality_labels": list(centrality.keys()),
                "top_influencers": top_influencers[:10],
                "top_insights": diagnostics[:5],
            },
            "labels": {
                "communities": len(communities),
                "centrality": len(centrality),
                "influencers": len(influencers),
            },
            "statistics": graph_summary,
            "communities": communities,
            "centrality": centrality,
            "influencers": top_influencers,
            "influence_mappings": influence_mappings[:25] if isinstance(influence_mappings, list) else [],
            "diagnostics": diagnostics[:15],
            "warnings": diagnostics[:5],
        }

    def network(self, page=1, limit=100, cluster=None):
        nodes = artifact_service.load_json("graphs/nodes.json", default=[])
        edges = artifact_service.load_json("graphs/edges.json", default=[])

        if cluster is not None:
            try:
                cluster = int(cluster)
            except Exception:
                cluster = None

        if cluster is not None:
            nodes = [node for node in nodes if node.get("id") == cluster]
            edges = [
                edge for edge in edges
                if edge.get("source") == cluster or edge.get("target") == cluster
            ]

        return {
            "nodes": self._paginate(nodes, page=page, limit=limit),
            "edges": self._paginate(edges, page=page, limit=limit),
        }


graph_service = GraphService()