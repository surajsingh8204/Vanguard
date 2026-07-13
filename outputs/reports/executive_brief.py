class ExecutiveBriefGenerator:

    # ---------------------------------------------------
    # GENERATE EXECUTIVE BRIEF
    # ---------------------------------------------------

    def generate(

        self,

        forecasts,

        warnings,

        influence_scores,

        impact_reports

    ):

        brief = {

            "priority_narratives": [],

            "emerging_risks": [],

            "strategic_observations": []

        }

        # ---------------------------------------------
        # TOP FORECASTS
        # ---------------------------------------------

        for item in forecasts[:5]:

            brief[
                "priority_narratives"
            ].append(

                item["narrative"]

            )

        # ---------------------------------------------
        # RISKS
        # ---------------------------------------------

        for item in warnings[:5]:

            brief[
                "emerging_risks"
            ].append({

                "narrative":
                    item["narrative"],

                "warning_score":
                    round(
                        item.get(
                            "score",
                            item.get("warning_score", 0)
                        ),
                        2
                    )
            })

        # ---------------------------------------------
        # STRATEGIC OBSERVATIONS
        # ---------------------------------------------

        for item in impact_reports[:5]:

            observation = (

                f"{item['source']} "

                f"may influence "

                f"{len(item['impacts'])} "

                f"related narratives."

            )

            brief[
                "strategic_observations"
            ].append(
                observation
            )

        return brief

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(

        self,

        brief

    ):

        print("\n" + "=" * 60)

        print(
            "📋 EXECUTIVE DAILY BRIEF"
        )

        print("=" * 60)

        # -----------------------------------------
        # PRIORITY NARRATIVES
        # -----------------------------------------

        print(
            "\n🎯 Priority Narratives"
        )

        for n in brief[
            "priority_narratives"
        ]:

            print(
                f"• {n}"
            )

        # -----------------------------------------
        # EMERGING RISKS
        # -----------------------------------------

        print(
            "\n⚠ Emerging Risks"
        )

        for r in brief[
            "emerging_risks"
        ]:

            print(

                f"• {r['narrative']} "

                f"(Score: {r['warning_score']})"

            )

        # -----------------------------------------
        # STRATEGIC OBSERVATIONS
        # -----------------------------------------

        print(
            "\n🧠 Strategic Observations"
        )

        for obs in brief[
            "strategic_observations"
        ]:

            print(
                f"• {obs}"
            )

        print(
            "\n" + "=" * 60
        )
