import numpy as np


class SpikeDetector:

    def __init__(

        self,

        z_threshold=2.0,

        momentum_threshold=2.0
    ):

        self.z_threshold = z_threshold

        self.momentum_threshold = momentum_threshold

    # ---------------------------------------------------
    # DETECT SPIKES + MOMENTUM
    # ---------------------------------------------------

    def detect(self, timeline):

        spikes = []

        for narrative, days in timeline.items():

            counts = list(days.values())

            if len(counts) < 2:
                continue

            latest_day = list(days.keys())[-1]

            latest_count = counts[-1]

            previous_count = counts[-2]

            # ---------------------------------------------
            # MOMENTUM SCORE
            # ---------------------------------------------

            if previous_count == 0:

                momentum = float("inf")

            else:

                momentum = latest_count / previous_count

            # ---------------------------------------------
            # Z-SCORE
            # ---------------------------------------------

            mean = np.mean(counts)

            std = np.std(counts)

            if std == 0:

                z_score = 0

            else:

                z_score = (
                    latest_count - mean
                ) / std

            # ---------------------------------------------
            # DETECT SIGNAL
            # ---------------------------------------------

            if (
                z_score >= self.z_threshold
                or
                momentum >= self.momentum_threshold
            ):

                spikes.append({

                    "narrative": narrative,

                    "day": latest_day,

                    "count": latest_count,

                    "volume": sum(counts),

                    "momentum": round(
                        float(momentum),
                        2
                    ),

                    "z_score": round(
                        float(z_score),
                        2
                    )
                })

        return spikes

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(self, spikes):

        print("\n" + "=" * 60)
        print("🚨 NARRATIVE MOMENTUM REPORT")
        print("=" * 60)

        if len(spikes) == 0:

            print("\nNo significant narrative momentum detected.")

            return

        for spike in spikes:

            print(f"\n🧠 {spike['narrative']}")

            print(
                f"Date: {spike['day']}"
            )

            print(
                f"Mentions: {spike['count']}"
            )

            print(
                f"Momentum: {spike['momentum']}x"
            )

            print(
                f"Z-Score: {spike['z_score']}"
            )