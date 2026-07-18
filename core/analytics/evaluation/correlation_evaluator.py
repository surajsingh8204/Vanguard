import numpy as np


def _safe_correlation(scores, truth):
    """Pearson correlation that returns None instead of NaN.

    np.corrcoef yields NaN for fewer than 2 points or zero-variance
    inputs; None keeps the JSON artifacts valid and lets the frontend
    show an explicit empty state.
    """

    if len(scores) < 2:
        return None

    if np.std(scores) == 0 or np.std(truth) == 0:
        return None

    corr = np.corrcoef(scores, truth)[0, 1]

    if not np.isfinite(corr):
        return None

    return round(float(corr), 4)


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

        baseline_corr = _safe_correlation(
            baseline_scores,
            baseline_truth
        )

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

        vanguard_corr = _safe_correlation(
            vanguard_scores,
            vanguard_truth
        )

        return {

            "baseline_correlation": baseline_corr,

            "vanguard_correlation": vanguard_corr,

            "baseline_samples": len(baseline_scores),

            "vanguard_samples": len(vanguard_scores),
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

        baseline = results["baseline_correlation"]
        vanguard = results["vanguard_correlation"]

        print(
            f"\nBaseline Correlation: "
            f"{'N/A' if baseline is None else baseline}"
        )

        print(
            f"Vanguard Correlation: "
            f"{'N/A' if vanguard is None else vanguard}"
        )

        baseline_value = baseline if baseline is not None else 0.0
        vanguard_value = vanguard if vanguard is not None else 0.0

        if vanguard_value > baseline_value:

            print(
                "\n✅ Vanguard Outperforms Baseline"
            )

        elif vanguard_value < baseline_value:

            print(
                "\n⚠ Baseline Outperforms Vanguard"
            )

        else:

            print(
                "\n🤝 Performance Equivalent"
            )