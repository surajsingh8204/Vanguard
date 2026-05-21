import json
from collections import Counter

from embeddings.embedding_services import EmbeddingService
from vectorstore.faiss_store import VectorStore
from intelligence.rag_engine import RAGEngine

from processing.hdbscan_cluster import HDBSCANClusterer
from processing.subcluster import SubClusterer
from analytics.cluster_labeler import ClusterLabeler
from processing.document_purifier import DocumentPurifier
from analytics.timeline_engine import TimelineEngine


class AIPipeline:

    def __init__(self):

        print("Loading embedding model...")
        self.embedding_service = EmbeddingService()

        print("Initializing RAG engine...")
        self.rag = RAGEngine()

        self.vector_store = None

    # ---------------------------------------------------
    # TEXT CHUNKING
    # ---------------------------------------------------

    def chunk_text(self, text, chunk_size=300):

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):

            chunk = " ".join(words[i:i + chunk_size])

            if len(chunk.strip()) > 50:
                chunks.append(chunk)

        return chunks

    # ---------------------------------------------------
    # BUILD VECTOR DATABASE
    # ---------------------------------------------------

    def build_vector_db(self, articles):

        print("Building vector database...")

        all_chunks = []
        purifier = DocumentPurifier()

        for article in articles:

            if not article.get("content"):
                continue
            
            #---------------------------------------------------
            # PURIFY DOCUMENT
            #---------------------------------------------------
            cleaned = purifier.clean(article["content"])

            #---------------------------------------------------
            # QUALITY CHECK
            #---------------------------------------------------
            if not purifier.is_valid(cleaned):
                continue
            
            #---------------------------------------------------
            # CHUNKING
            #---------------------------------------------------
            chunks = self.chunk_text(cleaned)
            article_date = article.get("date", "unknown")
            for chunk in chunks:

                all_chunks.append({
                    "text": chunk,
                    "date": article_date
                })

        print("Total chunks:", len(all_chunks))

        # ---------------------------------------------------
        # EMBEDDINGS
        # ---------------------------------------------------

        texts = [x["text"] for x in all_chunks]

        embeddings = self.embedding_service.embed(texts)

        # ---------------------------------------------------
        # MAIN CLUSTERING
        # ---------------------------------------------------

        print("Running main narrative clustering...")

        labeler = ClusterLabeler()

        self.cluster_labels = {}

        clusterer = HDBSCANClusterer(
            min_cluster_size=12,
            min_samples=4
        )

        labels = clusterer.cluster(embeddings)

        # ---------------------------------------------------
        # GROUP BY MAIN CLUSTER
        # ---------------------------------------------------

        cluster_groups = {}

        for i, label in enumerate(labels):

            if label == -1:
                continue

            if label not in cluster_groups:
                cluster_groups[label] = []

            cluster_groups[label].append({
                "text": all_chunks[i],
                "embedding": embeddings[i],
                "date": all_chunks[i]["date"]
            })

        print("Main clusters found:", len(cluster_groups))

        # ---------------------------------------------------
        # SUBCLUSTERING
        # ---------------------------------------------------

        print("Running hierarchical sub-clustering...")

        subclusterer = SubClusterer()

        clustered_chunks = []
        filtered_embeddings = []

        for main_cluster, items in cluster_groups.items():

            # ---------------------------------------------------
            # GENERATE MAIN CLUSTER LABEL
            # ---------------------------------------------------

            cluster_texts = [
                x["text"]["text"]
                for x in items
            ]

            cluster_label = labeler.generate_label(
                cluster_texts
                )

            self.cluster_labels[int(main_cluster)] = cluster_label

            cluster_embeddings = [x["embedding"] for x in items]

            # small clusters skip subclustering
            if len(cluster_embeddings) < 5:

                for item in items:

                    clustered_chunks.append({
                        "text": item["text"],
                        "cluster": int(main_cluster),
                        "subcluster": 0
                    })

                    filtered_embeddings.append(item["embedding"])

                continue

            # ---------------------------------------------
            # RUN SUBCLUSTERING
            # ---------------------------------------------

            sub_labels = subclusterer.cluster(cluster_embeddings)

            for idx, item in enumerate(items):

                clustered_chunks.append({
                    "text": item["text"],
                    "cluster": int(main_cluster),
                    "subcluster": int(sub_labels[idx]),
                    "date": item["date"]
                })

                filtered_embeddings.append(item["embedding"])

        print("After noise removal:", len(clustered_chunks))

        # ---------------------------------------------------
        # VECTOR DATABASE
        # ---------------------------------------------------

        dimension = len(filtered_embeddings[0])

        self.vector_store = VectorStore(dimension)

        self.vector_store.add(
            filtered_embeddings,
            clustered_chunks
        )

        self.clustered_chunks = clustered_chunks

        print(
            "Vector DB built with",
            len(clustered_chunks),
            "clean chunks"
        )

    # ---------------------------------------------------
    # QUERY SYSTEM
    # ---------------------------------------------------

    def query(self, question):

        query_embedding = self.embedding_service.embed([question])[0]

        # ---------------------------------------------------
        # GLOBAL SEARCH
        # ---------------------------------------------------

        initial_results = self.vector_store.search(
            query_embedding,
            k=10
        )

        clusters = [r["cluster"] for r in initial_results]

        top_clusters = [
            c[0]
            for c in Counter(clusters).most_common(2)
        ]

        print("\n🎯 Top Narrative Clusters:\n")

        for cid in top_clusters:

            label = self.cluster_labels.get(cid, "Unknown")

            print(f"Cluster {cid}: {label}")

        # ---------------------------------------------------
        # CLUSTER-LEVEL SEARCH
        # ---------------------------------------------------

        all_results = []

        for cluster_id in top_clusters:

            cluster_results = self.vector_store.search_in_cluster(
                query_embedding,
                cluster_id,
                k=4
            )

            all_results.extend(cluster_results)

        # ---------------------------------------------------
        # GLOBAL RERANK
        # ---------------------------------------------------

        all_results = sorted(
            all_results,
            key=lambda x: x["score"],
            reverse=True
        )

        results = all_results[:5]

        # ---------------------------------------------------
        # DISPLAY
        # ---------------------------------------------------

        print("\n🔍 Retrieved Context:\n")

        for r in results:

            label = self.cluster_labels.get(r["cluster"], "Unknown")

            print(
                f"Cluster: {r['cluster']} ({label}) | "
                f"Subcluster: {r.get('subcluster', 0)} | "
                f"Score: {r['score']:.4f}"
            )

            print(r["text"]["text"][:200])

            print("-" * 50)

        # ---------------------------------------------------
        # CONTEXT BUILDING
        # ---------------------------------------------------

        context = "\n\n".join([
            r["text"]["text"] 
            for r in results
        ])

        # ---------------------------------------------------
        # GENERATE RESPONSE
        # ---------------------------------------------------

        answer = self.rag.generate(
            context,
            question
        )

        return answer

    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------

    def run(self):

        print("Loading processed data...")

        with open(
            "data_lake/processed/enriched_articles.json",
            "r",
            encoding="utf-8"
        ) as f:

            articles = json.load(f)

        self.build_vector_db(articles)

        timeline_engine = TimelineEngine()
        timeline_engine.build(
            self.clustered_chunks,
            self.cluster_labels
        )
        timeline_engine.display()

        print("Ready for queries!\n")

        while True:

            q = input("Ask a question (or 'exit'): ")

            if q.lower() == "exit":
                break

            response = self.query(q)

            print("\n🧠 Intelligence Report:\n")

            print(response)

            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":

    pipeline = AIPipeline()

    pipeline.run()