import hdbscan
import numpy as np

from config.settings import MIN_CLUSTER_SIZE, MIN_SAMPLES


class HDBSCANClusterer:

    def __init__(self, min_cluster_size=MIN_CLUSTER_SIZE, min_samples=MIN_SAMPLES):

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