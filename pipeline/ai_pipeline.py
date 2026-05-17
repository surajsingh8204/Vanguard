import json
from collections import Counter

from embeddings.embedding_services import EmbeddingService
from vectorstore.faiss_store import VectorStore
from intelligence.rag_engine import RAGEngine
from processing.hdbscan_cluster import HDBSCANClusterer


class AIPipeline:

    def __init__(self):

        print("Loading embedding model...")
        self.embedding_service = EmbeddingService()

        print("Initializing RAG engine...")
        self.rag = RAGEngine()

        self.vector_store = None

    # 🔥 Chunking function
    def chunk_text(self, text, chunk_size=300):

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    # 🔥 Build vector DB with HDBSCAN
    def build_vector_db(self, articles):

        print("Building vector database...")

        all_chunks = []

        for article in articles:
            chunks = self.chunk_text(article["content"])
            all_chunks.extend(chunks)

        print("Total chunks:", len(all_chunks))

        # Embeddings
        embeddings = self.embedding_service.embed(all_chunks)

        # 🔥 HDBSCAN clustering
        clusterer = HDBSCANClusterer(min_cluster_size=8)
        labels = clusterer.cluster(embeddings)

        clustered_chunks = []
        filtered_embeddings = []

        for i, label in enumerate(labels):

            if label == -1:
                continue  # remove noise

            clustered_chunks.append({
                "text": all_chunks[i],
                "cluster": int(label)
            })

            filtered_embeddings.append(embeddings[i])

        print("After noise removal:", len(clustered_chunks))

        dimension = len(filtered_embeddings[0])

        self.vector_store = VectorStore(dimension)

        # 🔥 store full objects (text + cluster)
        self.vector_store.add(filtered_embeddings, clustered_chunks)

        print("Vector DB built with", len(clustered_chunks), "clean chunks")

    # 🔥 Query with cluster-aware retrieval
    def query(self, question):

        query_embedding = self.embedding_service.embed([question])[0]

        # Step 1: global search → detect cluster
        initial_results = self.vector_store.search(query_embedding, k=8)

        clusters = [r["cluster"] for r in initial_results]
        dominant_cluster = Counter(clusters).most_common(1)[0][0]

        print("\n🎯 Dominant Cluster:", dominant_cluster)

        # Step 2: search INSIDE cluster
        results = self.vector_store.search_in_cluster(
            query_embedding,
            dominant_cluster,
            k=5
        )

        print("\n🔍 Retrieved Context:\n")

        for r in results:
            print(f"Score: {r['score']:.4f}")
            print(r["text"][:200])
            print("-" * 50)

        context = "\n\n".join([r["text"] for r in results])

        answer = self.rag.generate(context, question)

        return answer

    def run(self):

        print("Loading processed data...")

        with open("data_lake/processed/enriched_articles.json", "r") as f:
            articles = json.load(f)

        self.build_vector_db(articles)

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