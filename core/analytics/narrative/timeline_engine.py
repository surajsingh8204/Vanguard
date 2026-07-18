from collections import defaultdict

from core.utils.time_utils import TimeUtils


class TimelineEngine:

    def __init__(self):

        self.timeline = defaultdict(lambda: defaultdict(int))

    # ---------------------------------------------------
    # BUILD TIMELINE
    # ---------------------------------------------------

    def build(self, chunks, cluster_labels):

        counts = defaultdict(lambda: defaultdict(int))

        for chunk in chunks:

            cluster = chunk["cluster"]

            label = cluster_labels.get(
                cluster,
                f"Cluster {cluster}"
            )

            day = TimeUtils.parse_to_day(
                chunk.get("date")
            )

            if day is None:
                continue

            counts[label][day] += 1

        # Downstream engines (spikes, forecasts, evaluation) read
        # day counts in insertion order, so keep days chronological.
        self.timeline = {
            label: dict(sorted(days.items()))
            for label, days in counts.items()
        }

        return self.timeline

    # ---------------------------------------------------
    # SHOW TIMELINE
    # ---------------------------------------------------

    def display(self):

        print("\n📈 Narrative Timelines:\n")

        for narrative, days in self.timeline.items():

            print(f"\n🧠 {narrative}")

            sorted_days = sorted(days.items())

            for day, count in sorted_days:

                print(f"{day} → {count}")