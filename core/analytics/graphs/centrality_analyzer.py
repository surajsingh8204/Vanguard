import networkx as nx


class CentralityAnalyzer:

    def analyze(self, graph):

        results = {}

        # ----------------------------------
        # DEGREE CENTRALITY
        # ----------------------------------

        degree = nx.degree_centrality(graph)

        # ----------------------------------
        # PAGERANK
        # ----------------------------------

        pagerank = nx.pagerank(
            graph,
            weight="weight"
        )

        # ----------------------------------
        # BETWEENNESS
        # ----------------------------------

        betweenness = nx.betweenness_centrality(
            graph,
            weight="weight"
        )

        results["degree"] = degree
        results["pagerank"] = pagerank
        results["betweenness"] = betweenness

        return results

    def display(self, graph, results):

        print("\n" + "=" * 60)
        print("🏆 CENTRAL NARRATIVE ANALYSIS")
        print("=" * 60)

        # -------------------------------
        # PageRank
        # -------------------------------

        print("\n📈 Top Narratives (PageRank)\n")

        top_pr = sorted(

            results["pagerank"].items(),

            key=lambda x: x[1],

            reverse=True

        )[:10]

        for node, score in top_pr:

            label = graph.nodes[node]["label"]

            print(
                f"{label}"
            )

            print(
                f"Score: {score:.4f}"
            )

            print("-" * 40)

        # -------------------------------
        # Betweenness
        # -------------------------------

        print("\n🌉 Narrative Bridges\n")

        top_bt = sorted(

            results["betweenness"].items(),

            key=lambda x: x[1],

            reverse=True

        )[:10]

        for node, score in top_bt:

            label = graph.nodes[node]["label"]

            print(
                f"{label}"
            )

            print(
                f"Bridge Score: {score:.4f}"
            )

            print("-" * 40)