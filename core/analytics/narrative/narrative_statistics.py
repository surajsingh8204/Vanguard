from collections import Counter


class NarrativeStatistics:

    def generate(
        self,
        clustered_chunks,
        cluster_labels
    ):

        stats = {}

        cluster_sizes = Counter(
            chunk["cluster"]
            for chunk in clustered_chunks
        )

        for cluster_id, size in cluster_sizes.items():

            stats[cluster_id] = {

                "label": cluster_labels.get(
                    cluster_id,
                    f"Cluster {cluster_id}"
                ),

                "size": size
            }

        return stats

    def display(self, stats):

        print("\n" + "=" * 60)
        print("📊 NARRATIVE STATISTICS")
        print("=" * 60)

        top_narratives = sorted(

            stats.items(),

            key=lambda x: x[1]["size"],

            reverse=True

        )[:10]

        for cluster_id, info in top_narratives:

            print(
                f"\n{info['label']}"
            )

            print(
                f"Chunks: {info['size']}"
            )

            print("-" * 40)