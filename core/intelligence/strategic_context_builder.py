class StrategicContextBuilder:

    # ---------------------------------------------------
    # BUILD STRATEGIC CONTEXT
    # ---------------------------------------------------

    def build(

        self,

        forecasts,

        warnings,

        influence_scores,

        impact_reports

    ):

        context = []

        # ---------------------------------------------
        # TOP FORECASTS
        # ---------------------------------------------

        context.append(
            "TOP FORECASTED NARRATIVES:"
        )

        for item in forecasts[:5]:

            context.append(

                f"- {item['narrative']} "
                f"(Forecast Score: "
                f"{round(item['score'],2)})"

            )

        # ---------------------------------------------
        # WARNINGS
        # ---------------------------------------------

        context.append(
            "\nEARLY WARNINGS:"
        )

        for item in warnings[:5]:

            context.append(

                f"- {item['narrative']} "
                f"(Warning Score: "
                f"{round(item.get('score', item.get('warning_score', 0)),2)})"

            )

        # ---------------------------------------------
        # INFLUENCE
        # ---------------------------------------------

        context.append(
            "\nHIGH INFLUENCE NARRATIVES:"
        )

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

        for item in ranked_influence[:5]:

            context.append(

                f"- {item.get('narrative', item.get('label'))}"

            )

        # ---------------------------------------------
        # IMPACTS
        # ---------------------------------------------

        context.append(
            "\nNARRATIVE IMPACTS:"
        )

        for item in impact_reports[:5]:

            context.append(

                f"- {item['source']} "
                f"impacts "
                f"{', '.join(item['impacts'][:3])}"

            )

        return "\n".join(context)
