import hdbscan
import numpy as np

from core.config.settings import MIN_SAMPLES, MIN_SUBCLUSTER_SIZE


class SubClusterer:

    def __init__(self, min_cluster_size=MIN_SUBCLUSTER_SIZE, min_samples=MIN_SAMPLES):

        self.model = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean'
        )

    def cluster(self, embeddings):

        embeddings = np.array(embeddings)

        labels = self.model.fit_predict(embeddings)

        return labels