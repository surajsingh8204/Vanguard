import math


class EmergingNarrativeDetector:

    def detect(self, spikes):
        emerging = []

        for spike in spikes:
            volume = spike.get("volume", 1)
            raw_momentum = spike.get("momentum", 0)
            if not math.isfinite(raw_momentum) or raw_momentum < 0:
                momentum = 0.0
            else:
                momentum = math.log1p(raw_momentum)

            z_score = spike.get("z_score", 0)
            if not math.isfinite(z_score):
                z_score = 0.0

            score = 0.5 * momentum + 0.5 * z_score
            if not math.isfinite(score):
                score = 0.0

            emerging.append({
                "narrative": spike["narrative"],
                "score": round(float(score), 2),
                "momentum": round(float(momentum), 2),
                "z_score": round(float(z_score), 2),
                "volume": volume,
            })

        emerging.sort(key=lambda item: item["score"], reverse=True)
        return emerging

    def display(self, emerging):
        print("\n" + "=" * 60)
        print("EMERGING NARRATIVES")
        print("=" * 60)

        if not emerging:
            print("\nNo emerging narratives detected.")
            return

        for item in emerging[:10]:
            print(f"\n{item['narrative']}")
            print(f"Emerging Score: {item['score']}")
            print(f"Momentum: {item['momentum']}x")
            print(f"Z-Score: {item['z_score']}")
            print(f"Volume: {item['volume']}")
            print("-" * 40)
