import math

import numpy as np


class SpikeDetector:

    def __init__(self, z_threshold=2.0, momentum_threshold=2.0):
        self.z_threshold = z_threshold
        self.momentum_threshold = momentum_threshold

    def detect(self, timeline):
        spikes = []

        for narrative, days in timeline.items():
            counts = [float(value) for value in days.values()]
            if len(counts) < 2:
                continue

            latest_day = list(days.keys())[-1]
            latest_count = counts[-1]
            previous_count = counts[-2]

            if previous_count == 0:
                momentum = min(latest_count, 10.0) if latest_count > 0 else 1.0
            else:
                momentum = latest_count / previous_count

            if not math.isfinite(momentum):
                momentum = 10.0

            mean = float(np.mean(counts))
            std = float(np.std(counts))
            z_score = 0.0 if std == 0 else (latest_count - mean) / std
            if not math.isfinite(z_score):
                z_score = 0.0

            if (
                z_score >= self.z_threshold
                or momentum >= self.momentum_threshold
            ):
                spikes.append({
                    "narrative": narrative,
                    "day": latest_day,
                    "count": int(latest_count),
                    "volume": int(sum(counts)),
                    "momentum": round(float(momentum), 2),
                    "z_score": round(float(z_score), 2),
                })

        spikes.sort(key=lambda item: item["z_score"], reverse=True)
        return spikes

    def display(self, spikes):
        print("\n" + "=" * 60)
        print("NARRATIVE MOMENTUM REPORT")
        print("=" * 60)

        if not spikes:
            print("\nNo significant narrative momentum detected.")
            return

        for spike in spikes:
            print(f"\n{spike['narrative']}")
            print(f"Date: {spike['day']}")
            print(f"Mentions: {spike['count']}")
            print(f"Momentum: {spike['momentum']}x")
            print(f"Z-Score: {spike['z_score']}")
