import hdbscan
import numpy as np


class HDBSCANClusterer:

    def __init__(self, min_cluster_size=5, min_samples=2):

        print("Initializing HDBSCAN...")

        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean'  # cosine already handled via normalized embeddings
        )

    def cluster(self, embeddings):

        embeddings = np.array(embeddings)

        print("Running HDBSCAN clustering...")

        labels = self.clusterer.fit_predict(embeddings)

        return labels