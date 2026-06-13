from collections import defaultdict


class RetrievalReranker:

    def rerank(

        self,

        results,

        max_per_subcluster=2,

        top_k=8

    ):

        grouped = defaultdict(list)

        for r in results:

            key = (

                r["cluster"],

                r.get(
                    "subcluster",
                    0
                )
            )

            grouped[key].append(r)

        final_results = []

        for key, chunks in grouped.items():

            chunks = sorted(

                chunks,

                key=lambda x:
                x["score"],

                reverse=True

            )

            final_results.extend(

                chunks[
                    :max_per_subcluster
                ]

            )

        final_results = sorted(

            final_results,

            key=lambda x:
            x["score"],

            reverse=True

        )

        return final_results[:top_k]