import json
import os

import faiss
import numpy as np

from config.settings import GLOBAL_RETRIEVAL_K, TOP_CLUSTERS


def normalize(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


class VectorStore:

    def __init__(self, dimension):
        self.index = faiss.IndexFlatIP(dimension)

        self.texts = []
        self.embeddings = []

        # 🔥 cluster → indices
        self.cluster_map = {}

    def add(self, embeddings, texts):

        embeddings = np.array(embeddings).astype("float32")
        embeddings = normalize(embeddings)

        self.index.add(embeddings)

        start_idx = len(self.texts)

        self.texts.extend(texts)
        self.embeddings.extend(embeddings)

        # 🔥 build cluster map
        for i, item in enumerate(texts):

            idx = start_idx + i
            cluster = item["cluster"]

            if cluster not in self.cluster_map:
                self.cluster_map[cluster] = []

            self.cluster_map[cluster].append(idx)

    def save(

        self,

        directory

    ):

        os.makedirs(
            directory,
            exist_ok=True
        )

        # save faiss index

        faiss.write_index(

            self.index,

            os.path.join(
                directory,
                "faiss.index"
            )

        )

        # save metadata

        metadata = {

            "texts":
                self.texts,

            "cluster_map":
                self.cluster_map,

            "embeddings":
                np.array(
                    self.embeddings
                ).tolist()
        }

        with open(

            os.path.join(
                directory,
                "metadata.json"
            ),

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                metadata,

                f,

                indent=4,

                ensure_ascii=False

            )

        print(
            "✅ Vector store saved."
        )

    @classmethod
    def load(

        cls,

        directory

    ):

        index = faiss.read_index(

            os.path.join(
                directory,
                "faiss.index"
            )

        )

        with open(

            os.path.join(
                directory,
                "metadata.json"
            ),

            "r",

            encoding="utf-8"

        ) as f:

            metadata = json.load(f)

        dimension = index.d

        store = cls(
            dimension
        )

        store.index = index

        store.texts = metadata[
            "texts"
        ]

        store.embeddings = np.array(

            metadata[
                "embeddings"
            ],

            dtype="float32"

        )

        store.cluster_map = {

            int(k): v

            for k, v in
            metadata[
                "cluster_map"
            ].items()
        }

        print(
            "✅ Vector store loaded."
        )

        return store

    def search(self, query_embedding, k=GLOBAL_RETRIEVAL_K):

        query_embedding = np.array([query_embedding]).astype("float32")
        query_embedding = normalize(query_embedding)

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for i, idx in enumerate(indices[0]):

            item = self.texts[idx]

            results.append({
                "text": item["text"],
                "cluster": item["cluster"],
                "subcluster": item.get("subcluster", 0),
                "score": float(distances[0][i])
                

            })

        return results

    # 🔥 TRUE cluster search
    def search_in_cluster(self, query_embedding, cluster_id, k=GLOBAL_RETRIEVAL_K // TOP_CLUSTERS):

        query_embedding = np.array([query_embedding]).astype("float32")
        query_embedding = normalize(query_embedding)

        indices = self.cluster_map.get(cluster_id, [])

        if not indices:
            return []

        cluster_vectors = np.array([self.embeddings[i] for i in indices])

        scores = np.dot(cluster_vectors, query_embedding.T).reshape(-1)

        top_k_idx = np.argsort(scores)[-k:][::-1]

        results = []

        for i in top_k_idx:

            idx = indices[i]
            item = self.texts[idx]

            results.append({
                "text": item["text"],
                "cluster": item["cluster"],
                "subcluster": item.get("subcluster", 0),
                "score": float(scores[i])
                

            })

        return results
