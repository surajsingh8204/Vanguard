import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from core.utils.time_utils import TimeUtils


class GraphDiagnostics:

    def __init__(self):

        pass

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
    # ANALYZE EDGES
    # ---------------------------------------------------

    def analyze(

        self,

        cluster_groups,

        cluster_labels
    ):

        narrative_vectors = {}
        narrative_dates = {}

        # ---------------------------------------------
        # BUILD REPRESENTATIONS
        # ---------------------------------------------

        for cluster_id, items in cluster_groups.items():

            embeddings = np.array([
                x["embedding"]
                for x in items
            ])

            centroid = np.mean(
                embeddings,
                axis=0
            )

            dates = {
                day
                for day in (
                    TimeUtils.parse_to_day(item.get("date"))
                    for item in items
                )
                if day is not None
            }

            narrative_vectors[cluster_id] = centroid
            narrative_dates[cluster_id] = dates

        cluster_ids = list(
            narrative_vectors.keys()
        )

        diagnostics = []

        # ---------------------------------------------
        # PAIRWISE ANALYSIS
        # ---------------------------------------------

        for i in range(len(cluster_ids)):

            for j in range(i + 1, len(cluster_ids)):

                id_a = cluster_ids[i]
                id_b = cluster_ids[j]

                vec_a = narrative_vectors[id_a]
                vec_b = narrative_vectors[id_b]

                semantic_sim = cosine_similarity(

                    [vec_a],

                    [vec_b]

                )[0][0]

                temporal_sim = self.temporal_overlap(

                    narrative_dates[id_a],

                    narrative_dates[id_b]
                )

                final_score = (
                    semantic_sim * temporal_sim
                )

                diagnostics.append({

                    "cluster_a": cluster_labels.get(
                        id_a,
                        f"Cluster {id_a}"
                    ),

                    "cluster_b": cluster_labels.get(
                        id_b,
                        f"Cluster {id_b}"
                    ),

                    "semantic_similarity": round(
                        float(semantic_sim),
                        4
                    ),

                    "temporal_overlap": round(
                        float(temporal_sim),
                        4
                    ),

                    "final_score": round(
                        float(final_score),
                        4
                    )
                })

        diagnostics = sorted(

            diagnostics,

            key=lambda x: x["final_score"],

            reverse=True
        )

        return diagnostics

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(

        self,

        diagnostics,

        top_n=15
    ):

        print("\n" + "=" * 60)
        print("🧪 GRAPH DIAGNOSTICS REPORT")
        print("=" * 60)

        for item in diagnostics[:top_n]:

            print("\n🧠 Narrative Pair:\n")

            print(item["cluster_a"])

            print("↕")

            print(item["cluster_b"])

            print()

            print(
                f"Semantic Similarity: "
                f"{item['semantic_similarity']}"
            )

            print(
                f"Temporal Overlap: "
                f"{item['temporal_overlap']}"
            )

            print(
                f"Final Score: "
                f"{item['final_score']}"
            )

            print("-" * 50)