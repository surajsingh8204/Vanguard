class InfluenceMapper:

    def generate(
        self,
        graph,
        influence_scores,
        top_n=10
    ):

        ranked = sorted(

            influence_scores.items(),

            key=lambda x: x[1]["score"],

            reverse=True

        )[:top_n]

        mappings = []

        for cluster_id, info in ranked:

            if not graph.has_node(cluster_id):
                continue

            neighbors = []

            for neighbor in graph.neighbors(
                cluster_id
            ):

                weight = graph[
                    cluster_id
                ][neighbor]["weight"]

                neighbors.append({

                    "id": neighbor,

                    "label":
                    graph.nodes[
                        neighbor
                    ]["label"],

                    "weight": weight
                })

            neighbors = sorted(

                neighbors,

                key=lambda x:
                x["weight"],

                reverse=True

            )[:5]

            mappings.append({

                "source":
                info["label"],

                "targets":
                neighbors
            })

        return mappings

    def display(
        self,
        mappings
    ):

        print("\n" + "=" * 60)
        print("🌐 NARRATIVE INFLUENCE MAP")
        print("=" * 60)

        for item in mappings:

            print(
                f"\n🧠 {item['source']}"
            )

            for target in item[
                "targets"
            ]:

                print(
                    f"   → "
                    f"{target['label']}"
                )

                print(
                    f"     Weight: "
                    f"{target['weight']}"
                )

            print("-" * 40)