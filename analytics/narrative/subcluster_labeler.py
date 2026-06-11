from collections import defaultdict


class SubclusterLabeler:

    def generate_labels(
        self,
        clustered_chunks,
        labeler
    ):

        subcluster_labels = {}

        # ----------------------------------
        # GROUP BY
        # (main_cluster, subcluster)
        # ----------------------------------

        grouped = defaultdict(list)

        for chunk in clustered_chunks:

            main_cluster = chunk["cluster"]

            subcluster = chunk["subcluster"]

            grouped[
                (
                    main_cluster,
                    subcluster
                )
            ].append(
                chunk["text"]
            )

        # ----------------------------------
        # GENERATE LABELS
        # ----------------------------------

        for (
            main_cluster,
            subcluster
        ), texts in grouped.items():

            if subcluster == -1:
                continue

            try:

                label = labeler.generate_label(
                    texts[:20]
                )

            except Exception:

                label = (
                    f"Subcluster {subcluster}"
                )

            if main_cluster not in subcluster_labels:

                subcluster_labels[
                    main_cluster
                ] = {}

            subcluster_labels[
                main_cluster
            ][subcluster] = label

        return subcluster_labels