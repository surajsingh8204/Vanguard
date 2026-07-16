import numpy as np


class CorrelationEvaluator:

    # ---------------------------------------------------
    # EVALUATE
    # ---------------------------------------------------

    def evaluate(

        self,

        timeline,

        baseline_forecasts,

        vanguard_forecasts

    ):

        actual_growth = {}

        # ---------------------------------------------
        # ACTUAL GROWTH
        # ---------------------------------------------

        for narrative, days in timeline.items():

            counts = list(days.values())

            if len(counts) < 2:
                continue

            growth = (

                counts[-1]

                -

                counts[-2]

            )

            actual_growth[narrative] = growth

        # ---------------------------------------------
        # BASELINE CORRELATION
        # ---------------------------------------------

        baseline_scores = []
        baseline_truth = []

        for item in baseline_forecasts:

            narrative = item["narrative"]

            if narrative not in actual_growth:
                continue

            baseline_scores.append(
                item["score"]
            )

            baseline_truth.append(
                actual_growth[narrative]
            )

        baseline_corr = np.corrcoef(

            baseline_scores,

            baseline_truth

        )[0, 1]

        # ---------------------------------------------
        # VANGUARD CORRELATION
        # ---------------------------------------------

        vanguard_scores = []
        vanguard_truth = []

        for item in vanguard_forecasts:

            narrative = item["narrative"]

            if narrative not in actual_growth:
                continue

            vanguard_scores.append(
                item["score"]
            )

            vanguard_truth.append(
                actual_growth[narrative]
            )

        vanguard_corr = np.corrcoef(

            vanguard_scores,

            vanguard_truth

        )[0, 1]

        return {

            "baseline_correlation":

                round(
                    float(baseline_corr),
                    4
                ),

            "vanguard_correlation":

                round(
                    float(vanguard_corr),
                    4
                )
        }

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(
        self,
        results
    ):

        print("\n" + "=" * 60)

        print(
            "📈 FORECAST CORRELATION EVALUATION"
        )

        print("=" * 60)

        print(
            f"\nBaseline Correlation: "
            f"{results['baseline_correlation']}"
        )

        print(
            f"Vanguard Correlation: "
            f"{results['vanguard_correlation']}"
        )

        if (

            results[
                "vanguard_correlation"
            ]

            >

            results[
                "baseline_correlation"
            ]

        ):

            print(
                "\n✅ Vanguard Outperforms Baseline"
            )

        elif (

            results[
                "vanguard_correlation"
            ]

            <

            results[
                "baseline_correlation"
            ]

        ):

            print(
                "\n⚠ Baseline Outperforms Vanguard"
            )

        else:

            print(
                "\n🤝 Performance Equivalent"
            )