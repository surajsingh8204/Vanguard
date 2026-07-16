class InfluenceEngine:

    def normalize(self, values):

        if not values:
            return {}

        max_val = max(values.values())

        if max_val == 0:
            return {k: 0 for k in values}

        return {
            k: v / max_val
            for k, v in values.items()
        }

    def calculate(
        self,
        narrative_stats,
        centrality_results
    ):

        # ----------------------------------
        # NARRATIVE VOLUME
        # ----------------------------------

        volumes = {

            cluster_id: info["size"]

            for cluster_id, info

            in narrative_stats.items()
        }

        volume_norm = self.normalize(
            volumes
        )

        # ----------------------------------
        # PAGERANK
        # ----------------------------------

        pagerank_norm = self.normalize(
            centrality_results["pagerank"]
        )

        # ----------------------------------
        # BETWEENNESS
        # ----------------------------------

        betweenness_norm = self.normalize(
            centrality_results["betweenness"]
        )

        # ----------------------------------
        # COMBINED INFLUENCE
        # ----------------------------------

        influence_scores = {}

        for cluster_id in narrative_stats:

            volume_score = volume_norm.get(
                cluster_id,
                0
            )

            pagerank_score = pagerank_norm.get(
                cluster_id,
                0
            )

            betweenness_score = betweenness_norm.get(
                cluster_id,
                0
            )

            influence = (

                0.6 * volume_score

                +

                0.3 * pagerank_score

                +

                0.1 * betweenness_score

            )

            influence_scores[cluster_id] = {

                "label":
                narrative_stats[
                    cluster_id
                ]["label"],

                "score":
                round(
                    influence,
                    4
                ),

                "volume":
                narrative_stats[
                    cluster_id
                ]["size"],

                "volume_score":
                round(
                    volume_score,
                    4
                ),

                "pagerank_score":
                round(
                    pagerank_score,
                    4
                ),

                "betweenness_score":
                round(
                    betweenness_score,
                    4
                )
            }

        return influence_scores

    def display(
        self,
        influence_scores
    ):

        print("\n" + "=" * 60)
        print("🔥 NARRATIVE INFLUENCE RANKING")
        print("=" * 60)

        ranked = sorted(

            influence_scores.items(),

            key=lambda x:
            x[1]["score"],

            reverse=True

        )[:10]

        for rank, (
            cluster_id,
            info
        ) in enumerate(
            ranked,
            start=1
        ):

            print(f"\n#{rank}")

            print(
                info["label"]
            )

            print(
                f"Influence Score: "
                f"{info['score']:.4f}"
            )

            print(
                f"Volume: "
                f"{info['volume']}"
            )

            print(
                f"Volume Score: "
                f"{info['volume_score']:.4f}"
            )

            print(
                f"PageRank Score: "
                f"{info['pagerank_score']:.4f}"
            )

            print(
                f"Bridge Score: "
                f"{info['betweenness_score']:.4f}"
            )

            print("-" * 40)