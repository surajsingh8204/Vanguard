class ImpactAnalyzer:

    # ---------------------------------------------------
    # ANALYZE IMPACT
    # ---------------------------------------------------

    def generate(

        self,

        influence_scores,

        graph

    ):

        reports = []

        influence_items = (
            influence_scores.values()
            if isinstance(influence_scores, dict)
            else influence_scores
        )

        ranked_influence = sorted(

            influence_items,

            key=lambda x: x.get("score", 0),

            reverse=True

        )

        top_narratives = [

            x.get("narrative", x.get("label"))

            for x in ranked_influence[:10]

            if isinstance(x, dict)

        ]

        node_lookup = {

            data.get("label", node): node

            for node, data in graph.nodes(data=True)

        }

        for narrative in top_narratives:

            graph_node = node_lookup.get(
                narrative,
                narrative
            )

            if not graph.has_node(
                graph_node
            ):
                continue

            impacts = []

            neighbors = []

            for n in graph.neighbors(
                graph_node
            ):

                weight = graph[
                    graph_node
                ][n]["weight"]

                neighbors.append(
                    (n, weight)
                )

            neighbors.sort(

                key=lambda x: x[1],

                reverse=True

            )

            impacts = [

                graph.nodes[x[0]].get(
                    "label",
                    x[0]
                )

                for x in neighbors[:5]

            ]

            reports.append({

                "source":
                    narrative,

                "impacts":
                    impacts
            })

        return reports

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(

        self,

        reports

    ):

        print("\n" + "=" * 60)

        print(
            "🌐 CROSS-NARRATIVE IMPACT REPORT"
        )

        print("=" * 60)

        for report in reports:

            print(
                f"\n🧠 {report['source']}"
            )

            print(
                "\nLikely Impact Areas:"
            )

            for item in report[
                "impacts"
            ]:

                print(
                    f"→ {item}"
                )

            print(
                "-" * 40
            )
