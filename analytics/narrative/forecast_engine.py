import numpy as np


class ForecastEngine:

    def forecast(
        self,
        timeline,
        influence_scores,
        emerging_narratives
    ):

        emerging_lookup = {}

        for item in emerging_narratives:

            emerging_lookup[
                item["narrative"]
            ] = item["score"]

        influence_lookup = {}

        for _, item in influence_scores.items():

            influence_lookup[
                item["label"]
            ] = item["score"]

        forecasts = []

        for narrative, days in timeline.items():

            counts = list(
                days.values()
            )

            if len(counts) < 3:
                continue

            # -------------------------
            # TREND SLOPE
            # -------------------------

            x = np.arange(
                len(counts)
            )

            slope = np.polyfit(
                x,
                counts,
                1
            )[0]

            # -------------------------
            # RECENT MOMENTUM
            # -------------------------

            recent = counts[-1]

            previous = counts[-2]

            if previous == 0:

                momentum = recent

            else:

                momentum = (
                    recent / previous
                )

            # -------------------------
            # INFLUENCE AND EMERGENCE
            # -------------------------

            influence = influence_lookup.get(
                narrative,
                0
            )

            emergence = emerging_lookup.get(
                narrative,
                0
            )

            # -------------------------
            # FORECAST SCORE
            # -------------------------

            score = (

                0.4 * slope

                +

                0.2 * momentum

                +

                0.2 * influence

                +

                0.2 * emergence

            )

            forecasts.append({

                "narrative":
                narrative,

                "score":
                round(
                    float(score),
                    2
                ),

                "slope":
                round(
                    float(slope),
                    2
                ),

                "momentum":
                round(
                    float(momentum),
                    2
                ),

                "influence":
                round(
                    float(influence),
                    2
                ),

                "emergence":
                round(
                    float(emergence),
                    2
                ),

                "current_volume":
                recent
            })

        forecasts.sort(

            key=lambda x:
            x["score"],

            reverse=True

        )

        return forecasts

    def display(
        self,
        forecasts
    ):

        print("\n" + "=" * 60)
        print("🔮 NARRATIVE FORECAST")
        print("=" * 60)

        for item in forecasts[:10]:

            print(
                f"\n🧠 {item['narrative']}"
            )

            print(
                f"Forecast Score: "
                f"{item['score']}"
            )

            print(
                f"Trend Slope: "
                f"{item['slope']}"
            )

            print(
                f"Momentum: "
                f"{item['momentum']}"
            )

            print(
                f"Influence: "
                f"{item['influence']}"
            )

            print(
                f"Emergence: "
                f"{item['emergence']}"
            )

            print(
                f"Current Volume: "
                f"{item['current_volume']}"
            )

            print("-" * 40)