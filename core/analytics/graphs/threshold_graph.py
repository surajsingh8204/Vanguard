import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


class NarrativeGraph:

    def __init__(

        self,

        similarity_threshold=0.55
    ):

        self.graph = nx.Graph()

        self.similarity_threshold = similarity_threshold

    # ---------------------------------------------------
    # BUILD NARRATIVE REPRESENTATIONS
    # ---------------------------------------------------

    def build_narrative_vectors(

        self,

        cluster_groups,

        cluster_labels
    ):

        narrative_vectors = {}

        narrative_dates = defaultdict(set)

        for cluster_id, items in cluster_groups.items():

            embeddings = np.array([
                x["embedding"]
                for x in items
            ])

            centroid = np.mean(
                embeddings,
                axis=0
            )

            narrative_vectors[cluster_id] = {

                "label": cluster_labels.get(
                    cluster_id,
                    f"Cluster {cluster_id}"
                ),

                "vector": centroid
            }

            for item in items:

                narrative_dates[cluster_id].add(
                    item["date"][:8]
                )

        return narrative_vectors, narrative_dates

    # ---------------------------------------------------
    # TEMPORAL OVERLAP
    # ---------------------------------------------------

    def temporal_overlap(

        self,

        dates_a,

        dates_b
    ):

        intersection = len(
            dates_a.intersection(dates_b)
        )

        union = len(
            dates_a.union(dates_b)
        )

        if union == 0:
            return 0

        return intersection / union

    # ---------------------------------------------------
    # BUILD GRAPH
    # ---------------------------------------------------

    def build(

        self,

        cluster_groups,

        cluster_labels
    ):

        vectors, narrative_dates = (
            self.build_narrative_vectors(
                cluster_groups,
                cluster_labels
            )
        )

        cluster_ids = list(vectors.keys())

        # ---------------------------------------------
        # ADD NODES
        # ---------------------------------------------

        for cluster_id in cluster_ids:

            self.graph.add_node(

                cluster_id,

                label=vectors[cluster_id]["label"]
            )

        # ---------------------------------------------
        # ADD EDGES
        # ---------------------------------------------

        for i in range(len(cluster_ids)):

            for j in range(i + 1, len(cluster_ids)):

                id_a = cluster_ids[i]
                id_b = cluster_ids[j]

                vec_a = vectors[id_a]["vector"]
                vec_b = vectors[id_b]["vector"]

                semantic_sim = cosine_similarity(
                    [vec_a],
                    [vec_b]
                )[0][0]

                temporal_sim = self.temporal_overlap(

                    narrative_dates[id_a],

                    narrative_dates[id_b]
                )

                edge_weight = (
                    semantic_sim * temporal_sim
                )

                if edge_weight >= self.similarity_threshold:

                    self.graph.add_edge(

                        id_a,

                        id_b,

                        weight=round(
                            float(edge_weight),
                            4
                        ),

                        semantic_similarity=round(
                            float(semantic_sim),
                            4
                        ),

                        temporal_overlap=round(
                            float(temporal_sim),
                            4
                        )
                    )

        return self.graph

    # ---------------------------------------------------
    # DISPLAY GRAPH SUMMARY
    # ---------------------------------------------------

    def display_summary(self):

        print("\n" + "=" * 60)
        print("🕸️ NARRATIVE GRAPH SUMMARY")
        print("=" * 60)

        print(
            f"\nNodes: {self.graph.number_of_nodes()}"
        )

        print(
            f"Edges: {self.graph.number_of_edges()}"
        )

        print("\n🔗 Narrative Relationships:\n")

        for u, v, data in self.graph.edges(data=True):

            label_u = self.graph.nodes[u]["label"]

            label_v = self.graph.nodes[v]["label"]

            print(
                f"{label_u}"
            )

            print("   ↔")

            print(
                f"{label_v}"
            )

            print(
                f"Weight: {data['weight']}"
            )

            print("-" * 40)