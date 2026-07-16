import math
class EmergingNarrativeDetector:

    def detect(self, spikes):

        emerging = []

        for spike in spikes:

            volume = spike.get(
                "volume",
                1
            )

            momentum = math.log1p(spike.get(
                "momentum",
                0
            ))

            z_score = spike.get(
                "z_score",
                0
            )

            # -------------------------
            # EMERGING SCORE
            # -------------------------

            score = (

                0.5 * momentum

                +

                0.5 * z_score

            )

            emerging.append({

                "narrative":
                spike["narrative"],

                "score":
                round(score, 2),

                "momentum":
                momentum,

                "z_score":
                z_score,

                "volume":
                volume
            })

        emerging.sort(

            key=lambda x:
            x["score"],

            reverse=True

        )

        return emerging

    def display(
        self,
        emerging
    ):

        print("\n" + "=" * 60)
        print("🚀 EMERGING NARRATIVES")
        print("=" * 60)

        if not emerging:

            print(
                "\nNo emerging narratives detected."
            )

            return

        for item in emerging[:10]:

            print(
                f"\n🧠 {item['narrative']}"
            )

            print(
                f"Emerging Score: "
                f"{item['score']}"
            )

            print(
                f"Momentum: "
                f"{item['momentum']}x"
            )

            print(
                f"Z-Score: "
                f"{item['z_score']}"
            )

            print(
                f"Volume: "
                f"{item['volume']}"
            )

            print("-" * 40)