from collections import defaultdict
from datetime import datetime


class TimelineEngine:

    def __init__(self):

        self.timeline = defaultdict(lambda: defaultdict(int))

    # ---------------------------------------------------
    # BUILD TIMELINE
    # ---------------------------------------------------

    def build(self, chunks, cluster_labels):

        for chunk in chunks:

            cluster = chunk["cluster"]

            label = cluster_labels.get(
                cluster,
                f"Cluster {cluster}"
            )

            raw_date = chunk.get("date")

            try:

                # GDELT format: YYYYMMDDHHMMSS
                dt = datetime.strptime(
                    raw_date,
                    "%Y%m%d%H%M%S"
                )

                day = dt.strftime("%Y-%m-%d")

            except:

                continue

            self.timeline[label][day] += 1

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