import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class TopKGraph:

    def __init__(self, k=3, min_similarity=0.30):

        self.k = k
        self.min_similarity = min_similarity
        self.graph = nx.Graph()

    def build(self, cluster_groups, cluster_labels):

        narrative_vectors = {}

        # ------------------------------------
        # CENTROIDS
        # ------------------------------------

        for cluster_id, items in cluster_groups.items():

            embeddings = np.array([
                x["embedding"]
                for x in items
            ])

            centroid = np.mean(
                embeddings,
                axis=0
            )

            narrative_vectors[cluster_id] = centroid

        cluster_ids = list(
            narrative_vectors.keys()
        )

        # ------------------------------------
        # ADD NODES
        # ------------------------------------

        for cluster_id in cluster_ids:

            self.graph.add_node(

                cluster_id,

                label=cluster_labels.get(
                    cluster_id,
                    f"Cluster {cluster_id}"
                )
            )

        # ------------------------------------
        # TOP-K EDGES
        # ------------------------------------

        for source_id in cluster_ids:

            source_vector = narrative_vectors[source_id]

            similarities = []

            for target_id in cluster_ids:

                if source_id == target_id:
                    continue

                target_vector = narrative_vectors[target_id]

                sim = cosine_similarity(

                    [source_vector],

                    [target_vector]

                )[0][0]

                similarities.append(
                    (target_id, float(sim))
                )

            similarities.sort(
                key=lambda x: x[1],
                reverse=True
            )


            # ------------------------------------
            # HYBRID FILTER
            # ------------------------------------

            filtered_neighbors = [

                item

                for item in similarities

                if item[1] >= self.min_similarity

            ]

            top_neighbors = filtered_neighbors[:self.k]

            print(
                f"\nCluster {source_id}"
            )

            print(
                f"Candidates above threshold: "
                f"{len(filtered_neighbors)}"
            )



            for neighbor_id, score in top_neighbors:

                self.graph.add_edge(

                    source_id,

                    neighbor_id,

                    weight=round(score, 4)
                )

        return self.graph

    def display_summary(self):

        print("\n" + "=" * 60)
        print("🕸️ TOP-K NARRATIVE GRAPH")
        print("=" * 60)

        print(
            f"\nNodes: {self.graph.number_of_nodes()}"
        )

        print(
            f"Edges: {self.graph.number_of_edges()}"
        )

        print("\nTop Relationships:\n")

        for u, v, data in self.graph.edges(data=True):

            print(
                f"{self.graph.nodes[u]['label']}"
            )

            print(" ↔ ")

            print(
                f"{self.graph.nodes[v]['label']}"
            )

            print(
                f"Weight: {data['weight']}"
            )

            print("-" * 40)