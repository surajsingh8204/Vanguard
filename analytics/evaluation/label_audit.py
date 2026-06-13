from collections import defaultdict


class LabelAudit:

    # ---------------------------------------------------
    # BUILD AUDIT
    # ---------------------------------------------------

    def analyze(

        self,

        clustered_chunks,

        cluster_labels,

        subcluster_labels

    ):

        cluster_stats = defaultdict(int)

        subcluster_stats = defaultdict(set)

        # ---------------------------------------------
        # COUNT VOLUME
        # ---------------------------------------------

        for chunk in clustered_chunks:

            cluster_id = chunk["cluster"]

            cluster_stats[cluster_id] += 1

            subcluster_id = chunk.get(
                "subcluster",
                0
            )

            sub_label = (

                subcluster_labels
                .get(cluster_id, {})
                .get(
                    subcluster_id,
                    "Unknown"
                )

            )

            subcluster_stats[
                cluster_id
            ].add(
                sub_label
            )

        # ---------------------------------------------
        # REPORT
        # ---------------------------------------------

        report = []

        for cluster_id in sorted(

            cluster_stats.keys()

        ):

            report.append({

                "cluster":

                    cluster_id,

                "label":

                    cluster_labels.get(
                        cluster_id,
                        "Unknown"
                    ),

                "volume":

                    cluster_stats[
                        cluster_id
                    ],

                "subclusters":

                    sorted(

                        list(

                            subcluster_stats[
                                cluster_id
                            ]

                        )

                    )

            })

        return report

    # ---------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------

    def display(

        self,

        report,

        top_n=20

    ):

        print(
            "\n" + "=" * 60
        )

        print(
            "🏷️ LABEL AUDIT REPORT"
        )

        print(
            "=" * 60
        )

        for item in report[:top_n]:

            print(
                f"\n🧠 Cluster "
                f"{item['cluster']}"
            )

            print(
                f"Label: "
                f"{item['label']}"
            )

            print(
                f"Volume: "
                f"{item['volume']}"
            )

            print(
                "\nTop Subclusters:"
            )

            for sub in item[
                "subclusters"
            ][:5]:

                print(
                    f"   • {sub}"
                )

            print(
                "-" * 40
            )