from collections import defaultdict

from core.utils.time_utils import TimeUtils


class EvolutionEngine:

    def __init__(self):
        self.resolution = "day"

    def build_temporal_clusters(self, clustered_chunks, cluster_labels):
        """Group chunks by narrative and temporal bucket.

        Uses the same day/hour auto-resolution strategy as TimelineEngine so
        single-calendar-day corpora still produce evolution snapshots.
        """

        day_groups = defaultdict(lambda: defaultdict(list))
        hour_groups = defaultdict(lambda: defaultdict(list))
        all_days = set()
        all_hours = set()

        for chunk in clustered_chunks:
            cluster = chunk["cluster"]
            label = cluster_labels.get(cluster, f"Cluster {cluster}")
            day = TimeUtils.parse_to_day(chunk.get("date"))
            hour = TimeUtils.parse_to_hour(chunk.get("date"))

            if day is not None:
                day_groups[label][day].append(chunk)
                all_days.add(day)

            if hour is not None:
                hour_groups[label][hour].append(chunk)
                all_hours.add(hour)

        if len(all_days) >= 2:
            self.resolution = "day"
            return day_groups
        if len(all_hours) >= 2:
            self.resolution = "hour"
            return hour_groups
        if day_groups:
            self.resolution = "day"
            return day_groups

        self.resolution = "hour"
        return hour_groups

    def detect_evolution(self, temporal_clusters):
        evolution_report = {}

        for narrative, dates in temporal_clusters.items():
            sorted_dates = sorted(dates.keys())
            if not sorted_dates:
                continue

            evolution_steps = []
            for date in sorted_dates:
                texts = [item["text"] for item in dates[date] if item.get("text")]
                if not texts:
                    continue
                combined = " ".join(texts[:5])
                evolution_steps.append({
                    "date": date,
                    "summary": combined[:220].strip(),
                    "volume": len(dates[date]),
                })

            if evolution_steps:
                evolution_report[narrative] = evolution_steps

        return evolution_report

    def display(self, evolution_report):
        print("\n" + "=" * 60)
        print("NARRATIVE EVOLUTION REPORT")
        print("=" * 60)

        for narrative, steps in evolution_report.items():
            print(f"\n{narrative}\n")
            for step in steps:
                print(f"{step['date']} → {step['summary']}")
                print("-" * 40)
