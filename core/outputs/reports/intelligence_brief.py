class IntelligenceBriefGenerator:

    # ---------------------------------------------------
    # GENERATE BRIEFS
    # ---------------------------------------------------

    def generate(

        self,

        forecasts,

        influence_scores,

        warnings,

        graph

    ):

        briefs = []

        influence_items = (
            influence_scores.values()
            if isinstance(influence_scores, dict)
            else influence_scores
        )

        influence_lookup = {

            x.get("narrative", x.get("label")): x

            for x in influence_items

            if isinstance(x, dict)

        }

        warning_lookup = {

            x["narrative"]: x

            for x in warnings

        }

        node_lookup = {

            data.get("label", node): node

            for node, data in graph.nodes(data=True)

        }

        top_narratives = forecasts[:5]

        for item in top_narratives:

            narrative = item["narrative"]

            forecast_score = round(
                item["score"],
                2
            )

            influence = influence_lookup.get(
                narrative
            )

            warning = warning_lookup.get(
                narrative
            )

            # -------------------------------------
            # SIGNALS
            # -------------------------------------

            signals = []

            if influence:

                signals.append(
                    "High Influence"
                )

            if warning:

                signals.append(
                    "Early Warning"
                )

            if forecast_score > 2:

                signals.append(
                    "Strong Momentum"
                )

            # -------------------------------------
            # RELATED NARRATIVES
            # -------------------------------------

            related = []

            graph_node = node_lookup.get(
                narrative,
                narrative
            )

            if graph.has_node(graph_node):

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

                related = [

                    graph.nodes[x[0]].get(
                        "label",
                        x[0]
                    )

                    for x in neighbors[:3]

                ]

            # -------------------------------------
            # RISK LEVEL
            # -------------------------------------

            risk = "LOW"

            if warning:

                risk = "HIGH"

            elif influence:

                risk = "MEDIUM"

            # -------------------------------------
            # OUTLOOK
            # -------------------------------------

            if warning:

                outlook = (
                    "Rapid growth expected."
                )

            elif influence:

                outlook = (
                    "Strategically important narrative."
                )

            else:

                outlook = (
                    "Continue monitoring."
                )

            briefs.append({

                "narrative":
                    narrative,

                "forecast_score":
                    forecast_score,

                "signals":
                    signals,

                "related":
                    related,

                "risk":
                    risk,

                "outlook":
                    outlook
            })

        return briefs

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(

        self,

        briefs

    ):

        print("\n" + "=" * 60)

        print(
            "🧠 VANGUARD INTELLIGENCE BRIEFING"
        )

        print("=" * 60)

        for i, brief in enumerate(
            briefs,
            start=1
        ):

            print(
                f"\n📌 Brief #{i}"
            )

            print(
                f"\nNarrative:"
            )

            print(
                brief["narrative"]
            )

            print(
                f"\nRisk Level:"
            )

            print(
                brief["risk"]
            )

            print(
                "\nSignals:"
            )

            for signal in brief[
                "signals"
            ]:

                print(
                    f"✓ {signal}"
                )

            print(
                "\nRelated Narratives:"
            )

            if len(
                brief["related"]
            ) == 0:

                print(
                    "None"
                )

            else:

                for rel in brief[
                    "related"
                ]:

                    print(
                        f"• {rel}"
                    )

            print(
                "\nAssessment:"
            )

            print(
                brief["outlook"]
            )

            print(
                "\n" + "-" * 50
            )
