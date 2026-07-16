import community as community_louvain
from collections import defaultdict


class CommunityDetector:

    def detect(self, graph):

        partition = community_louvain.best_partition(
            graph,
            weight="weight"
        )

        communities = defaultdict(list)

        for node, community_id in partition.items():

            communities[community_id].append(node)

        return communities

    def display(

        self,

        communities,

        graph
    ):

        print("\n" + "=" * 60)
        print("🌐 NARRATIVE COMMUNITIES")
        print("=" * 60)

        for community_id, nodes in communities.items():

            print(
                f"\n🧠 Community {community_id}"
            )

            print("-" * 40)

            for node in nodes:

                label = graph.nodes[node]["label"]

                print(f"• {label}")