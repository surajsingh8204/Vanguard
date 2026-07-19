import math

import numpy as np


class ForecastEngine:

    @staticmethod
    def _series_features(counts):
        """Derive slope/momentum/recent volume for any non-empty count series."""

        values = [float(value) for value in counts if value is not None]
        if not values:
            return None

        recent = values[-1]
        if len(values) == 1:
            return {
                "slope": 0.0,
                "momentum": 1.0,
                "recent": recent,
            }

        previous = values[-2]
        if previous == 0:
            momentum = min(recent, 10.0) if recent > 0 else 1.0
        else:
            momentum = recent / previous

        if len(values) >= 2:
            x = np.arange(len(values), dtype=float)
            slope = float(np.polyfit(x, values, 1)[0])
        else:
            slope = 0.0

        if not math.isfinite(momentum):
            momentum = 10.0
        if not math.isfinite(slope):
            slope = 0.0

        return {
            "slope": slope,
            "momentum": float(momentum),
            "recent": recent,
        }

    def forecast(self, timeline, influence_scores, emerging_narratives):
        emerging_lookup = {
            item["narrative"]: item["score"]
            for item in emerging_narratives
        }
        influence_lookup = {
            item["label"]: item["score"]
            for _, item in influence_scores.items()
        }

        forecasts = []
        for narrative, days in timeline.items():
            features = self._series_features(list(days.values()))
            if features is None:
                continue

            influence = float(influence_lookup.get(narrative, 0) or 0)
            emergence = float(emerging_lookup.get(narrative, 0) or 0)
            volume_signal = math.log1p(max(features["recent"], 0.0))

            if len(days) >= 2:
                score = (
                    0.35 * features["slope"]
                    + 0.25 * features["momentum"]
                    + 0.20 * influence
                    + 0.20 * emergence
                )
            else:
                # Single-bucket corpora still produce ranked pressure scores.
                score = (
                    0.45 * influence
                    + 0.35 * volume_signal
                    + 0.20 * emergence
                )

            forecasts.append({
                "narrative": narrative,
                "score": round(float(score), 2),
                "slope": round(float(features["slope"]), 2),
                "momentum": round(float(features["momentum"]), 2),
                "influence": round(influence, 2),
                "emergence": round(emergence, 2),
                "current_volume": int(features["recent"]),
            })

        forecasts.sort(key=lambda item: item["score"], reverse=True)
        return forecasts

    def baseline_forecast(self, timeline):
        forecasts = []
        for narrative, days in timeline.items():
            features = self._series_features(list(days.values()))
            if features is None:
                continue

            volume_signal = math.log1p(max(features["recent"], 0.0))
            if len(days) >= 2:
                score = 0.6 * features["slope"] + 0.4 * features["momentum"]
            else:
                score = volume_signal

            forecasts.append({
                "narrative": narrative,
                "score": round(float(score), 2),
                "slope": round(float(features["slope"]), 2),
                "momentum": round(float(features["momentum"]), 2),
                "current_volume": int(features["recent"]),
            })

        forecasts.sort(key=lambda item: item["score"], reverse=True)
        return forecasts

    def display(self, forecasts):
        print("\n" + "=" * 60)
        print("NARRATIVE FORECAST")
        print("=" * 60)

        for item in forecasts[:10]:
            print(f"\n{item['narrative']}")
            print(f"Forecast Score: {item['score']}")
            print(f"Trend Slope: {item['slope']}")
            print(f"Momentum: {item['momentum']}")
            print(f"Influence: {item['influence']}")
            print(f"Emergence: {item['emergence']}")
            print(f"Current Volume: {item['current_volume']}")
            print("-" * 40)
