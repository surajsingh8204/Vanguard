from collections import defaultdict

from core.utils.time_utils import TimeUtils


class TimelineEngine:

    def __init__(self):
        self.timeline = {}
        self.resolution = "day"

    def build(self, chunks, cluster_labels):
        """Build per-narrative count series.

        Uses daily buckets when the corpus spans multiple days. When everything
        lands on a single calendar day (common for smaller newest-feed runs),
        automatically switches to hourly buckets so spikes, evolution, and
        forecasts still have a usable time series.
        """

        day_counts = defaultdict(lambda: defaultdict(int))
        hour_counts = defaultdict(lambda: defaultdict(int))
        all_days = set()
        all_hours = set()

        for chunk in chunks:
            cluster = chunk["cluster"]
            label = cluster_labels.get(cluster, f"Cluster {cluster}")
            day = TimeUtils.parse_to_day(chunk.get("date"))
            hour = TimeUtils.parse_to_hour(chunk.get("date"))

            if day is not None:
                day_counts[label][day] += 1
                all_days.add(day)

            if hour is not None:
                hour_counts[label][hour] += 1
                all_hours.add(hour)

        if len(all_days) >= 2:
            source = day_counts
            self.resolution = "day"
        elif len(all_hours) >= 2:
            source = hour_counts
            self.resolution = "hour"
        elif day_counts:
            source = day_counts
            self.resolution = "day"
        else:
            source = hour_counts
            self.resolution = "hour"

        self.timeline = {
            label: TimeUtils.fill_contiguous_buckets(dict(sorted(days.items())))
            for label, days in source.items()
            if days
        }
        return self.timeline

    def display(self):
        print(f"\nNarrative Timelines ({self.resolution} resolution):\n")
        for narrative, days in self.timeline.items():
            print(f"\n{narrative}")
            for day, count in sorted(days.items()):
                print(f"{day} → {count}")
