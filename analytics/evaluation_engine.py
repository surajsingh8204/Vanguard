import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


class EvaluationEngine:

    def __init__(self):

        pass

    # ---------------------------------------------------
    # CLUSTER COHERENCE
    # ---------------------------------------------------

    def cluster_coherence(self, clusters):

        coherence_scores = {}

        for cluster_id, items in clusters.items():

            embeddings = np.array([
                x["embedding"]
                for x in items
            ])

            if len(embeddings) < 2:
                continue

            sim_matrix = cosine_similarity(embeddings)

            avg_similarity = np.mean(sim_matrix)

            coherence_scores[cluster_id] = round(
                float(avg_similarity),
                4
            )

        return coherence_scores

    # ---------------------------------------------------
    # CLUSTER SEPARATION
    # ---------------------------------------------------

    def cluster_separation(self, clusters):

        centroids = {}

        # ---------------------------------------------
        # build centroids
        # ---------------------------------------------

        for cluster_id, items in clusters.items():

            embeddings = np.array([
                x["embedding"]
                for x in items
            ])

            centroid = np.mean(embeddings, axis=0)

            centroids[cluster_id] = centroid

        # ---------------------------------------------
        # compare centroids
        # ---------------------------------------------

        ids = list(centroids.keys())

        distances = []

        for i in range(len(ids)):

            for j in range(i + 1, len(ids)):

                sim = cosine_similarity(
                    [centroids[ids[i]]],
                    [centroids[ids[j]]]
                )[0][0]

                distances.append(sim)

        if len(distances) == 0:
            return 0

        return round(float(np.mean(distances)), 4)

    # ---------------------------------------------------
    # NARRATIVE PURITY
    # ---------------------------------------------------

    def narrative_purity(self, clusters):

        purity_scores = {}

        for cluster_id, items in clusters.items():

            texts = [
                x["text"]
                for x in items
            ]

            lengths = [
                len(t.split())
                for t in texts
            ]

            avg_length = np.mean(lengths)

            purity_scores[cluster_id] = round(
                float(avg_length),
                2
            )

        return purity_scores

    # ---------------------------------------------------
    # DISPLAY REPORT
    # ---------------------------------------------------

    def display_report(
        self,
        coherence,
        separation,
        purity,
        labels
    ):

        print("\n" + "=" * 60)
        print("📊 NARRATIVE EVALUATION REPORT")
        print("=" * 60)

        print("\n🌍 Global Cluster Separation:")
        print(separation)

        print("\n🧠 Cluster Quality:\n")

        for cluster_id in coherence:

            label = labels.get(
                cluster_id,
                f"Cluster {cluster_id}"
            )

            print(f"\n[{cluster_id}] {label}")

            print(
                f"Coherence: {coherence[cluster_id]}"
            )

            print(
                f"Purity: {purity.get(cluster_id, 0)}"
            )
