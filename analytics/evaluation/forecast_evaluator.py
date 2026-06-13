class ForecastEvaluator:

    # ---------------------------------------------------
    # EVALUATE
    # ---------------------------------------------------

    def evaluate(

        self,

        timeline,

        baseline_forecasts,

        vanguard_forecasts

    ):

        # ---------------------------------------------
        # ACTUAL GROWTH
        # ---------------------------------------------

        actual_growths = []

        for narrative, days in timeline.items():

            counts = list(days.values())

            if len(counts) < 2:
                continue

            growth = (

                counts[-1]

                -

                counts[-2]

            )

            actual_growths.append({

                "narrative": narrative,

                "growth": growth

            })

        actual_growths.sort(

            key=lambda x: x["growth"],

            reverse=True

        )

        # ---------------------------------------------
        # TOP 10 ACTUAL
        # ---------------------------------------------

        top_actual = {

            x["narrative"]

            for x in actual_growths[:10]

        }

        # ---------------------------------------------
        # BASELINE
        # ---------------------------------------------

        top_baseline = {

            x["narrative"]

            for x in baseline_forecasts[:10]

        }

        baseline_hits = len(

            top_actual & top_baseline

        )

        # ---------------------------------------------
        # VANGUARD
        # ---------------------------------------------

        top_vanguard = {

            x["narrative"]

            for x in vanguard_forecasts[:10]

        }

        vanguard_hits = len(

            top_actual & top_vanguard

        )

        return {

            "actual_top_10":

                list(top_actual),

            "baseline_hits":

                baseline_hits,

            "vanguard_hits":

                vanguard_hits

        }

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(

        self,

        results

    ):

        print("\n" + "=" * 60)

        print("🧪 FORECAST EVALUATION")

        print("=" * 60)

        print(

            f"\nBaseline Hits: "

            f"{results['baseline_hits']} / 10"

        )

        print(

            f"Vanguard Hits: "

            f"{results['vanguard_hits']} / 10"

        )

        print("\nTop Actual Narratives:")

        for narrative in results["actual_top_10"]:

            print(

                f"• {narrative}"

            )