from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class EvolutionEngine:

    def __init__(self):

        pass

    # ---------------------------------------------------
    # BUILD TEMPORAL NARRATIVES
    # ---------------------------------------------------

    def build_temporal_clusters(

        self,

        clustered_chunks,

        cluster_labels
    ):

        temporal = defaultdict(
            lambda: defaultdict(list)
        )

        for chunk in clustered_chunks:

            cluster = chunk["cluster"]

            label = cluster_labels.get(
                cluster,
                f"Cluster {cluster}"
            )

            date = chunk["date"][:8]

            temporal[label][date].append(chunk)

        return temporal

    # ---------------------------------------------------
    # DETECT EVOLUTION
    # ---------------------------------------------------

    def detect_evolution(

        self,

        temporal_clusters
    ):

        evolution_report = {}

        for narrative, dates in temporal_clusters.items():

            sorted_dates = sorted(dates.keys())

            if len(sorted_dates) < 2:
                continue

            evolution_steps = []

            previous_embedding = None

            for date in sorted_dates:

                texts = [
                    x["text"]
                    for x in dates[date]
                ]

                combined = " ".join(texts[:5])

                evolution_steps.append({

                    "date": date,

                    "summary": combined[:150]
                })

            evolution_report[narrative] = evolution_steps

        return evolution_report

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(self, evolution_report):

        print("\n" + "=" * 60)
        print("🧬 NARRATIVE EVOLUTION REPORT")
        print("=" * 60)

        for narrative, steps in evolution_report.items():

            print(f"\n🧠 {narrative}\n")

            for step in steps:

                print(
                    f"{step['date']} → "
                    f"{step['summary']}"
                )

                print("-" * 40)